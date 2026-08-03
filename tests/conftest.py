import random

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import Engine, StaticPool, event
from sqlmodel import Session, SQLModel, create_engine

from trakt_backend import app, get_session
from trakt_backend.jobs import QueueManager, get_jobs


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        echo=True,
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    try:
        with Session(engine) as session:
            yield session
    finally:
        SQLModel.metadata.drop_all(engine)
        engine.dispose()


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
def client(session: Session, jobs: QueueManager):
    def override_get_session():
        yield session

    def override_get_jobs():
        yield jobs

    random.seed(67)
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_jobs] = override_get_jobs

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


pytest_plugins = [
    "tests.feeds.fixtures",
    "tests.groups.fixtures",
    "tests.items.fixtures",
]
