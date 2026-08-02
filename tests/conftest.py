import random

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, StaticPool, event
from sqlmodel import Session, SQLModel, create_engine

from trakt_backend import app, get_session


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        echo=True,
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture
def client(session: Session):
    def override_get_session():
        yield session

    random.seed(67)
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


pytest_plugins = [
    "tests.feeds.fixtures",
    "tests.groups.fixtures",
    "tests.items.fixtures",
]
