from sqlmodel import Session, select

from trakt_backend.database.service import get_tenant_service
from trakt_backend.feeds import Feed


def test_create_tenant_creates_registry_entry(registry_session):
    tenant_service = get_tenant_service(registry_session)
    tenant = tenant_service.create("user_123", do_setup=False)

    assert tenant.user_id == "user_123"
    assert tenant.database_url == "sqlite:///data/user-user_123.db"

    stored = tenant_service.get("user_123")

    assert stored is not None
    assert stored.user_id == "user_123"


def test_create_tenant_is_idempotent(
    tenant_service,
):
    first = tenant_service.create("user_123")
    second = tenant_service.create("user_123")

    assert first.user_id == second.user_id
    assert first.database_url == second.database_url


def test_delete_tenant_removes_registry_entry(
    tenant_service,
):
    tenant_service.create("user_123")

    tenant_service.delete("user_123")

    assert tenant_service.get("user_123") is None


def test_tenants_have_independent_databases(
    tenant_service,
    tenant_database_factory,
):
    alice = tenant_service.create("alice")
    bob = tenant_service.create("bob")

    alice_engine = tenant_database_factory(alice.database_url)
    bob_engine = tenant_database_factory(bob.database_url)

    with Session(alice_engine) as session:
        session.add(
            Feed(
                name="Alice feed",
                link="https://alice.example.com",
            )
        )
        session.commit()

    with Session(bob_engine) as session:
        feeds = session.exec(select(Feed)).all()

    assert feeds == []
