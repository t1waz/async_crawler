class Manager:
    @classmethod
    async def get_queryset(cls):
        return await cls.model.all()

    @classmethod
    async def all(cls):
        return await cls.get_queryset()

    @classmethod
    async def get(cls, **kwargs):
        return await cls.get_queryset().get(**kwargs)

    @classmethod
    async def filter(cls, **kwargs):
        return await cls.get_queryset().filter(**kwargs)
