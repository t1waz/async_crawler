from links.managers import LinkManager, LinkDataManager
from links.serializers import LinkSerializer, LinkDataSerializer
from utils.views import View


class LinkView(View):
    manager = LinkManager
    serializer_class = LinkSerializer


class LinkDataView(View):
    manager = LinkDataManager
    serializer_class = LinkDataSerializer
