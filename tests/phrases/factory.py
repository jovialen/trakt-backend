from polyfactory import Ignore
from polyfactory.factories.pydantic_factory import ModelFactory

from trakt_backend.phrases import HighlightedPhrase


class HighlightedPhraseFactory(ModelFactory[HighlightedPhrase]):
    __model__ = HighlightedPhrase

    id = Ignore()
