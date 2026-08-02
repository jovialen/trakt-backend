from polyfactory import Ignore
from polyfactory.factories.pydantic_factory import ModelFactory

from trakt_backend.groups import FeedGroup


class FeedGroupFactory(ModelFactory[FeedGroup]):
    __model__ = FeedGroup

    id = Ignore()
