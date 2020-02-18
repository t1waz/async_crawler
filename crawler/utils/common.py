import asyncio
from exceptions import ValidationError
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse


class Serializer:
    def __new__(cls, *args, **kwargs):
        meta = getattr(cls, 'Meta', None)
        assert meta, f'{cls.__name__} missing meta'

        if not hasattr(cls, '_fields'):
            assert hasattr(meta, 'model'), f'{cls.__name__} missing model'
            assert hasattr(meta, 'manager'), f'{cls.__name__} missing manager'

            cls._cls_name = cls.__name__

            cls._fields = meta.model._meta.db_fields
            cls._model_pk_field = meta.model._meta.pk.model_field_name
            cls._model = meta.model
            cls._manager = meta.manager

            cls._list_fields = getattr(meta, 'list_fields', None) or cls._fields
            cls._create_fields = getattr(meta, 'create_fields', None) or cls._fields
            cls._update_fields = getattr(meta, 'update_fields', None) or cls._fields
            cls._instance_fields = getattr(meta, 'instance_fields', None) or cls._fields
            cls._create_optional_fields = getattr(meta, 'create_optional_fields', set())
            cls._validators = [getattr(cls, validator) for validator in cls.__dict__ if
                               validator.startswith('validate')]
            cls._serializer_methods = [getattr(cls, method) for method in cls.__dict__ if
                                       method.startswith('get')]

        return super(Serializer, cls).__new__(cls)

    def __init__(self, data=None, instance=None):
        if instance:
            assert isinstance(instance, self._model), f'{self._cls_name} incorrect instance'

        self._input_data = data
        self._instance = instance
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

        tasks = [validator(self, data=self._input_data) for validator in self._validators if 
                 validator.__name__.split('validate_')[1] in self._input_data.keys()]

        return await asyncio.gather(*tasks)

    async def save(self, to_dict=False):
        if self._valid is None:
            raise ValidationError('run is_valid first')

        if not self._valid:
            raise ValidationError('cannot save, data not valid')

        try:
            self._instance = await self._manager.create(**self._input_data)
        except BaseException:
            self._instance = None

        if to_dict:
            return self.to_dict()

        return self._instance

    async def set_serialized_fields(self):
        methods = [method for method in self._serializer_methods if 
                   method.__name__.split('get_')[1] in self._instance_fields]

        tasks = [method(self, instance=self._instance) for method in methods]
        attributes = await asyncio.gather(*tasks)

        for attribute, value in zip(methods, attributes):
            setattr(self._instance, attribute.__name__.split('_')[1], value)

    async def to_dict(self, serialized_fields=True):
        if serialized_fields:
            await self.set_serialized_fields()

        return {attr: str(getattr(self._instance, attr)) for attr in self._instance_fields}


class Manager:
    def __new__(cls, *args, **kwargs):
        meta = getattr(cls, 'Meta', None)
        assert meta, f'{cls.__name__} missing meta'

        if not hasattr(cls, '_model'):
            assert hasattr(meta, 'model'), f'{cls.__name__} missing model'
            cls._model = getattr(meta, 'model')

        return super(Manager, cls).__new__(cls)

    @classmethod
    async def get_all(cls):
        return await cls()._model.all()

    @classmethod
    async def get_instance(cls, **kwargs):
        return await cls()._model.get(**kwargs)

    @classmethod
    async def get_list(cls, **kwargs):
        try:
            return await cls()._model.filter(**kwargs)
        except BaseException:
            return None

    @classmethod
    async def filter_count(cls, **kwargs):
        return await cls()._model.filter(**kwargs).count()

    @classmethod
    async def create(cls, **kwargs):
        return await cls()._model.create(**kwargs)

    @classmethod
    async def bulk_create(cls, instances):
        await cls()._model.bulk_create(instances)

    @classmethod
    async def instance(cls, **kwargs):
        return await cls()._model(**kwargs)


class View(HTTPEndpoint):
    def __new__(cls, *args, **kwargs):
        assert hasattr(cls, 'manager'), f'{cls.__name__} missing manager'
        assert hasattr(cls, 'serializer'), f'{cls.__name__} missing serializer'

        if not hasattr(cls, '_manager'):
            cls._manager = getattr(cls, 'manager')
            cls._serializer = getattr(cls, 'serializer')

        return super(View, cls).__new__(cls)

    def __init__(self, *args, **kwargs):
        self.instance = None
        self.response_data = {
            'content': {},
            'status_code': 200
        }
        super().__init__(*args, **kwargs)

    async def get_request_data(self, request):
        try:
            data = await request.json()
        except BaseException:
            data = None

        return data

    async def post(self, request):
        data = await self.get_request_data(request)
        if not data:
            self.response_data['content'] = 'invalid request'
            self.response_data['status_code'] = 400

            return JSONResponse(**self.response_data)

        serializer = self._serializer(data=data)
        is_valid, errors = await serializer.is_valid()
        if not is_valid:
            self.response_data['content'] = errors or 'incorrect data'
            self.response_data['status_code'] = 400

            return JSONResponse(**self.response_data)

        self.instance = await serializer.save()
        if not self.instance:
            self.response_data['content'] = 'internal error'
            self.response_data['status_code'] = 500

            return JSONResponse(**self.response_data)

        self.response_data['content'] = await serializer.to_dict(self.instance)
        self.response_data['status_code'] = 201

        return JSONResponse(**self.response_data)

    async def get(self, request):
        params_id = request.path_params.get('id')
        if params_id:
            queryset = await self._manager.get_list(id=params_id)
            if not queryset:
                self.response_data['content'] = 'incorrect id'
                self.response_data['status_code'] = 400

                return JSONResponse(**self.response_data)
        else:
            queryset = await self._manager.get_all()

        tasks = [self._serializer(instance=instance).to_dict() for instance in queryset]

        return JSONResponse(await asyncio.gather(*tasks))
