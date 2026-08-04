from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.requests import Request
from svix.webhooks import WebhookVerificationError

from trakt_backend.database.controller import clerk_webhook
from trakt_backend.settings import Settings


def make_request():
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/webhooks/clerk",
            "headers": [],
        }
    )


@pytest.fixture
def settings():
    return Settings(
        clerk_webhook_signing_secret="secret",
    )


@pytest.mark.asyncio
async def test_clerk_webhook_rejects_invalid_signature(settings):
    request = make_request()
    tenants = MagicMock()

    request.body = AsyncMock(return_value=b"{}")

    with patch(
        "trakt_backend.database.controller.Webhook.verify",
        side_effect=WebhookVerificationError("bad signature"),
    ):
        with pytest.raises(HTTPException) as exc:
            await clerk_webhook(request, tenants, settings)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Invalid signature"


@pytest.mark.asyncio
async def test_clerk_webhook_creates_tenant_for_user_created(settings):
    request = make_request()
    request.body = AsyncMock(return_value=b"{}")

    tenants = MagicMock()

    event = {
        "type": "user.created",
        "data": {
            "id": "user_123",
        },
    }

    with patch(
        "trakt_backend.database.controller.Webhook.verify",
        return_value=event,
    ):
        await clerk_webhook(request, tenants, settings)

    tenants.create.assert_called_once_with("user_123")


@pytest.mark.asyncio
async def test_clerk_webhook_creates_tenant_for_session_created(settings):
    request = make_request()
    request.body = AsyncMock(return_value=b"{}")

    tenants = MagicMock()

    event = {
        "type": "session.created",
        "data": {
            "user_id": "user_123",
        },
    }

    with patch(
        "trakt_backend.database.controller.Webhook.verify",
        return_value=event,
    ):
        await clerk_webhook(request, tenants, settings)

    tenants.create.assert_called_once_with("user_123")


@pytest.mark.asyncio
async def test_clerk_webhook_deletes_tenant_for_user_deleted(settings):
    request = make_request()
    request.body = AsyncMock(return_value=b"{}")

    tenants = MagicMock()

    event = {
        "type": "user.deleted",
        "data": {
            "id": "user_123",
        },
    }

    with patch(
        "trakt_backend.database.controller.Webhook.verify",
        return_value=event,
    ):
        await clerk_webhook(request, tenants, settings)

    tenants.delete.assert_called_once_with("user_123")
