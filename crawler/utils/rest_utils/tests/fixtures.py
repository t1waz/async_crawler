from serializer import Serializer
from serializer.fields import ForeignKeyField
from tortoise import fields
from tortoise.models import Model
from manager import Manager


class SampleModel(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField(max_length=400)


class SampleModelManager(Manager):
    model = SampleModel


class SampleModelChild(Model):
    id = fields.UUIDField(pk=True)
    name = fields.TextField(max_length=400)
    number = fields.IntField()
    created = fields.DatetimeField(auto_now_add=True)
    data = fields.BinaryField()
    sample_model = fields.ForeignKeyField('tests.SampleModel', related_name='childs')


class SampleModelChildManager(Manager):
    model = SampleModelChild


class IncorrectModel:
    pass


class IncorrectModelManager(Manager):
    model = IncorrectModel


class CorrectSerializerOne(Serializer):
    class Meta:
        manager = SampleModelManager
        fields = ('id',)


class CorrectSerializerTwo(Serializer):
    sample_model = ForeignKeyField(many=False,
                                   queryset=SampleModelManager.all(),
                                   slug_field='name')

    class Meta:
        manager = SampleModelChildManager
        fields = ('id', 'name', 'number', 'created', 'data', 'sample_model', 'ser_test')
        read_only_fields = ('created',)

    async def get_ser_test(self, instance):
        return 'ser_test'


class CorrectSerializerThree(Serializer):
    sample_model = ForeignKeyField(many=False,
                                   queryset=SampleModelManager.all(),
                                   slug_field='name')

    class Meta:
        manager = SampleModelChildManager
        fields = ('id', 'sample_model')
