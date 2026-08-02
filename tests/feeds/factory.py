from polyfactory import Ignore
from polyfactory.factories.pydantic_factory import ModelFactory

from trakt_backend.feeds import Feed


class FeedFactory(ModelFactory[Feed]):
    __model__ = Feed

    id = Ignore()
