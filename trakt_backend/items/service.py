from datetime import datetime
from typing import Annotated

from fastapi import Depends, HTTPException, Query, Request
from sqlmodel import col, select, update

from ..database import SessionDep
from ..feed_group import FeedGroupLink
from .dto import FeedItemQuery
from .model import FeedItem


class FeedItemService:
    def __init__(
        self,
        session: SessionDep,
        group_scope_id: int | None = None,
        feed_scope_id: int | None = None,
    ):
        self.session = session
        self.group_scope_id = group_scope_id
        self.feed_scope_id = feed_scope_id

    def all(self, query: Annotated[FeedItemQuery, Query()]):
        db_query = query.query(select(FeedItem))
        db_query = self._scope_query(db_query)
        items = self.session.exec(db_query).all()
        return items

    def get(self, item_id: int):
        item = self.session.exec(
            self._scope_query(select(FeedItem).where(col(FeedItem.id) == item_id))
        ).one_or_none()

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        return item

    def mark_read(self, item: FeedItem, commit: bool = True):
        item.read_later = False
        item.read_at = datetime.now()

        self.session.add(item)

        if commit:
            self.session.commit()
            self.session.refresh(item)

        return item

    def read_later(self, item: FeedItem, commit: bool = True):
        item.read_later = True

        self.session.add(item)

        if commit:
            self.session.commit()
            self.session.refresh(item)

        return item

    def save(self, item: FeedItem, commit: bool = True):
        item.saved_at = datetime.now()

        self.session.add(item)

        if commit:
            self.session.commit()
            self.session.refresh(item)

        return item

    def bulk_mark_read(self, item_ids: list[str], commit: bool = True):
        if not item_ids:
            return []

        items = (
            self.session.exec(
                self._scope_query(
                    update(FeedItem)
                    .where(col(FeedItem.id).in_(item_ids))
                    .values(read_at=datetime.now(), read_later=False)
                    .returning(FeedItem)
                )
            )
            .scalars()
            .all()
        )

        if commit:
            self.session.commit()

        return items

    def bulk_read_later(self, item_ids: list[str], commit: bool = True):
        if not item_ids:
            return []

        items = (
            self.session.exec(
                self._scope_query(
                    update(FeedItem)
                    .where(col(FeedItem.id).in_(item_ids))
                    .values(read_later=True)
                    .returning(FeedItem)
                )
            )
            .scalars()
            .all()
        )

        if commit:
            self.session.commit()

        return items

    def bulk_save(self, item_ids: list[str], commit: bool = True):
        if not item_ids:
            return []

        items = (
            self.session.exec(
                self._scope_query(
                    update(FeedItem)
                    .where(col(FeedItem.id).in_(item_ids))
                    .values(saved_at=datetime.now())
                    .returning(FeedItem)
                )
            )
            .scalars()
            .all()
        )

        if commit:
            self.session.commit()

        return items

    def _scope_query(self, query):
        if self.group_scope_id is not None:
            query = query.join(FeedGroupLink, col(FeedItem.feed_id) == FeedGroupLink.feed_id).where(
                col(FeedGroupLink.group_id) == self.group_scope_id
            )

        if self.feed_scope_id is not None:
            query = query.where(col(FeedItem.feed_id) == self.feed_scope_id)

        return query


def get_feed_item_service(session: SessionDep, request: Request):
    group_id = request.path_params.get("group_id")
    feed_id = request.path_params.get("feed_id")

    yield FeedItemService(session, group_id, feed_id)


FeedItemServiceDep = Annotated[FeedItemService, Depends(get_feed_item_service)]
