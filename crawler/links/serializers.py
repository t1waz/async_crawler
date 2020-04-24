import validators

from links.managers import LinkManager, LinkDataManager
from serializer import Serializer
from serializer.fields import ForeignKeyField


class LinkSerializer(Serializer):
    class Meta:
        managwer = LinkManager
        fields = ('id', 'url', 'interval', 'chuj')

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

    async def get_chuj(self, instance):
        return 'chuj'


class LinkDataSerializer(Serializer):
    link = ForeignKeyField(slug_field='url',
                           queryset=LinkDataManager.all,
                           many=False)

    class Meta:
        model = LinkDataManager
        fields = ('id', 'link', 'created')
        read_only_fields = ('created',)
