from collections.abc import Sequence
from datetime import datetime
from logging import exception
from typing import Annotated

import trafilatura
from fastapi import Depends, Query, Request
from sqlmodel import col, select, update

from ..database import SessionDep
from ..feed_group import FeedGroupLink
from ..jobs import JobsDep, QueueManager
from .dto import FeedItemQuery
from .model import FeedItem


class FeedItemService:
    def __init__(
        self,
        session: SessionDep,
        jobs: QueueManager,
        group_scope_id: int | None = None,
        feed_scope_id: int | None = None,
    ):
        self.session = session
        self.group_scope_id = group_scope_id
        self.feed_scope_id = feed_scope_id
        self.jobs = jobs

    def all(self, query: Annotated[FeedItemQuery, Query()]) -> Sequence[FeedItem | type[FeedItem]]:
        db_query = query.query(select(FeedItem))
        db_query = self._scope_query(db_query)
        items = self.session.exec(db_query).all()
        return items

    def get(self, item_id: str) -> FeedItem | type[FeedItem] | None:
        item = self.session.exec(
            self._scope_query(select(FeedItem).where(col(FeedItem.id) == item_id))
        ).one_or_none()

        if not item:
            return None

        return item

    def mark_read(self, item: FeedItem | type[FeedItem]) -> FeedItem | type[FeedItem]:
        item.read_later = False
        item.read_at = datetime.now()

        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)

        return item

    def read_later(self, item: FeedItem | type[FeedItem]) -> FeedItem | type[FeedItem]:
        item.read_later = True

        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)

        return item

    def save(self, item: FeedItem | type[FeedItem]) -> FeedItem | type[FeedItem]:
        item.saved_at = datetime.now()

        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)

        return item

    def bulk_get(self, item_ids: list[str]) -> Sequence[FeedItem | type[FeedItem]]:
        items = self.session.exec(select(FeedItem).where(col(FeedItem.id).in_(item_ids))).all()
        return items

    def bulk_mark_read(self, item_ids: list[str]) -> Sequence[FeedItem | type[FeedItem]]:
        if not item_ids:
            return []

        self.session.exec(
            self._scope_query(
                update(FeedItem)
                .where(col(FeedItem.id).in_(item_ids))
                .values(read_at=datetime.now(), read_later=False)
            )
        )
        self.session.commit()
        return self.bulk_get(item_ids)

    def bulk_read_later(self, item_ids: list[str]) -> Sequence[FeedItem | type[FeedItem]]:
        if not item_ids:
            return []

        self.session.exec(
            self._scope_query(
                update(FeedItem).where(col(FeedItem.id).in_(item_ids)).values(read_later=True)
            )
        )
        self.session.commit()
        return self.bulk_get(item_ids)

    def bulk_save(self, item_ids: list[str]) -> Sequence[FeedItem | type[FeedItem]]:
        if not item_ids:
            return []

        self.session.exec(
            self._scope_query(
                update(FeedItem)
                .where(col(FeedItem.id).in_(item_ids))
                .values(saved_at=datetime.now())
            )
        )
        self.session.commit()
        return self.bulk_get(item_ids)

    def contains(self, item: FeedItem) -> bool:
        if self.feed_scope_id is not None:
            return item.feed_id == self.feed_scope_id

        if self.group_scope_id is not None:
            return (
                self.session.exec(
                    select(FeedGroupLink).where(
                        FeedGroupLink.group_id == self.group_scope_id,
                        FeedGroupLink.feed_id == item.feed_id,
                    )
                ).first()
                is not None
            )

        return True

    async def fetch_content(self, item: FeedItem | type[FeedItem]) -> FeedItem | type[FeedItem]:
        from .broadcaster import get_feed_item_broadcaster

        html = trafilatura.fetch_url(item.link)

        if html is None:
            exception("Failed to fetch feed item content")
            return item

        result = trafilatura.extract(
            html,
            output_format="html",
            include_images=True,
            include_comments=False,
            include_formatting=True,
            url=item.link,
        )

        if result is None:
            exception("Failed to extract feed item content")
            return item

        item.content = result
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)

        broadcaster = get_feed_item_broadcaster()
        if broadcaster.has_subscribers():
            await broadcaster.updated_item(item)

        return item

    async def queue_fetch_content(self, item: FeedItem | type[FeedItem]):
        from .jobs import FeedItemPullJob

        await self.jobs.add(FeedItemPullJob(item.id, self))

    def _scope_query(self, query):
        if self.group_scope_id is not None:
            query = query.join(FeedGroupLink, col(FeedItem.feed_id) == FeedGroupLink.feed_id).where(
                col(FeedGroupLink.group_id) == self.group_scope_id
            )

        if self.feed_scope_id is not None:
            query = query.where(col(FeedItem.feed_id) == self.feed_scope_id)

        return query


def get_feed_item_service(session: SessionDep, jobs: JobsDep, request: Request):
    group_id = request.path_params.get("group_id")
    feed_id = request.path_params.get("feed_id")

    yield FeedItemService(session, jobs, group_id, feed_id)


FeedItemServiceDep = Annotated[FeedItemService, Depends(get_feed_item_service)]
