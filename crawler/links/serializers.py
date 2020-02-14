import validators
from links.models import Link
from utils.common import Serializer
from links.managers import LinkManager


class LinkCreateSerializer(Serializer):
    class Meta:
        model = Link
        manager = LinkManager
        create_fields = ('url', 'interval')
        create_optional_fields = ('interval',)
        instance_fields = ('id',)

    async def validate_url(data):
        if not validators.url(data.get('url')) is True:
            return False, 'invalid url'

        return True, ''

    async def validate_interval(data):
        interval = data.get('interval')

        if not isinstance(interval, int):
            return False, 'interval is not a integer'

        if interval < 1:
            return False, 'interval lower that 1'

        return True, ''
