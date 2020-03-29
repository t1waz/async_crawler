from links.models import (
    Link,
    LinkData
)
from utils.managers import Manager


class LinkManager(Manager):
    model = Link


class LinkDataManager(Manager):
    model = LinkData
