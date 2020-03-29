from links.managers import LinkManager
from links.serializers import LinkSerializer
from utils.views import View


class LinkView(View):
    manager = LinkManager
    serializer_class = LinkSerializer
