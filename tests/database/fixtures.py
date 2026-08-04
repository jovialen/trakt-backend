from collections.abc import Generator

import pytest
from sqlalchemy import StaticPool, create_engine
from sqlmodel import Session, SQLModel

from trakt_backend.database.meta_fixtures import get_meta_engine
from trakt_backend.database.model import registry_metadata
from trakt_backend.database.service import TenantService


@pytest.fixture
def registry_session() -> Generator[Session, None, None]:
    get_meta_engine.cache_clear()

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    registry_metadata.create_all(engine)

    try:
        with Session(engine) as session:
            yield session
    finally:
        registry_metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def tenant_engines():
    engines = {}

    yield engines

    for engine in engines.values():
        engine.dispose()


@pytest.fixture
def tenant_service(registry_session):
    return TenantService(registry_session)


@pytest.fixture
def tenant_database_factory():
    engines = {}

    def factory(user_id: str):
        if user_id not in engines:
            engine = create_engine(
                "sqlite://",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )

            SQLModel.metadata.create_all(engine)
            engines[user_id] = engine

        return engines[user_id]

    yield factory

    for engine in engines.values():
        engine.dispose()
