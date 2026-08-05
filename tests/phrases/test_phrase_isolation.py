from trakt_backend.app import app
from trakt_backend.auth import get_current_user


def test_users_have_separate_phrase_databases(
    client,
    authenticated_user,
):
    async def user():
        return authenticated_user

    app.dependency_overrides[get_current_user] = user

    client.post(
        "/phrases",
        json={
            "phrase": "war",
            "color": "#ff0000",
        },
    )

    response = client.get("/phrases")

    assert len(response.json()) == 1


def test_second_user_cannot_see_first_users_phrases(
    client,
    authenticated_user,
    authenticated_user_two,
):
    async def user_one():
        return authenticated_user

    async def user_two():
        return authenticated_user_two

    app.dependency_overrides[get_current_user] = user_one

    client.post(
        "/phrases",
        json={
            "phrase": "war",
            "color": "#ff0000",
        },
    )

    app.dependency_overrides[get_current_user] = user_two

    response = client.get("/phrases")

    assert response.status_code == 200
    assert response.json() == []
