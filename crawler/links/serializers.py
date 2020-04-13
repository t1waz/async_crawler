import validators

from links.managers import LinkManager, LinkDataManager
from utils.serializers import Serializer
from utils.fields import ForeignKeyField


class LinkSerializer(Serializer):
    class Meta:
        manager = LinkManager
        fields = ('id', 'url', 'interval')

    async def validate_url(self, data):
        if not validators.url(data.get('url')) is True:
            return False, 'invalid url'

        return True, ''

    async def validate_interval(self, data):
        interval = data.get('interval')

        if not isinstance(interval, int):
            return False, 'interval is not a integer'

        if interval < 1:
            return False, 'interval lower that 1'

        return True, ''


class LinkDataSerializer(Serializer):
    link = ForeignKeyField(slug_field='url', queryset=LinkManager.all, many=False)

    class Meta:
        manager = LinkDataManager
        fields = ('id', 'link', 'created')
        read_only_fields = ('created',)
