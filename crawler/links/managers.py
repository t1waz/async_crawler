from utils.common import Manager
from links.models import (
    Link,
    LinkData
)


class LinkManager(Manager):
    class Meta:
        model = Link


class LinkDataManager(Manager):
    class Meta:
        model = LinkData
