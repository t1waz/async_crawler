from links.models import (
    Link,
    LinkData
)
from manager import Manager


class LinkManager(Manager):
    model = Link


class LinkDataManager(Manager):
    model = LinkData
