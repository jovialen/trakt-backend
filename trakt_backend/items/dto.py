from pydantic import Field

from trakt_backend.utils import Pagination


class FeedItemQuery(Pagination):
    feed_id: int | None = Field(default=None)
    unread: bool | None = Field(default=None)
    saved: bool | None = Field(default=None)
    read_later: bool | None = Field(default=None)
