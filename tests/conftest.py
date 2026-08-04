import pytest
import pytest_asyncio
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import Engine, event
from sqlmodel import Session

from trakt_backend import app
from trakt_backend.auth import get_current_user
from trakt_backend.database.fixtures import get_session
from trakt_backend.jobs import QueueManager, get_jobs


@pytest.fixture
def session(
    authenticated_user,
    tenant_database_factory,
):
    engine = tenant_database_factory(authenticated_user.user_id)

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
    authenticated_user,
    tenant_database_factory,
):
    def override_get_jobs():
        yield jobs

    def override_get_current_user():
        yield authenticated_user

    def override_get_session(
        user=Depends(get_current_user),  # noqa: B008
    ):
        engine = tenant_database_factory(user.user_id)

        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_jobs] = override_get_jobs
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_session] = override_get_session

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
