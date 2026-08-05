import asyncio

import pytest

from trakt_backend.items.broadcaster import FeedItemBroadcaster


@pytest.mark.asyncio
async def test_publish_delivers_to_subscriber(news_article):
    broadcaster = FeedItemBroadcaster()

    subscription = broadcaster.subscribe()

    task = asyncio.create_task(subscription.__anext__())

    await asyncio.sleep(0)

    await broadcaster._publish(news_article)

    item = await asyncio.wait_for(task, timeout=1)

    assert item == news_article

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
