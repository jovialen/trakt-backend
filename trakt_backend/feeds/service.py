from logging import debug, exception, info
from typing import Annotated

import feedparser
from fastapi import Depends
from sqlalchemy import delete
from sqlmodel import col, select

from ..database import SessionDep
from ..feed_group import FeedGroupLink
from ..jobs import JobsDep, QueueManager
from ..utils import PaginationQuery, paginate
from .dto import FeedCreate, FeedPatch, FeedUpdate
from .model import Feed


class FeedService:
    def __init__(self, session: SessionDep, jobs: QueueManager):
        self.session = session
        self.jobs = jobs

    def all(self, pagination: PaginationQuery | None = None) -> list[Feed | type[Feed]]:
        query = select(Feed)

        if pagination is not None:
            query = paginate(query, pagination)

        feeds = self.session.exec(query).all()
        return feeds

    def create(self, feed: FeedCreate) -> Feed | type[Feed]:
        db_feed = Feed(**feed.model_dump(exclude={"groups"}))

        self.session.add(db_feed)
        self.session.flush()
        self.session.refresh(db_feed)

        self._add_groups_to_feed(db_feed, feed.groups)

        self.session.commit()
        self.session.refresh(db_feed)

        return db_feed

    def get(self, feed_id: int) -> Feed | type[Feed] | None:
        feed = self.session.get(Feed, feed_id)
        return feed

    def update(self, feed: Feed | type[Feed], update: FeedUpdate) -> Feed | type[Feed]:
        self._patch_feed(feed, update)
        self.session.commit()
        self.session.refresh(feed)
        return feed

    def patch(self, feed: Feed | type[Feed], patch: FeedPatch) -> Feed | type[Feed]:
        self._patch_feed(feed, patch)
        self.session.commit()
        self.session.refresh(feed)
        return feed

    def delete(self, feed: Feed | type[Feed]):
        self.session.delete(feed)
        self.session.commit()

    async def sync(self, feed: Feed | type[Feed]):
        from ..items import FeedItem, get_feed_item_broadcaster

        rss = feedparser.parse(feed.link)

        if rss.get("bozo"):
            exception(f"Feed {feed.id} contains parse errors: {rss.get('bozo_exception', '')}")
            return

        existing_ids = set(
            self.session.exec(select(FeedItem.id).where(col(FeedItem.feed_id) == feed.id)).all()
        )

        new_items = []

        for entry in rss.get("entries", []):
            item = FeedItem(feed=feed).import_from_parsed(entry)

            # This does not discover if items get changed, but that is acceptable for now
            # In the future, a possible fix to this might be to check if the published_at
            # or updated_at has been moved forward
            if item.id not in existing_ids:
                debug(f"New entry {item.id} in feed {feed.id}. Adding item to feed.")
                new_items.append(item)

        if len(new_items) > 0:
            self.session.add_all(new_items)
            self.session.commit()

        if (broadcaster := get_feed_item_broadcaster()).has_subscribers():
            for item in new_items:
                self.session.refresh(item)
                await broadcaster.publish(item)

        info(
            "Feed %s synced: %d new items",
            feed.id,
            len(new_items),
        )

    async def queue_sync(self, feed: Feed | type[Feed]):
        from .jobs import FeedSyncJob

        await self.jobs.add(FeedSyncJob(feed.id, self))

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


def get_feed_service(session: SessionDep, jobs: JobsDep):
    yield FeedService(session, jobs)


FeedServiceDep = Annotated[FeedService, Depends(get_feed_service)]
