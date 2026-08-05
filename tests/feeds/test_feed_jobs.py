import datetime
from unittest.mock import AsyncMock, patch

import pytest
from sqlmodel import Session, col, select

from tests.items.factory import FeedItemFactory
from trakt_backend.feeds.jobs import FeedSyncJob
from trakt_backend.items import FeedItem, get_feed_item_broadcaster


def rss_entry(
    id: str,
    title: str = "Title",
    link: str = "https://example.com/item",
):
    return {
        "id": id,
        "title": title,
        "link": link,
        "summary": "Summary",
        "published_parsed": datetime.datetime(2000, 1, 1, 12, 0, 0),
        "updated_parsed": datetime.datetime(2001, 1, 1, 12, 30, 0),
        "authors": [{"name": "Author"}],
        "tags": [{"term": "Category"}],
        "content": [{"value": "Content"}],
    }


@pytest.mark.asyncio
async def test_feed_sync_job_adds_new_items(session: Session, nrk_feed, feed_service):
    rss = {
        "entries": [
            rss_entry("item-1", "First item"),
            rss_entry("item-2", "Second item"),
        ]
    }

    with patch("trakt_backend.feeds.service.feedparser.parse", return_value=rss):
        await FeedSyncJob(nrk_feed.id, feed_service).execute()

    items = session.exec(select(FeedItem).where(FeedItem.feed_id == nrk_feed.id)).all()

    assert len(items) == 2
    assert {item.id for item in items} == {"item-1", "item-2"}
    assert {item.title for item in items} == {"First item", "Second item"}


@pytest.mark.asyncio
async def test_feed_sync_job_skips_existing_items(session: Session, nrk_feed, feed_service):
    existing = FeedItemFactory.build(
        id="existing-item",
        feed=nrk_feed,
        title="Existing item",
        link="https://example.com/existing",
    )

    session.add(existing)
    session.commit()

    rss = {
        "entries": [
            rss_entry("existing-item", "Existing item"),
            rss_entry("new-item", "New item"),
        ]
    }

    with patch("trakt_backend.feeds.service.feedparser.parse", return_value=rss):
        await FeedSyncJob(nrk_feed.id, feed_service).execute()

    session.expire_all()

    items = session.exec(select(FeedItem).where(FeedItem.feed_id == nrk_feed.id)).all()

    assert len(items) == 2
    assert {item.id for item in items} == {"existing-item", "new-item"}


@pytest.mark.asyncio
async def test_feed_sync_job_maps_rss_fields(session: Session, nrk_feed, feed_service):
    rss = {
        "entries": [
            rss_entry(
                "item-1",
                title="Important article",
                link="https://example.com/article",
            )
        ]
    }

    with patch("trakt_backend.feeds.service.feedparser.parse", return_value=rss):
        await FeedSyncJob(nrk_feed.id, feed_service).execute()

    item = session.exec(select(FeedItem).where(col(FeedItem.id) == "item-1")).one()

    assert item.feed_id == nrk_feed.id
    assert item.title == "Important article"
    assert item.link == "https://example.com/article"
    assert item.summary == "Summary"
    assert item.authors == "Author"
    assert item.categories == "Category"
    assert item.content == "Content"


@pytest.mark.asyncio
async def test_feed_sync_job_publishes_new_items(
    session,
    nrk_feed,
    feed_service,
):
    rss = {
        "entries": [
            rss_entry("item-1"),
            rss_entry("item-2"),
        ]
    }

    broadcaster = get_feed_item_broadcaster()
    broadcaster.publish = AsyncMock()

    with patch.object(broadcaster, "has_subscribers", return_value=True):
        with patch(
            "trakt_backend.feeds.service.feedparser.parse",
            return_value=rss,
        ):
            await FeedSyncJob(nrk_feed.id, feed_service).execute()

    assert broadcaster.publish.await_count == 2


@pytest.mark.asyncio
async def test_feed_sync_job_does_not_publish_without_subscribers(
    session,
    nrk_feed,
    feed_service,
):
    rss = {
        "entries": [
            rss_entry("item-1"),
        ]
    }

    broadcaster = get_feed_item_broadcaster()
    broadcaster.publish = AsyncMock()

    with patch.object(
        broadcaster,
        "has_subscribers",
        return_value=False,
    ):
        with patch(
            "trakt_backend.feeds.service.feedparser.parse",
            return_value=rss,
        ):
            await FeedSyncJob(nrk_feed.id, feed_service).execute()

    broadcaster.publish.assert_not_awaited()
