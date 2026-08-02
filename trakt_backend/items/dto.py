from pydantic import BaseModel
from sqlmodel import col

from ..utils import Pagination
from .model import FeedItem


class FeedItemQuery(Pagination, BaseModel):
    unread: bool | None = None
    saved: bool | None = None
    read_later: bool | None = None

    def query(self, query):
        if self.read_later is not None:
            query = query.where(col(FeedItem.read_later) == self.read_later)

        if self.saved:
            query = query.where(col(FeedItem.saved_at).is_not(None))
        elif self.saved is False:
            query = query.where(col(FeedItem.saved_at).is_(None))

        if self.unread:
            query = query.where(col(FeedItem.read_at).is_(None))
        elif self.unread is False:
            query = query.where(col(FeedItem.read_at).is_not(None))

        query = super().query(query)

        return query
