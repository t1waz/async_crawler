import datetime
import asyncio
from tests.fixtures import (
    SampleModel,
    SampleModelChild,
)
from tortoise import Tortoise


class DBHandler:
    def __enter__(self, *args, **kwargs):
        asyncio.get_event_loop().run_until_complete(self.open_db())

    def __exit__(self, *args, **kwargs):
        asyncio.get_event_loop().run_until_complete(self.close_db())

    @classmethod
    async def clear_models(cls):
        await SampleModel.all().delete()
        await SampleModelChild.all().delete()

    @classmethod
    async def init_models(cls):
        sample_model_1 = SampleModel(name='model_1')
        await sample_model_1.save()

        sample_model_2 = SampleModel(name='model_2')
        await sample_model_2.save()

        sample_model_3 = SampleModel(name='model_3')
        await sample_model_3.save()

        sample_model_child_1 = SampleModelChild(name='child_1',
                                                number=1,
                                                data=b'1',
                                                sample_model=sample_model_1,
                                                created=datetime.datetime.now())
        await sample_model_child_1.save()

        sample_model_child_2 = SampleModelChild(name='child_2',
                                                number=2,
                                                data=b'2',
                                                sample_model=sample_model_2,
                                                created=datetime.datetime.now())
        await sample_model_child_2.save()

        sample_model_child_3 = SampleModelChild(name='child_3',
                                                number=3,
                                                data=b'3',
                                                sample_model=sample_model_3,
                                                created=datetime.datetime.now())
        await sample_model_child_3.save()

    @classmethod
    async def open_db(cls):
        await Tortoise.init(db_url='sqlite://:memory1:',
                            modules={'tests': ['tests.fixtures']})
        await Tortoise.generate_schemas()

        await cls.clear_models()
        await cls.init_models()

    @classmethod
    async def close_db(cls):
        await Tortoise.close_connections()
