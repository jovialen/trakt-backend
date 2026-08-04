from datetime import UTC, datetime, timedelta

import pytest

from trakt_backend.auth import UserToken


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
def authenticated_user_two():
    now = datetime.now(UTC)

    return UserToken.model_validate(
        {
            "azp": "http://localhost:3000",
            "exp": int((now + timedelta(hours=1)).timestamp()),
            "iat": int(now.timestamp()),
            "iss": "https://clerk.example.com",
            "nbf": int((now - timedelta(minutes=1)).timestamp()),
            "sid": "session_456",
            "sub": "user_456",
            "v": 2,
            "fva": [1],
            "sts": "active",
        },
        by_alias=True,
    )
