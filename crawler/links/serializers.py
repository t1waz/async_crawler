import validators

from tortoise_rest_utils.serializer import Serializer
from tortoise_rest_utils.serializer.fields import ForeignKeyField
from links.models import (
    Link,
    LinkData,
)


class LinkSerializer(Serializer):
    class Meta:
        model = Link
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
                           queryset=lambda: Link.all(),
                           many=False)

    class Meta:
        model = LinkData
        fields = ('id', 'link', 'created')
        read_only_fields = ('created',)
