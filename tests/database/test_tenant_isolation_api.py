from trakt_backend.app import app
from trakt_backend.auth import get_current_user


def test_users_have_separate_feed_databases(
    client,
    authenticated_user,
):
    async def user_one():
        return authenticated_user

    app.dependency_overrides[get_current_user] = user_one

    response = client.post(
        "/feeds",
        json={
            "name": "Private feed",
            "link": "https://private.example.com",
            "groups": [],
        },
    )

    assert response.status_code == 201

    response = client.get("/feeds")

    assert len(response.json()) == 1


def test_second_user_cannot_see_first_users_feeds(
    client,
    authenticated_user,
    authenticated_user_two,
):
    async def user_one():
        return authenticated_user

    async def user_two():
        return authenticated_user_two

    app.dependency_overrides[get_current_user] = user_one

    response = client.post(
        "/feeds",
        json={
            "name": "Alice feed",
            "link": "https://alice.example.com",
            "groups": [],
        },
    )

    assert response.status_code == 201

    app.dependency_overrides[get_current_user] = user_two

    response = client.get("/feeds")

    assert response.status_code == 200
    assert response.json() == []
