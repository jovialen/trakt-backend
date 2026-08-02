from datetime import datetime
from random import random

from polyfactory import Ignore, Use
from polyfactory.factories.pydantic_factory import ModelFactory

from trakt_backend.items import FeedItem


class FeedItemFactory(ModelFactory[FeedItem]):
    __model__ = FeedItem

    feed_id = Ignore()

    read_at = Use(lambda: datetime.now() if random() < 0.3 else None)

    read_later = Use(lambda: random() < 0.15)

    saved_at = Use(lambda: datetime.now() if random() < 0.2 else None)
