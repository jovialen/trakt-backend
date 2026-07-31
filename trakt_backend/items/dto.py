from pydantic import Field, BaseModel

from trakt_backend.utils import PaginationQuery


class FeedItemQuery(PaginationQuery):
    feed_id: int | None = Field(default=None)
    unread: bool | None = Field(default=None)
    saved: bool | None = Field(default=None)
    read_later: bool | None = Field(default=None)
