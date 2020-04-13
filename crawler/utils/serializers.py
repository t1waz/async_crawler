import asyncio
import copy
from collections.abc import Iterable

from tortoise import exceptions
from tortoise.models import Model

from utils.exceptions import ValidationError
from utils.fields import SerializerField, ForeignKeyField


class SerializerMeta(type):
    @staticmethod
    def get_variable_from_method_name(method_name='', splitter='', end_rstrip=''):
        return next(iter(method_name.split(splitter)[1:2]), '').rstrip(end_rstrip)

    def validate_meta(cls, meta, instance, attrs):
        assert meta is not None, f'{instance.__name__} missing Meta'
        assert hasattr(meta, 'manager'), f'{instance.__name__} Meta missing model'
        assert hasattr(meta, 'fields'), f'{instance.__name__} Meta missing fields'
        assert isinstance(meta.fields, Iterable), f'{instance.__name__} fields must be iterable'
        assert issubclass(meta.manager.model, Model), \
            f'{instance.__name__} Meta model not TortToise model instance'

        serialized_fields = [cls.get_variable_from_method_name(attr, 'get_', '_') for attr in
                             dir(instance) if cls.get_variable_from_method_name(attr, 'get_', '_')
                             and callable(attr)]
        allowed_fields = list(meta.manager.model._meta.fields) + serialized_fields
        assert all(attr in allowed_fields for attr in meta.fields), \
            f'incorrect Meta field declaration - some fields ' \
            f'does not belong to model or serialized fields'

        read_only_fields = getattr(meta, 'read_only_fields', None)
        if read_only_fields:
            assert all(attr in allowed_fields for attr in read_only_fields), \
                f'incorrect Meta read_only_field declaration - some fields ' \
                f'does not belong to model or serialized fields'

        model_fk_fields = meta.manager.model._meta.fk_fields
        if model_fk_fields:
            serializer_fk_fields = (name for name, field in attrs.items() if
                                    isinstance(field, ForeignKeyField))
            assert serializer_fk_fields, f'{instance.__name__} missing  foreign keys mapping'

    def __new__(cls, name, bases, attrs, **kwargs):
        instance = super().__new__(cls, name, bases, attrs, **kwargs)
        if not bases:
            return instance

        meta = attrs.get('Meta')
        cls.validate_meta(cls, meta, instance, attrs)

        instance.manager = meta.manager
        instance.model_pk_field_name = instance.manager.model._meta.pk_attr

        instance.validators = {cls.get_variable_from_method_name(name, 'validate_', '_'): attr
                               for name, attr in attrs.items() if
                               name.startswith('validate') and callable(attr)}
        instance.serializer_methods = {cls.get_variable_from_method_name(name, 'get_', '_'): attr
                                       for name, attr in attrs.items() if
                                       cls.get_variable_from_method_name(name, 'get_', '_')
                                       and callable(attr)}

        instance.fk_fields = {name: field for name, field in attrs.items() if
                              issubclass(field.__class__, SerializerField)}
        instance.fields = tuple(list(meta.manager.model._meta.fields) +
                                list(instance.serializer_methods.keys()))
        instance.read_only_fields = getattr(meta, 'read_only_fields', ())

        return instance


class Serializer(metaclass=SerializerMeta):
    def __init__(self, instance=None, data=None):
        if instance and not issubclass(instance.__class__, self.manager.model):
            raise ValidationError(f'{self.__class__.__name__} instance not serializer model class')

        self._data = data
        self._errors = []
        self._instance = instance
        self._validated_data = None

    def _check_data(self):
        input_read_only_fields = [f for f in self._data.keys() if f in self.read_only_fields]
        if any(input_read_only_fields):
            return False, [f'field {f} is read only' for f in input_read_only_fields]

        if self.model_pk_field_name in self._data.keys():
            return False, ['primary key in input']

        data_keys_diff = set(self._data.keys()).difference(self.fields)
        data_keys_diff.discard(self.model_pk_field_name)

        return not bool(data_keys_diff), [f'field {f} missing in input' for f in data_keys_diff]

    async def _run_validators(self):
        tasks = [validator(self, data=self._data) for name, validator in self.validators.items()
                 if name in self._data.keys()]

        return await asyncio.gather(*tasks)

    async def is_valid(self):
        if not self._data:
            raise ValidationError('initial data not provided, cannot call is_valid()')

        data_valid, errors = self._check_data()
        self._errors = errors
        if not data_valid:
            return False

        validation_outputs, errors = zip(*await self._run_validators())
        self._errors += list(filter(None, errors))
        valid = all(validation_outputs)
        if valid:
            self._validated_data = copy.deepcopy(self._data)

        return valid

    async def _set_serialized_fields(self):
        attribute_names, methods = self.serializer_methods.keys(), self.serializer_methods.values()
        tasks = [method(self, self._instance) for method in methods]
        attributes = await asyncio.gather(*tasks)
        for name, value in zip(attribute_names, attributes):
            setattr(self._instance, name, value)

    async def to_dict(self):
        if self._data and not self.validated_data:
            raise ValidationError('first call is_valid')

        await self._set_serialized_fields()

        return {attr: str(getattr(self._instance, attr)) for attr in self.fields}

    async def save(self, to_dict=False):
        if self._errors:
            raise ValueError('cannot save, data not valid')
        elif self._data and self._validated_data is None:
            raise ValueError('run is_valid first')

        try:
            self._instance = await self.manager.create(**self._validated_data)
        except exceptions.IntegrityError:
            self._errors.append('cannot save instance')

        if to_dict:
            return self.to_dict()

        return self._instance

    async def update(self):
        if self._errors:
            raise ValueError('cannot update, data not valid')
        elif self._validated_data is None:
            raise ValueError('run is_valid first')

        for attr, value in self._validated_data.items():
            setattr(self._instance, attr, value)

        status = True
        try:
            await self._instance.save()
        except exceptions.IntegrityError:
            self._errors = 'cannot update instance, internal error'
            status = False

        return status

    @property
    def validated_data(self):
        return self._validated_data

    @property
    def errors(self):
        return self._errors
