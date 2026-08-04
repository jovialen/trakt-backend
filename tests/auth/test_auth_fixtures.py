from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.requests import Request

from trakt_backend.auth.fixtures import get_current_user
from trakt_backend.settings import Settings


def make_request():
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/auth",
            "headers": [],
        }
    )


@pytest.fixture
def settings():
    return Settings(
        clerk_secret_key="secret",
        clerk_authorized_parties="http://localhost:3000",
    )


@pytest.mark.asyncio
async def test_get_current_user_returns_user(settings):
    request = make_request()

    state = SimpleNamespace(
        is_signed_in=True,
        message=None,
        payload={
            "azp": "http://localhost:3000",
            "exp": 2000000000,
            "iat": 1999999000,
            "iss": "https://clerk.example.com",
            "nbf": 1999999000,
            "sid": "session_123",
            "sub": "user_123",
            "v": 2,
            "fva": [1],
            "sts": "active",
        },
    )

    with patch(
        "trakt_backend.auth.fixtures.authenticate_request_async",
        AsyncMock(return_value=state),
    ):
        user = await get_current_user(request, settings, object())

    assert user.sub == "user_123"
    assert user.user_id == "user_123"


@pytest.mark.asyncio
async def test_get_current_user_rejects_unsigned_request(settings):
    request = make_request()

    state = SimpleNamespace(
        is_signed_in=False,
        message="Unauthorized",
        payload=None,
    )

    with patch(
        "trakt_backend.auth.fixtures.authenticate_request_async",
        AsyncMock(return_value=state),
    ):
        with pytest.raises(HTTPException) as exc:
            await get_current_user(request, settings, object())

    assert exc.value.status_code == 401
    assert exc.value.detail == "Unauthorized"


@pytest.mark.asyncio
async def test_get_current_user_requires_sub(settings):
    request = make_request()

    state = SimpleNamespace(
        is_signed_in=True,
        message=None,
        payload={
            "azp": "http://localhost:3000",
            "exp": 2000000000,
            "iat": 1999999000,
            "iss": "https://clerk.example.com",
            "nbf": 1999999000,
            "sid": "session_123",
            "v": 2,
            "fva": [1],
            "sts": "active",
        },
    )

    with patch(
        "trakt_backend.auth.fixtures.authenticate_request_async",
        AsyncMock(return_value=state),
    ):
        with pytest.raises(HTTPException) as exc:
            await get_current_user(request, settings, object())

    assert exc.value.status_code == 401
    assert exc.value.detail == "Could not validate credentials"
