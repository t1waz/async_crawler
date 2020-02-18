from utils.common import View
from links.managers import LinkManager
from links.serializers import (
    LinkCreateSerializer,
    LinkStatusSerializer,
)


class AddLinkView(View):
    manager = LinkManager
    serializer = LinkCreateSerializer

    async def post(self, request):
        response = await super().post(request)

        if self.response_data['status_code'] == 201:
            await request.app.state.queue.put(self.instance)

        return response


class GetLinkView(View):
    manager = LinkManager
    serializer = LinkStatusSerializer
