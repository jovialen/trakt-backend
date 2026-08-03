from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlmodel import col, select

from ..database import SessionDep
from ..feed_group import FeedGroupLink
from ..feeds import Feed
from ..utils import PaginationQuery, paginate
from .dto import FeedGroupCreate, FeedGroupPatch, FeedGroupUpdate
from .model import FeedGroup


class FeedGroupService:
    def __init__(self, session: SessionDep):
        self.session = session

    def all(
        self, pagination: PaginationQuery | None = None
    ) -> Sequence[FeedGroup | type[FeedGroup]]:
        query = select(FeedGroup)

        if pagination is not None:
            query = paginate(query, pagination)

        groups = self.session.exec(query).all()
        return groups

    def create(self, group: FeedGroupCreate) -> FeedGroup | type[FeedGroup]:
        db_group = FeedGroup.model_validate(group)

        self.session.add(db_group)
        self.session.commit()
        self.session.refresh(db_group)

        return db_group

    def get(self, group_id: int) -> FeedGroup | type[FeedGroup] | None:
        group = self.session.get(FeedGroup, group_id)
        return group

    def update(
        self, group: FeedGroup | type[FeedGroup], update: FeedGroupUpdate
    ) -> FeedGroup | type[FeedGroup]:
        self._patch_group(group, update)
        self.session.commit()
        self.session.refresh(group)
        return group

    def patch(
        self, group: FeedGroup | type[FeedGroup], patch: FeedGroupPatch
    ) -> FeedGroup | type[FeedGroup]:
        self._patch_group(group, patch)
        self.session.commit()
        self.session.refresh(group)
        return group

    def delete(self, group: FeedGroup | type[FeedGroup]):
        self.session.delete(group)
        self.session.commit()

    def get_feeds(self, group: FeedGroup | type[FeedGroup]) -> Sequence[Feed | type[Feed]]:
        feeds = self.session.exec(
            select(Feed)
            .join(FeedGroupLink, col(Feed.id) == FeedGroupLink.feed_id)
            .where(col(FeedGroupLink.group_id) == group.id)
        ).all()

        return feeds

    def add_feed(self, group: FeedGroup | type[FeedGroup], feed: Feed | type[Feed]):
        self.session.add(FeedGroupLink(group_id=group.id, feed_id=feed.id))
        self.session.commit()

    def remove_feed(self, group: FeedGroup | type[FeedGroup], feed: Feed | type[Feed]):
        feed_group_link = self.session.exec(
            select(FeedGroupLink).where(
                col(FeedGroupLink.feed_id) == feed.id, col(FeedGroupLink.group_id) == group.id
            )
        ).one_or_none()

        if not feed_group_link:
            return False

        self.session.delete(feed_group_link)
        self.session.commit()
        return True

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
