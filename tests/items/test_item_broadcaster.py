import asyncio

import pytest

from trakt_backend.items.broadcaster import FeedItemBroadcaster


@pytest.mark.asyncio
async def test_publish_delivers_to_subscriber(news_article):
    broadcaster = FeedItemBroadcaster()

    subscription = broadcaster.subscribe()

    task = asyncio.create_task(subscription.__anext__())

    await asyncio.sleep(0)

    await broadcaster.new_item(news_article)

    event = await asyncio.wait_for(task, timeout=1)

    assert event.event_type == "new_item"
    assert event.item.id == news_article.id

    await subscription.aclose()


@pytest.mark.asyncio
async def test_has_subscribers():
    broadcaster = FeedItemBroadcaster()

    assert not broadcaster.has_subscribers()

    subscription = broadcaster.subscribe()
    task = asyncio.create_task(subscription.__anext__())

    await asyncio.sleep(0)

    assert broadcaster.has_subscribers()

    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    assert not broadcaster.has_subscribers()


@pytest.mark.asyncio
async def test_subscriber_replays_missed_events(news_article):
    broadcaster = FeedItemBroadcaster()

    await broadcaster.new_item(news_article)

    events = broadcaster.subscribe(last_event_id=0)

    event = await asyncio.wait_for(
        events.__anext__(),
        timeout=1,
    )

    assert event.id == 1
    assert event.item.id == news_article.id

    await events.aclose()
