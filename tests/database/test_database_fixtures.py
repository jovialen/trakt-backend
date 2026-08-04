from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from trakt_backend.database.fixtures import get_engine
from trakt_backend.database.meta_fixtures import get_meta_engine
from trakt_backend.database.model import Tenant
from trakt_backend.settings import Settings


def test_get_engine_creates_tenant_in_dev_mode(
    tenant_database_factory,
):
    user = MagicMock(user_id="user_123")
    tenants = MagicMock()
    tenants.create.return_value = Tenant(
        user_id="user_123",
        database_url="sqlite:///tenant.db",
    )

    settings = Settings(app_environment="development")

    engine = get_engine(
        user,
        tenants,
        settings,
    )

    assert engine is not None
    tenants.create.assert_called_once_with("user_123")


def test_get_engine_raises_when_tenant_missing():
    user = MagicMock(user_id="missing")
    tenants = MagicMock()
    tenants.get.return_value = None

    settings = Settings(app_environment="production")

    with pytest.raises(HTTPException) as exc:
        get_engine(
            user,
            tenants,
            settings,
        )

    assert exc.value.status_code == 500
    assert exc.value.detail == "No tenant found"


def test_get_meta_engine_creates_database():
    get_meta_engine.cache_clear()

    engine = get_meta_engine("sqlite://")

    assert engine is not None

    # Cached call should return same object
    assert get_meta_engine("sqlite://") is engine
