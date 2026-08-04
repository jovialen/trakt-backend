from random import seed

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import Engine, event
from sqlmodel import Session

from trakt_backend import app, get_session
from trakt_backend.auth import get_current_user
from trakt_backend.jobs import QueueManager, get_jobs


@pytest.fixture
def session(
    authenticated_user,
    tenant_service,
    tenant_database_factory,
):
    tenant = tenant_service.create(authenticated_user.user_id)

    engine = tenant_database_factory(tenant.database_url)

    with Session(engine) as session:
        yield session


@pytest_asyncio.fixture
async def jobs():
    jobs = QueueManager(1)
    jobs.start()

    yield jobs

    await jobs.stop()


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture
def client(
    jobs,
    session,
    authenticated_user,
):
    def override_get_session():
        yield session

    def override_get_jobs():
        yield jobs

    def override_get_current_user():
        yield authenticated_user

    seed(67)

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_jobs] = override_get_jobs
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


pytest_plugins = [
    "tests.auth.fixtures",
    "tests.feeds.fixtures",
    "tests.groups.fixtures",
    "tests.items.fixtures",
    "tests.database.fixtures",
]
