from links.models import Link, LinkData
from links.serializers import LinkSerializer, LinkDataSerializer
from tortoise_rest_utils.view import View


class LinkView(View):
    serializer_class = LinkSerializer

    def get_queryset(self):
        return Link.all()

class LinkDataView(View):
    serializer_class = LinkDataSerializer

    def get_queryset(self):
        return LinkData.all()
