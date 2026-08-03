from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from trakt_backend.feeds import (
    Feed,
    FeedCreate,
    FeedPatch,
    FeedService,
    FeedUpdate,
)
from trakt_backend.feeds.jobs import FeedSyncJob
from trakt_backend.utils import PaginationQuery


def test_list_feeds(feed_service: FeedService, feed_batch: list[Feed]):
    feeds = feed_service.all()

    assert len(feeds) == len(feed_batch)
    assert feeds[0].id is not None


def test_list_feeds_with_pagination(
    feed_service: FeedService,
    feed_batch: list[Feed],
):
    pagination = PaginationQuery(
        limit=10,
        offset=0,
    )

    feeds = feed_service.all(pagination)

    assert len(feeds) == 10


def test_create_feed(feed_service: FeedService):
    feed = FeedCreate(
        name="test feed",
        link="https://example.com/feed.xml",
        groups=[],
    )

    created = feed_service.create(feed)

    assert created.id is not None
    assert created.name == "test feed"
    assert created.link == "https://example.com/feed.xml"
    assert created.groups == []


def test_create_feed_with_groups(
    feed_service: FeedService,
    news_group,
):
    feed = FeedCreate(
        name="feed with groups",
        link="https://example.com/feed.xml",
        groups=[news_group.id],
    )

    created = feed_service.create(feed)

    assert created.groups == [news_group]


def test_get_feed(feed_service: FeedService, nrk_feed: Feed):
    feed = feed_service.get(nrk_feed.id)

    assert feed.id == nrk_feed.id


def test_get_feed_not_found(feed_service: FeedService):
    with pytest.raises(HTTPException) as exc_info:
        feed_service.get(999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Feed not found"


def test_update_feed(feed_service: FeedService, nrk_feed: Feed):
    update = FeedUpdate(
        name="Updated name",
        link="https://example.com/updated.xml",
        groups=[],
    )

    updated = feed_service.update(nrk_feed.id, update)

    assert updated.id == nrk_feed.id
    assert updated.name == "Updated name"
    assert updated.link == "https://example.com/updated.xml"


def test_update_feed_not_found(feed_service: FeedService):
    update = FeedUpdate(
        name="Updated name",
        link="https://example.com/updated.xml",
        groups=[],
    )

    with pytest.raises(HTTPException) as exc_info:
        feed_service.update(999999, update)

    assert exc_info.value.status_code == 404


def test_patch_feed(feed_service: FeedService, nrk_feed: Feed):
    patch = FeedPatch(
        name="Patched name",
    )

    updated = feed_service.patch(nrk_feed.id, patch)

    assert updated.id == nrk_feed.id
    assert updated.name == "Patched name"
    assert updated.link == nrk_feed.link


def test_patch_feed_groups(
    feed_service: FeedService,
    google_feed: Feed,
    technology_group,
):
    patch = FeedPatch(
        groups=[technology_group.id],
    )

    updated = feed_service.patch(google_feed.id, patch)

    assert updated.groups == [technology_group]


def test_patch_feed_not_found(feed_service: FeedService):
    patch = FeedPatch(
        name="Patched name",
    )

    with pytest.raises(HTTPException) as exc_info:
        feed_service.patch(999999, patch)

    assert exc_info.value.status_code == 404


def test_delete_feed(feed_service: FeedService, nrk_feed: Feed):
    feed_id = nrk_feed.id

    result = feed_service.delete(feed_id)

    assert result == {"ok": True}

    with pytest.raises(HTTPException) as exc_info:
        feed_service.get(feed_id)

    assert exc_info.value.status_code == 404


def test_delete_feed_not_found(feed_service: FeedService):
    with pytest.raises(HTTPException) as exc_info:
        feed_service.delete(999999)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_sync_feed(feed_service: FeedService, nrk_feed: Feed, jobs):
    jobs.add = AsyncMock()

    await feed_service.queue_sync(nrk_feed)

    jobs.add.assert_awaited_once()

    job = jobs.add.await_args.args[0]

    assert isinstance(job, FeedSyncJob)
    assert job.feed_id == nrk_feed.id
