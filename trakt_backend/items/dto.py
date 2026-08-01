from pydantic import BaseModel
from sqlmodel import col, select

from ..utils import Pagination
from .model import FeedItem


class FeedItemQuery(Pagination, BaseModel):
    unread: bool | None = None
    saved: bool | None = None
    read_later: bool | None = None

    def query(self):
        db_query = select(FeedItem)

        if self.read_later is not None:
            db_query = db_query.where(FeedItem.read_later == self.read_later)

        if self.saved is not None:
            db_query = db_query.where(col(FeedItem.read_at).isnot(None))

        if self.unread is not None:
            db_query = db_query.where(col(FeedItem.read_at).isnot(None))

        db_query = super().query(db_query)

        return db_query
