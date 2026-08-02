from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import delete
from sqlmodel import select

from ..database import SessionDep
from ..feed_group import FeedGroupLink
from ..utils import PaginationQuery, paginate
from .dto import FeedCreate, FeedPatch, FeedRead, FeedUpdate
from .model import Feed


class FeedService:
    def __init__(self, session: SessionDep):
        self.session = session

    def all(self, pagination: PaginationQuery | None = None) -> list[FeedRead]:
        query = select(Feed)

        if pagination is not None:
            query = paginate(query, pagination)

        feeds = self.session.exec(query).all()
        return list(map(lambda feed: FeedRead.from_feed(feed), feeds))

    def create(self, feed: FeedCreate) -> FeedRead:
        db_feed = Feed(**feed.model_dump(exclude={"groups"}))

        self.session.add(db_feed)
        self.session.flush()
        self.session.refresh(db_feed)

        self._add_groups_to_feed(db_feed, feed.groups)

        self.session.commit()
        db_feed = self.session.get(Feed, db_feed.id)

        return FeedRead.from_feed(db_feed)

    def get(self, feed_id: int) -> FeedRead:
        feed = self.session.get(Feed, feed_id)

        if not feed:
            raise HTTPException(status_code=404, detail="Feed not found")

        return FeedRead.from_feed(feed)

    def update(self, feed_id: int, feed: FeedUpdate) -> FeedRead:
        db_feed = self.session.get(Feed, feed_id)

        if not db_feed:
            raise HTTPException(status_code=404, detail="Feed not found")

        self._patch_feed(db_feed, feed)
        self.session.commit()
        db_feed = self.session.get(Feed, db_feed.id)

        return FeedRead.from_feed(db_feed)

    def patch(self, feed_id: int, patch: FeedPatch) -> FeedRead:
        db_feed = self.session.get(Feed, feed_id)

        if not db_feed:
            raise HTTPException(status_code=404, detail="Feed not found")

        self._patch_feed(db_feed, patch)
        self.session.commit()
        db_feed = self.session.get(Feed, db_feed.id)

        return FeedRead.from_feed(db_feed)

    def delete(self, feed_id: int):
        feed = self.session.get(Feed, feed_id)

        if not feed:
            raise HTTPException(status_code=404, detail="Feed not found")

        self.session.delete(feed)
        self.session.commit()

        return {"ok": True}

    def _add_groups_to_feed(self, feed: Feed | type[Feed], group_ids: list[int]):
        self.session.exec(delete(FeedGroupLink).where(FeedGroupLink.feed_id == feed.id))

        for group_id in group_ids:
            self.session.add(FeedGroupLink(feed_id=feed.id, group_id=group_id))

    def _patch_feed(self, feed: Feed | type[Feed], changes: FeedPatch | FeedUpdate):
        updates = changes.model_dump(exclude={"groups"}, exclude_unset=True)

        for key, value in updates.items():
            setattr(feed, key, value)

        self.session.add(feed)

        if changes.groups is not None:
            self._add_groups_to_feed(feed, changes.groups)


def get_feed_service(session: SessionDep):
    yield FeedService(session)


FeedServiceDep = Annotated[FeedService, Depends(get_feed_service)]
