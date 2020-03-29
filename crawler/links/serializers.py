import validators

from links.models import Link
from utils.serializers import Serializer


class LinkSerializer(Serializer):
    class Meta:
        model = Link
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
