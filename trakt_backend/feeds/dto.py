from pydantic import BaseModel

from .model import FeedBase


class FeedDtoBase(FeedBase):
    groups: list[int]


class FeedCreate(FeedDtoBase):
    pass


class FeedUpdate(FeedDtoBase):
    pass


class FeedPatch(BaseModel):
    name: str | None = None
    link: str | None = None
    groups: list[int] | None = None


class FeedRead(FeedDtoBase):
    id: int
