from unittest.mock import AsyncMock

import pytest

from trakt_backend.items import FeedItemPullJob


@pytest.mark.asyncio
async def test_feed_item_pull_job_fetches_and_broadcasts(
    feed_item_service,
    news_article,
):
    feed_item_service.fetch_content = AsyncMock(
        return_value=news_article,
    )

    job = FeedItemPullJob(
        news_article.id,
        feed_item_service,
    )

    await job.execute()

    feed_item_service.fetch_content.assert_awaited_once_with(
        news_article,
    )
