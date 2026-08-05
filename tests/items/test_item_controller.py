import asyncio
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from trakt_backend.items import FeedItem, FeedItemService
from trakt_backend.items.broadcaster import (
    FeedItemBroadcaster,
    stream_feed_items,
)


def test_list_items(client: TestClient, article_batch: list[FeedItem]):
    response = client.get("/items/", params={"limit": 100, "offset": 0})

    assert response.status_code == 200
    assert len(response.json()) == 100


def test_list_items_second_page(client: TestClient, article_batch: list[FeedItem]):
    response = client.get("/items/", params={"limit": 100, "offset": 100})

    assert response.status_code == 200
    assert len(response.json()) == 100


def test_list_items_with_pagination(client: TestClient, article_batch: list[FeedItem]):
    response = client.get("/items/", params={"limit": 10, "offset": 0})

    assert response.status_code == 200
    assert len(response.json()) == 10


def test_list_unread_items(client: TestClient, article_batch: list[FeedItem]):
    response = client.get("/items/", params={"unread": True, "limit": 100})

    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(item["read_at"] is None for item in data)


def test_list_read_items(
    client: TestClient,
    article_batch: list[FeedItem],
    session,
):
    response = client.get("/items/", params={"unread": False, "limit": 100})

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0
    assert all(item["read_at"] is not None for item in data)


def test_list_saved_items(
    client: TestClient,
    article_batch: list[FeedItem],
    session,
):
    response = client.get("/items/", params={"saved": True, "limit": 100})

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0
    assert all(item["saved_at"] is not None for item in data)


def test_list_read_later_items(
    client: TestClient,
    article_batch: list[FeedItem],
    session,
):
    response = client.get("/items/", params={"read_later": True, "limit": 100})

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0
    assert all(item["read_later"] is True for item in data)


def test_get_item(client: TestClient, news_article: FeedItem):
    response = client.get(f"/items/{news_article.id}")

    assert response.status_code == 200
    assert response.json()["id"] == news_article.id


def test_get_item_not_found(client: TestClient):
    response = client.get("/items/does-not-exist")

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_read_item(client: TestClient, news_article: FeedItem):
    assert news_article.read_at is None

    response = client.post(f"/items/{news_article.id}/read")

    assert response.status_code == 200
    data = response.json()
    assert data["read_at"] is not None
    assert data["read_later"] is False


def test_read_item_clears_read_later(
    client: TestClient,
    news_article: FeedItem,
    session,
):
    news_article.read_later = True
    session.add(news_article)
    session.commit()

    response = client.post(f"/items/{news_article.id}/read")

    assert response.status_code == 200
    data = response.json()
    assert data["read_at"] is not None
    assert data["read_later"] is False


def test_read_item_not_found(client: TestClient):
    response = client.post("/items/does-not-exist/read")

    assert response.status_code == 404


def test_read_item_later(client: TestClient, news_article: FeedItem):
    assert news_article.read_later is False

    response = client.post(f"/items/{news_article.id}/read_later")

    assert response.status_code == 200
    assert response.json()["read_later"] is True


def test_read_item_later_not_found(client: TestClient):
    response = client.post("/items/does-not-exist/read_later")

    assert response.status_code == 404


def test_save_item(client: TestClient, news_article: FeedItem):
    assert news_article.saved_at is None

    response = client.post(f"/items/{news_article.id}/save")

    assert response.status_code == 200
    assert response.json()["saved_at"] is not None


def test_save_item_not_found(client: TestClient):
    response = client.post("/items/does-not-exist/save")

    assert response.status_code == 404


def test_bulk_read_items(client: TestClient, article_batch: list[FeedItem]):
    item_ids = [item.id for item in article_batch[:3]]

    response = client.post("/items/read", json=item_ids)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 3
    assert all(item["read_at"] is not None for item in data)
    assert all(item["read_later"] is False for item in data)


def test_bulk_read_items_empty(client: TestClient):
    response = client.post("/items/read", json=[])

    assert response.status_code == 200
    assert response.json() == []


def test_bulk_read_items_later(client: TestClient, article_batch: list[FeedItem]):
    item_ids = [item.id for item in article_batch[:3]]

    response = client.post("/items/read_later", json=item_ids)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(item["read_later"] is True for item in data)


def test_bulk_read_items_later_empty(client: TestClient):
    response = client.post("/items/read_later", json=[])

    assert response.status_code == 200
    assert response.json() == []


def test_bulk_save_items(client: TestClient, article_batch: list[FeedItem]):
    item_ids = [item.id for item in article_batch[:3]]

    response = client.post("/items/save", json=item_ids)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(item["saved_at"] is not None for item in data)


def test_bulk_save_items_empty(client: TestClient):
    response = client.post("/items/save", json=[])

    assert response.status_code == 200
    assert response.json() == []


def test_stream_items_endpoint(client):
    async def fake_events(*_):
        yield "event: new_item\ndata: {}\n\n"

    with patch(
        "trakt_backend.items.controller.stream_feed_items",
        fake_events,
    ):
        response = client.get("/items/stream")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")


@pytest.mark.asyncio
async def test_feed_item_events_streams_matching_item(
    feed_item_service,
    news_article,
):
    broadcaster = FeedItemBroadcaster()

    events = stream_feed_items(broadcaster, feed_item_service)

    task = asyncio.create_task(events.__anext__())

    await asyncio.sleep(0)

    await broadcaster._publish(news_article)

    event = await asyncio.wait_for(task, timeout=1)

    assert event.startswith("event: new_item")
    assert news_article.id in event

    await events.aclose()


@pytest.mark.asyncio
async def test_feed_item_events_filters_non_matching_items(
    session,
    nrk_feed,
    tekno_feed,
    news_article,
):
    service = FeedItemService(
        session,
        feed_scope_id=tekno_feed.id,
    )

    broadcaster = FeedItemBroadcaster()

    events = stream_feed_items(broadcaster, service)

    task = asyncio.create_task(events.__anext__())

    await asyncio.sleep(0)

    await broadcaster._publish(news_article)

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(task, timeout=0.1)

    task.cancel()
    await events.aclose()
