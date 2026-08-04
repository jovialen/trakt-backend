from fastapi.testclient import TestClient

from trakt_backend import app


def test_get_auth_token(client, authenticated_user):
    response = client.get("/auth/")

    assert response.status_code == 200

    body = response.json()

    assert body["sub"] == authenticated_user.sub
    assert body["user_id"] == authenticated_user.user_id
    assert body["azp"] == authenticated_user.authorized_party
    assert body["sts"] == authenticated_user.session_status
    assert body["is_valid"] is True


def test_auth_requires_credentials():
    with TestClient(app) as unauthenticated_client:
        response = unauthenticated_client.get("/auth/")

        assert response.status_code == 401
