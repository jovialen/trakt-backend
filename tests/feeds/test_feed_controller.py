from fastapi.testclient import TestClient

from tests.feeds.factory import FeedFactory
from trakt_backend.feeds import Feed


def test_new_feed(client: TestClient):
    response = client.get("/feeds/new")

    assert response.status_code == 200

    payload = response.json()

    assert payload["name"] == "New Feed"
    assert payload["link"] == "https://new.feed"
    assert payload["groups"] == [1]


def test_list_feeds(client: TestClient, feed_batch: list[Feed]):
    response = client.get("/feeds")

    assert response.status_code == 200

    feeds = response.json()

    assert len(feeds) == len(feed_batch)

    ids = {feed["id"] for feed in feeds}
    expected = {feed.id for feed in feed_batch}

    assert ids == expected


def test_create_feed(client: TestClient):
    feed = FeedFactory.build()

    response = client.post(
        "/feeds",
        json={
            "name": feed.name,
            "link": feed.link,
            "groups": [],
        },
    )

    assert response.status_code == 201

    created = response.json()

    assert created["id"] is not None
    assert created["name"] == feed.name
    assert created["link"] == feed.link
    assert created["groups"] == []

    persisted = client.get(f"/feeds/{created['id']}")

    assert persisted.status_code == 200
    assert persisted.json() == created


def test_get_feed(client: TestClient, nrk_feed: Feed):
    response = client.get(f"/feeds/{nrk_feed.id}")

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == nrk_feed.id
    assert body["name"] == nrk_feed.name
    assert body["link"] == nrk_feed.link


def test_get_missing_feed(client: TestClient):
    # 999999 is just an ID we know doesn't exist. If it does, then we have bigger problems than a
    # false negative here
    response = client.get("/feeds/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Feed not found"


def test_update_feed(client: TestClient, nrk_feed: Feed):
    response = client.put(
        f"/feeds/{nrk_feed.id}",
        json={
            "name": "BBC",
            "link": "https://bbc.co.uk/rss.xml",
            "groups": [],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == nrk_feed.id
    assert body["name"] == "BBC"
    assert body["link"] == "https://bbc.co.uk/rss.xml"

    persisted = client.get(f"/feeds/{nrk_feed.id}")

    assert persisted.json()["name"] == "BBC"


def test_patch_feed(client: TestClient, nrk_feed: Feed):
    response = client.patch(
        f"/feeds/{nrk_feed.id}",
        json={
            "name": "Updated NRK",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["name"] == "Updated NRK"
    assert body["link"] == nrk_feed.link


def test_delete_feed(client: TestClient, nrk_feed: Feed):
    response = client.delete(f"/feeds/{nrk_feed.id}")

    assert response.status_code == 200
    assert response.json() == {"ok": True}

    response = client.get(f"/feeds/{nrk_feed.id}")

    assert response.status_code == 404


def test_delete_missing_feed(client: TestClient):
    # Refer to the comment in the test_get_missing_feed
    response = client.delete("/feeds/999999")

    assert response.status_code == 404
