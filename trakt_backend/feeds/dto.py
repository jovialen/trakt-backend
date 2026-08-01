from typing import Self

from pydantic import BaseModel

from .model import Feed, FeedBase


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

    @classmethod
    def from_feed(cls, feed: Feed | type[Feed]) -> Self:
        return cls(
            **feed.model_dump(),
            groups=[group.id for group in feed.groups],
        )
