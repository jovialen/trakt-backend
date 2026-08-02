from datetime import datetime
from time import struct_time
from typing import TYPE_CHECKING, Self

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from ..feeds import Feed


class RSS2Item(SQLModel):
    id: str = Field(default=None, primary_key=True)
    title: str
    link: str
    summary: str
    published_at: datetime
    updated_at: datetime
    authors: str
    categories: str
    content: str

    def import_from_parsed(self, entry: dict) -> Self:
        self.id = entry.get("id") or entry.get("guid") or entry.get("link", "")
        self.title = entry.get("title", "")
        self.link = entry.get("link", "")
        self.summary = entry.get("summary", "")

        self.published_at = self._parse_feed_time(entry.get("published_parsed", None))
        self.updated_at = self._parse_feed_time(entry.get("updated_parsed", None))

        self.authors = ", ".join(
            author.get("name", "") for author in entry.get("authors", []) if author.get("name")
        ) or entry.get("author", "")

        self.categories = ", ".join(tag["term"] for tag in entry.get("tags", []) if "term" in tag)

        self.content = "\n\n".join(
            c.get("value", "") for c in entry.get("content", [])
        ) or entry.get("summary", "")

        return self

    @classmethod
    def _parse_feed_time(cls, value) -> datetime:
        if value is None:
            return datetime.now()

        if isinstance(value, datetime):
            return value

        if isinstance(value, struct_time):
            return datetime(*value[:6])


class FeedItemBase(SQLModel):
    feed_id: int = Field(foreign_key="feed.id", primary_key=True)

    read_at: datetime | None = Field(default=None, nullable=True, index=True)
    read_later: bool = Field(default=False, index=True)
    saved_at: datetime | None = Field(default=None, nullable=True)


class FeedItem(FeedItemBase, RSS2Item, table=True):
    __tablename__ = "item"

    feed: Feed = Relationship(back_populates="items")
