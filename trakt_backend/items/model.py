from datetime import datetime
from typing import Self

from sqlmodel import Field, SQLModel


class RSS2Item(SQLModel):
    id: str = Field(default=None, primary_key=True)
    guid: str = Field(unique=True)
    feed_id: int = Field(foreign_key="feed.id", nullable=False, index=True)
    title: str
    link: str
    summary: str
    published_at: datetime
    updated_at: datetime
    authors: str
    categories: str
    content: str

    def from_parsed(self, feed: dict) -> Self:
        self.id = feed.get("id", None)
        self.guid = feed.get("guid", None)
        self.title = feed.get("title", None)
        self.link = feed.get("link", None)
        self.summary = feed.get("summary", None)
        self.published_at = feed.get("published_parsed", None)
        self.updated_at = feed.get("updated_parsed", None)
        self.authors = feed.get("authors", [])
        self.categories = feed.get("categories", [])
        self.content = feed.get("content", None)

        if (author := feed.get("author")) is not None and author not in self.authors:
            self.authors.insert(0, author)

        self.authors = ";".join(self.authors)
        self.categories = ";".join(self.categories)

        return self


class FeedItemBase(SQLModel):
    read_at: datetime | None = Field(default=None, nullable=True, index=True)
    read_later: bool = Field(default=False, index=True)
    saved_at: datetime | None = Field(default=None, nullable=True)


class FeedItem(FeedItemBase, RSS2Item, table=True):
    pass
