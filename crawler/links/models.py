from tortoise import fields
from tortoise.models import Model


class Link(Model):
    id = fields.UUIDField(pk=True)
    url = fields.TextField(max_length=400)
    interval = fields.IntField(default=60)

    def __str__(self):
        return f'id: {self.id} url:{self.url}'


class LinkData(Model):
    id = fields.IntField(pk=True)
    link = fields.ForeignKeyField('models.Link', related_name='datas')
    created = fields.DatetimeField(auto_now_add=True)
    data = fields.BinaryField(null=True)
    status_code = fields.IntField(null=True)

    def __str__(self):
        return f'data for link: {self.link.url} created: {self.created}'
