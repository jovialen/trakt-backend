from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

# Circular import here, but since its only because of type checking, this is an acceptable solution
if TYPE_CHECKING:
    from ..groups.model import FeedGroup
    from ..items.model import FeedItem
from ..feed_group.model import FeedGroupLink

# A regex pattern which matches the majority of URLs which would be used as RSS feeds endpoints
RSS_FEED_REGEX = r"(?i)\bhttps?://[^\s()<>]+(?:\bfeeds\b|\brss\b|\bxml\b|\batom\b|\.xml|\.rss|\?format=rss)[^\s()<>]*"


class FeedBase(SQLModel):
    name: str = Field(min_length=1, max_length=50)
    link: str = Field(min_length=1, max_length=200, schema_extra={"pattern": RSS_FEED_REGEX})


class Feed(FeedBase, table=True):
    id: int = Field(default=None, primary_key=True)

    # noinspection type-hints
    groups: list[FeedGroup] = Relationship(
        back_populates="feeds",
        link_model=FeedGroupLink,
        sa_relationship_kwargs={"passive_deletes": True},
    )

    items: list[FeedItem] = Relationship(
        back_populates="feed",
    )
