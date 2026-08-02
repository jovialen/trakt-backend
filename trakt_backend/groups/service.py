from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import col, select

from ..database import SessionDep
from ..feed_group import FeedGroupLink
from ..feeds import Feed, FeedRead
from ..utils import PaginationQuery, paginate
from .dto import FeedGroupCreate, FeedGroupPatch, FeedGroupUpdate
from .model import FeedGroup


class FeedGroupService:
    def __init__(self, session: SessionDep):
        self.session = session

    def all(self, pagination: PaginationQuery | None = None):
        query = select(FeedGroup)

        if pagination is not None:
            query = paginate(query, pagination)

        groups = self.session.exec(query).all()
        return groups

    def create(self, group: FeedGroupCreate):
        db_group = FeedGroup.model_validate(group)

        self.session.add(db_group)
        self.session.commit()
        self.session.refresh(db_group)

        return db_group

    def get(self, group_id: int):
        group = self.session.get(FeedGroup, group_id)

        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        return group

    def update(self, group_id: int, group: FeedGroupUpdate):
        db_group = self.session.get(FeedGroup, group_id)

        if not db_group:
            raise HTTPException(status_code=404, detail="Group not found")

        self._patch_group(db_group, group)
        self.session.commit()
        self.session.refresh(db_group)

        return db_group

    def patch(self, group_id: int, group: FeedGroupUpdate):
        db_group = self.session.get(FeedGroup, group_id)

        if not db_group:
            raise HTTPException(status_code=404, detail="Group not found")

        self._patch_group(db_group, group)
        self.session.commit()
        self.session.refresh(db_group)

        return db_group

    def delete(self, group_id: int):
        group = self.session.get(FeedGroup, group_id)

        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        self.session.delete(group)
        self.session.commit()

        return {"ok": True}

    def get_feeds(self, group: FeedGroup):
        feeds = self.session.exec(
            select(Feed)
            .join(FeedGroupLink, col(Feed.id) == FeedGroupLink.feed_id)
            .where(col(FeedGroupLink.group_id) == group.id)
        ).all()

        return list(map(lambda feed: FeedRead.from_feed(feed), feeds))

    def add_feed(self, group: FeedGroup, feed: Feed):
        self.session.add(FeedGroupLink(group_id=group.id, feed_id=feed.id))
        self.session.commit()

    def remove_feed(self, group: FeedGroup, feed: Feed):
        feed_group_link = self.session.exec(
            select(FeedGroupLink).where(
                col(FeedGroupLink.feed_id) == feed.id, col(FeedGroupLink.group_id) == group.id
            )
        ).one_or_none()

        if not feed_group_link:
            raise HTTPException(status_code=404, detail="Feed not found")

        self.session.delete(feed_group_link)
        self.session.commit()

    def _patch_group(
        self, group: FeedGroup | type[FeedGroup], patch: FeedGroupPatch | FeedGroupUpdate
    ):
        changes = patch.model_dump(exclude_unset=True)
        for key, value in changes.items():
            setattr(group, key, value)
        self.session.add(group)


def get_feed_group_service(session: SessionDep):
    yield FeedGroupService(session)


FeedGroupServiceDep = Annotated[FeedGroupService, Depends(get_feed_group_service)]
