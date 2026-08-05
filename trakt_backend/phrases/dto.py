from pydantic import BaseModel, Field

from .model import HEX_REGEX, HighlightedPhraseBase


class HighlightedPhraseCreate(HighlightedPhraseBase):
    pass


class HighlightedPhraseUpdate(HighlightedPhraseBase):
    pass


class HighlightedPhrasePatch(BaseModel):
    phrase: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = Field(default=None, pattern=HEX_REGEX)
