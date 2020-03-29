import asyncio

from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from tortoise import exceptions


class ViewMeta(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        instance = super().__new__(cls, name, bases, attrs, **kwargs)
        if not bases or HTTPEndpoint in bases:
            return instance

        assert 'manager' in attrs, f'{instance.__name__} missing manager in view'
        assert 'serializer_class' in attrs, f'{instance.__name__} missing serializer_class in view'

        instance.manager = attrs['manager']
        instance.serializer = attrs['serializer_class']

        return instance


class View(HTTPEndpoint, metaclass=ViewMeta):
    def __init__(self, *args, **kwargs):
        self.response_data = {
            'content': {},
            'status_code': 200
        }
        super().__init__(*args, **kwargs)

    @staticmethod
    async def get_request_data(request):
        try:
            return await request.json()
        except ValueError:
            return None

    async def get_instance_from_pk(self, pk):
        try:
            return await self.manager.get(**{self.serializer_class.model_pk_field_name: pk})
        except exceptions.DoesNotExist:
            return None

    async def post(self, request):
        data = await self.get_request_data(request)
        if not data:
            self.response_data['status_code'] = 400
            self.response_data['content'] = {'detail': 'invalid request for create'}

            return JSONResponse(**self.response_data)

        serializer = self.serializer_class(data=data)
        is_valid = await serializer.is_valid()

        if not is_valid:
            self.response_data['status_code'] = 400
            self.response_data['content'] = {'detail': serializer.errors or 'incorrect input data'}

            return JSONResponse(**self.response_data)

        if not await serializer.save():
            self.response_data['status_code'] = 500
            self.response_data['content'] = {'detail': 'cannot create, internal error'}

            return JSONResponse(**self.response_data)

        self.response_data['status_code'] = 201
        self.response_data['content'] = await serializer.to_dict()

        return JSONResponse(**self.response_data)

    async def get(self, request):
        pk = request.path_params.get('id')

        if not pk:
            instances = await self.manager.all()
            tasks = [self.serializer_class(instance=instance).to_dict() for instance in instances]
            self.response_data['content'] = await asyncio.gather(*tasks)

            return JSONResponse(**self.response_data)

        instance = await self.get_instance_from_pk(pk)

        if instance:
            self.response_data['content'] = await self.serializer_class(instance=instance).to_dict()
        else:
            self.response_data['status_code'] = 404
            self.response_data['content'] = {'detail': 'not found'}

        return JSONResponse(**self.response_data)

    async def delete(self, request):
        pk = request.path_params.get('id')
        if not pk:
            self.response_data['status_code'] = 405
            self.response_data['content'] = {'detail': 'Method DELETE not allowed.'}

            return JSONResponse(self.response_data)

        instance = await self.get_instance_from_pk(pk)
        if not instance:
            self.response_data['status_code'] = 404
            self.response_data['content'] = {'detail': 'objects does not exists'}
        else:
            await instance.delete()
            self.response_data['content'] = {'deleted': True}

        return JSONResponse(**self.response_data)

    async def patch(self, request):
        pk = request.path_params.get('id')
        if not pk:
            self.response_data['status_code'] = 405
            self.response_data['content'] = {'detail': 'Method PATCH not allowed.'}

            return JSONResponse(**self.response_data)

        data = await self.get_request_data(request)
        if not data:
            self.response_data['status_code'] = 400
            self.response_data['content'] = {'detail': 'invalid request for update'}

            return JSONResponse(**self.response_data)

        instance = await self.get_instance_from_pk(pk)
        if not instance:
            self.response_data['status_code'] = 404
            self.response_data['content'] = {'detail': 'objects does not exists'}

            return JSONResponse(**self.response_data)

        serializer = self.serializer_class(instance=instance, data=data)
        is_valid = await serializer.is_valid()
        if not is_valid:
            self.response_data['status_code'] = 404
            self.response_data['content'] = serializer.errors

            return JSONResponse(**self.response_data)

        is_updated = await serializer.update()
        if not is_updated:
            self.response_data['status_code'] = 404
            self.response_data['content'] = serializer.errors

            return JSONResponse(**self.response_data)

        self.response_data['content'] = await serializer.to_dict()

        return JSONResponse(**self.response_data)
