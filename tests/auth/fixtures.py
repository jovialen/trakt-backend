from datetime import UTC, datetime, timedelta

import pytest

from trakt_backend.app import app
from trakt_backend.auth import UserToken, get_current_user


@pytest.fixture
def authenticated_user():
    now = datetime.now(UTC)

    return UserToken.model_validate(
        {
            "azp": "http://localhost:3000",
            "exp": int((now + timedelta(hours=1)).timestamp()),
            "iat": int(now.timestamp()),
            "iss": "https://clerk.example.com",
            "nbf": int((now - timedelta(minutes=1)).timestamp()),
            "sid": "session_123",
            "sub": "user_123",
            "v": 2,
            "fva": [1],
            "sts": "active",
        },
        by_alias=True,
    )


@pytest.fixture
def authenticated_client(client, authenticated_user):
    async def override():
        return authenticated_user

    app.dependency_overrides[get_current_user] = override

    yield client

    app.dependency_overrides.pop(get_current_user, None)
