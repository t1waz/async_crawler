import asyncio
import copy
from collections.abc import Iterable

from tortoise import exceptions
from tortoise.models import Model

from utils.exceptions import ValidationError


class SerializerMeta(type):
    @staticmethod
    def get_variable_from_method_name(method_name='', splitter='', end_rstrip=''):
        return next(iter(method_name.split(splitter)[1:2]), '').rstrip(end_rstrip)

    def __new__(cls, name, bases, attrs, **kwargs):
        instance = super().__new__(cls, name, bases, attrs, **kwargs)
        if not bases:
            return instance

        _meta = attrs.get('Meta')
        assert _meta is not None, f'{instance.__name__} missing Meta'
        assert hasattr(_meta, 'model'), f'{instance.__name__} Meta missing model'
        assert hasattr(_meta, 'fields'), f'{instance.__name__} Meta missing fields'
        assert isinstance(_meta.fields, Iterable), f'{instance.__name__} fields must be iterable'
        assert issubclass(_meta.model, Model), f'{instance.__name__} Meta model not ' \
                                               f'TortToise model instance'

        instance.model = _meta.model
        instance.model_pk_field_name = instance.model._meta.pk_attr
        instance.fields = _meta.model._meta.fields
        instance.validators = {cls.get_variable_from_method_name(name, 'validate_', '_'): attr
                               for name, attr in attrs.items() if
                               name.startswith('validate') and callable(attr)}
        instance.serializer_methods = {cls.get_variable_from_method_name(name, 'get_', '_'): attr
                                       for name, attr in attrs.items() if
                                       cls.get_variable_from_method_name(name, 'get_', '_')
                                       and callable(attr)}
        instance.fields.update(set(instance.serializer_methods.keys()))

        assert all(attr in instance.fields for attr in _meta.fields), \
            f'incorrect Meta field declaration - some fields ' \
            f'does not belong to model or serialized fields'

        return instance


class Serializer(metaclass=SerializerMeta):
    def __init__(self, instance=None, data=None):
        if instance and not issubclass(instance.__class__, self.model):
            raise ValidationError(f'{self.__class__.__name__} instance not serializer model class')

        self._instance = instance
        self._data = data
        self._validated_data = None
        self._errors = None

    def check_input_data(self, data):
        if self.model_pk_field_name in data.keys():
            return False

        data_keys_diff = set(data.keys()).difference(self.fields)
        data_keys_diff.discard(self.model_pk_field_name)

        return not bool(data_keys_diff)

    async def run_validators(self):
        tasks = [validator(self, data=self._data) for name, validator in self.validators.items()
                 if name in self._data.keys()]

        return await asyncio.gather(*tasks)

    async def is_valid(self):
        if not self.check_input_data(self._data):
            self._errors = 'invalid input data'

            return False

        validation_outputs, errors = zip(*await self.run_validators())
        self._errors = list(filter(None, errors))
        valid = all(validation_outputs)
        if valid:
            self._validated_data = copy.deepcopy(self._data)

        return valid

    async def set_serialized_fields(self):
        attribute_names, methods = self.serializer_methods.keys(), self.serializer_methods.values()
        tasks = [method(self, self._instance) for method in methods]
        attributes = await asyncio.gather(*tasks)
        for name, value in zip(attribute_names, attributes):
            setattr(self._instance, name, value)

    async def to_dict(self):
        await self.set_serialized_fields()

        return {attr: str(getattr(self._instance, attr)) for attr in self.fields}

    async def save(self, to_dict=False):
        if self._errors:
            raise ValueError('cannot save, data not valid')
        elif self._validated_data is None:
            raise ValueError('run is_valid first')

        try:
            self._instance = await self.model.create(**self._validated_data)
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
        return self._validated_dat

    @property
    def errors(self):
        return self._errors