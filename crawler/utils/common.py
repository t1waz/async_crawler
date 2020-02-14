import asyncio
from starlette.endpoints import HTTPEndpoint
from exceptions import ValidationError


class Serializer:
    def __new__(cls, *args, **kwargs):
        meta = getattr(cls, 'Meta', None)
        assert meta, f'{cls.__name__} missing meta'

        if not hasattr(cls, '_fields'):
            assert hasattr(meta, 'model'), f'{cls.__name__} missing model'
            assert hasattr(meta, 'manager'), f'{cls.__name__} missing manager'

            cls._fields = meta.model._meta.db_fields
            cls._model_pk_field = meta.model._meta.pk.model_field_name
            cls._model = getattr(meta, 'model')
            cls._manager = getattr(meta, 'manager')

            cls._list_fields = getattr(meta, 'list_fields', None) or cls._fields
            cls._create_fields = getattr(meta, 'create_fields', None) or cls._fields
            cls._update_fields = getattr(meta, 'update_fields', None) or cls._fields
            cls._instance_fields = getattr(meta, 'instance_fields', None) or cls._fields
            cls._create_optional_fields = getattr(meta, 'create_optional_fields', set())
            cls._validators = [getattr(cls, validator) for validator in cls.__dict__ if
                               validator.startswith('validate')]

        return super(Serializer, cls).__new__(cls)

    def __init__(self, data):
        self._input_data = data
        self._valid, self._errors = None, None

    async def is_valid(self):
        validation_data = await self.run_validators()
        validation_outputs, errors = zip(*validation_data)

        self._errors = list(filter(None, errors))
        self._valid = all(validation_outputs)

        return self._valid, self._errors

    def check_input_data(self):
        data_keys_diff = set(self._create_fields).difference(set(self._input_data.keys()))
        data_keys_diff.discard(self._model_pk_field)
        data_keys_diff = data_keys_diff.difference(set(self._create_optional_fields))

        return not bool(data_keys_diff)

    async def run_validators(self):
        if not self.check_input_data():
            return [(False, 'incorrect input data')]

        tasks = [validator(data=self._input_data) for validator in self._validators if 
                 validator.__name__.split('validate_')[1] in self._input_data.keys()]

        return await asyncio.gather(*tasks)

    async def save(self, to_dict=False):
        if self._valid is None:
            raise ValidationError('run is_valid first')

        if not self._valid:
            raise ValidationError('cannot save, data not valid')

        try:
            instance = await self._manager.create(**self._input_data)
        except:
            instance = None

        if to_dict:
            instance = self.to_dict(instance)

        return instance

    @classmethod
    def to_dict(cls, instance):
        if isinstance(instance, cls._model):
            return {
                attr: str(getattr(instance, attr)) for attr in cls._instance_fields
            }


class Manager:
    def __new__(cls, *args, **kwargs):
        meta = getattr(cls, 'Meta', None)
        assert meta, f'{cls.__name__} missing meta'

        if not hasattr(cls, '_model'):
            assert hasattr(meta, 'model'), f'{cls.__name__} missing model'
            cls._model = getattr(meta, 'model')

        return super(Manager, cls).__new__(cls)

    @classmethod
    async def get_list(cls, **kwargs):
        try:
            return await cls()._model.filter(**kwargs)
        except:
            return None

    @classmethod
    async def create(cls, **kwargs):
        return await cls()._model.create(**kwargs)


class View(HTTPEndpoint):
    def __init__(self, *args, **kwargs):
        self.response_data = {
            'content': {},
            'status_code': 200
        }
        super().__init__(*args, **kwargs)

    async def get_request_data(self, request):
        try:
            data = await request.json()
        except:
            data = None

        return data
