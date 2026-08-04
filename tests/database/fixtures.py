from collections.abc import Generator

import pytest
from sqlalchemy import StaticPool, create_engine
from sqlmodel import Session, SQLModel

from trakt_backend import Settings, get_session
from trakt_backend.database.meta_fixtures import get_meta_engine, get_meta_session
from trakt_backend.database.model import Tenant, registry_metadata
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
    service = TenantService(registry_session)

    def create_tenant(user_id: str):
        tenant = Tenant(
            user_id=user_id,
            database_url=f"sqlite:///file:{user_id}?mode=memory&cache=shared&uri=true",
        )

        service.meta_session.add(tenant)
        service.meta_session.commit()
        service.meta_session.refresh(tenant)

        return tenant

    service._create_tenant = create_tenant

    return service


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


def test_get_session_yields_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    generator = get_session(engine)

    session = next(generator)

    assert isinstance(session, Session)

    with pytest.raises(StopIteration):
        next(generator)


def test_get_meta_session_yields_session():
    get_meta_engine.cache_clear()

    settings = Settings(
        registry_db_url="sqlite://",
    )

    generator = get_meta_session(settings)

    session = next(generator)

    assert isinstance(session, Session)

    with pytest.raises(StopIteration):
        next(generator)
