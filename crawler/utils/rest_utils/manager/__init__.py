class Manager:
    @classmethod
    def get_queryset(cls):
        return cls.model.all

    @classmethod
    def all(cls):
        return cls.get_queryset()

    @classmethod
    def get(cls, **kwargs):
        return cls.get_queryset().get(**kwargs)

    @classmethod
    def filter(cls, **kwargs):
        return cls.get_queryset().filter(**kwargs)

    @classmethod
    async def create(cls, **kwargs):
        instance = cls.model(**kwargs)
        await instance.save()

        return instance
