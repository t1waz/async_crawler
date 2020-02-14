from utils.common import View
from links.tasks import get_link_data
from links.serializers import LinkCreateSerializer
from starlette.responses import JSONResponse
from starlette.background import BackgroundTask
from links.managers import (
    LinkDataManager,
    LinkManager,
)


class AddLinkView(View):
    async def post(self, request):
        data = await self.get_request_data(request)
        if not data:
            self.response_data['content'] = 'invalid request'
            self.response_data['status_code'] = 400

            return JSONResponse(**self.response_data)

        link = LinkCreateSerializer(data=data)
        is_valid, errors = await link.is_valid()
        if not is_valid:
            self.response_data['content'] = errors or 'incorrect data'
            self.response_data['status_code'] = 400

            return JSONResponse(**self.response_data)

        link = await link.save()
        if not link:
            self.response_data['content'] = 'internal error'
            self.response_data['status_code'] = 500

            return JSONResponse(**self.response_data)

        task = BackgroundTask(get_link_data,
                              link=link)

        self.response_data['content'] = LinkCreateSerializer.to_dict(link)
        self.response_data['status_code'] = 201

        return JSONResponse(**self.response_data, background=task)


class GetLinkView(View):
    async def post(self, request):
        data = await self.get_request_data(request)
        if not data:
            self.response_data['content'] = 'invalid request'
            self.response_data['status_code'] = 400

            return JSONResponse(**self.response_data)

        if set(data.keys()).difference({'id'}):
            self.response_data['content'] = 'incorrect data'
            self.response_data['status_code'] = 400

            return JSONResponse(**self.response_data)

        link = await LinkManager.get_list(id=data['id'])
        if not link:
            self.response_data['content'] = 'incorrect id'
            self.response_data['status_code'] = 400

            return JSONResponse(**self.response_data)

        link_data = await LinkDataManager.get_list(link=data['id'])
        if not link_data:
            self.response_data['content'] = 'task pending'
        else:
            if not link_data[0].data:
                self.response_data['content'] = 'app cannot get data'
            else:
                self.response_data['content'] = link_data[0].data

        return JSONResponse(**self.response_data)
