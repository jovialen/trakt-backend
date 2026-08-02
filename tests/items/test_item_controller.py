from fastapi.testclient import TestClient

from trakt_backend.items import FeedItem


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
