from typing import Self

from pydantic import BaseModel

from ..items import FeedItemService
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
    unread: int

    @classmethod
    def from_feed(cls, feed: Feed | type[Feed], items: FeedItemService) -> Self:
        return cls(
            **feed.model_dump(),
            groups=[group.id for group in feed.groups],
            unread=items.count_unread(feed.id),
        )
