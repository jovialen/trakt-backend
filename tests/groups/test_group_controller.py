from unittest.mock import AsyncMock, patch


def test_new_group(client):
    response = client.get("/groups/new")

    assert response.status_code == 200

    payload = response.json()

    assert payload["name"] == "New Group"


def test_list_groups(client):
    response = client.get("/groups/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_group(client):
    response = client.post(
        "/groups/",
        json={
            "name": "New group",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["name"] == "New group"


def test_get_group(client, news_group):
    response = client.get(f"/groups/{news_group.id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == news_group.id
    assert data["name"] == "News"


def test_get_missing_group(client):
    response = client.get("/groups/99999")

    assert response.status_code == 404


def test_update_group(client, news_group):
    response = client.put(
        f"/groups/{news_group.id}",
        json={
            "name": "Updated news_group",
        },
    )

    assert response.status_code == 200

    assert response.json()["name"] == "Updated news_group"


def test_patch_group(client, news_group):
    response = client.patch(
        f"/groups/{news_group.id}",
        json={
            "name": "Patched news_group",
        },
    )

    assert response.status_code == 200

    assert response.json()["name"] == "Patched news_group"


def test_delete_group(client, news_group):
    response = client.delete(f"/groups/{news_group.id}")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_get_group_feeds(client, news_group, nrk_feed):
    response = client.get(f"/groups/{news_group.id}/feeds")

    assert response.status_code == 200

    feeds = response.json()

    assert len(feeds) == 1
    assert nrk_feed.id in [feed["id"] for feed in feeds]


def test_add_feed_to_group(client, blogs_group, tekno_feed):
    before = client.get(f"/groups/{blogs_group.id}/feeds/{tekno_feed.id}")
    assert before.status_code == 404, "found feed not in grouo"

    response = client.put(f"/groups/{blogs_group.id}/feeds/{tekno_feed.id}")
    assert response.status_code == 200, "failed to add feed to group"

    persistence = client.get(f"/groups/{blogs_group.id}/feeds/{tekno_feed.id}")
    assert persistence.status_code == 200, "failed to find feed in group"


def test_add_missing_feed_to_group(client, blogs_group):
    response = client.put(f"/groups/{blogs_group.id}/feeds/999999")
    assert response.status_code == 404


def test_remove_feed_from_group(client, news_group, nrk_feed):
    response = client.delete(f"/groups/{news_group.id}/feeds/{nrk_feed.id}")

    assert response.status_code == 200


def test_remove_missing_feed_from_group(client, technology_group, nrk_feed):
    response = client.delete(f"/groups/{technology_group.id}/feeds/{nrk_feed.id}")

    assert response.status_code == 404


def test_update_missing_group(client):
    response = client.put(
        "/groups/999999",
        json={
            "name": "Updated",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found"


def test_patch_missing_group(client):
    response = client.patch(
        "/groups/999999",
        json={
            "name": "Patched",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found"


def test_delete_missing_group(client):
    response = client.delete("/groups/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found"


def test_get_missing_group_feeds(client):
    response = client.get("/groups/999999/feeds")

    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found"


def test_get_group_feed_missing_group(client, nrk_feed):
    response = client.get(f"/groups/999999/feeds/{nrk_feed.id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found"


def test_get_group_feed_missing_feed(client, news_group):
    response = client.get(f"/groups/{news_group.id}/feeds/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Feed not found"


def test_add_feed_to_missing_group(client, nrk_feed):
    response = client.put(f"/groups/999999/feeds/{nrk_feed.id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found"


def test_remove_feed_from_missing_group(client, nrk_feed):
    response = client.delete(f"/groups/999999/feeds/{nrk_feed.id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found"


def test_sync_group_feeds(client, news_group):
    with patch(
        "trakt_backend.groups.controller.FeedService.queue_sync",
        new_callable=AsyncMock,
    ) as queue_sync:
        response = client.post(f"/groups/{news_group.id}/feeds/sync")

    assert response.status_code == 200
    assert queue_sync.await_count == len(news_group.feeds)
