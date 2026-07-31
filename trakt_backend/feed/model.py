from sqlmodel import SQLModel, Field


# A regex pattern which matches the majority of URLs which would be used as RSS feed endpoints
RSS_FEED_REGEX = r'(?i)\bhttps?://[^\s()<>]+(?:\bfeed\b|\brss\b|\bxml\b|\batom\b|\.xml|\.rss|\?format=rss)[^\s()<>]*'


class FeedBase(SQLModel):
    name: str = Field(min_length=1, max_length=50)
    link: str = Field(min_length=1, max_length=200, regex=RSS_FEED_REGEX)


class Feed(FeedBase, table=True):
    id: int = Field(default=None, primary_key=True)


class FeedCreate(FeedBase):
    pass


class FeedUpdate(FeedBase):
    pass


class FeedPatch(FeedBase):
    name: str | None = None
    link: str | None = None
