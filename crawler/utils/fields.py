import asyncio

class SerializerField:
    pass


class ForeignKeyField(SerializerField):
    def __init__(self, slug_field=None, queryset=None, many=False):
        self._slug_field = slug_field
        self._queryset = queryset
        self._many = many

    @classmethod
    async def get_object(cls, data):
        print(cls._queryset)
