from threading import Lock
from typing import Annotated

import requests
from fastapi import Depends
from sqlmodel import Session, SQLModel

from ..settings import get_settings
from .meta_fixtures import MetaSessionDep
from .model import Tenant, create_tenant_engine

tenant_mutex = Lock()


class TenantService:
    def __init__(self, meta_session: Session):
        self.meta_session = meta_session

    def get(self, user_id: str) -> Tenant | type[Tenant] | None:
        tenant = self.meta_session.get(Tenant, user_id)
        return tenant

    def create(self, user_id: str) -> Tenant | type[Tenant]:
        with tenant_mutex:
            if tenant := self.get(user_id):
                return tenant

            # Create tenant
            tenant = self._create_tenant(user_id)

            # Set up database

            # We have to import the root app here to make sure we load all the app models into scope
            # before attempting to create them all. If we don't, then we won't get any models at all
            # when we call SQLModel.metadata.create_all(engine)

            # noinspection unused-imports

            engine = create_tenant_engine(tenant.connection_url, tenant.turso_token)
            SQLModel.metadata.create_all(engine)

            return tenant

    def delete(self, user_id: str):
        with tenant_mutex:
            tenant = self.get(user_id)
            if tenant is None:
                return

            self.meta_session.delete(tenant)
            self.meta_session.commit()

            self._delete_database(user_id)

    def _create_tenant(self, user_id: str):
        db_url, db_token = self._create_database(user_id)
        tenant = Tenant(user_id=user_id, turso_url=db_url, turso_token=db_token)

        self.meta_session.add(tenant)
        self.meta_session.commit()
        self.meta_session.refresh(tenant)
        return tenant

    @staticmethod
    def _create_database(user_id: str):
        settings = get_settings()

        if settings.dev_mode:
            return TenantService._create_local_database(user_id)
        else:
            return TenantService._create_turso_database(user_id)

    @staticmethod
    def _delete_database(user_id: str):
        settings = get_settings()

        # For local development it isn't all that important that we delete the local file,
        # and in the spirit of not accidentally deleting something important, we won't
        # either.
        if not settings.dev_mode:
            TenantService._delete_turso_database(user_id)

    @staticmethod
    def _create_local_database(user_id: str):
        return f"sqlite:///user-{user_id}-database.db", None

    @staticmethod
    def _create_turso_database(user_id: str):
        settings = get_settings()

        database_name = f"trakt-user-{user_id}"

        headers = {
            "Authorization": f"Bearer {settings.turso_api_token}",
            "Content-Type": "application/json",
        }

        # Create database
        response = requests.post(
            f"https://api.turso.tech/v1/organizations/{settings.turso_org}/databases",
            headers=headers,
            json={
                "name": database_name,
                "group": "default",
            },
            timeout=30,
        )
        response.raise_for_status()

        database = response.json()["database"]

        # Create database auth token
        response = requests.post(
            f"https://api.turso.tech/v1/organizations/{settings.turso_org}/databases/{database_name}/auth/tokens",
            headers=headers,
            json={
                "authorization": "full-access",
            },
            timeout=30,
        )
        response.raise_for_status()

        token = response.json()["jwt"]

        return database["hostname"], token

    @staticmethod
    def _delete_turso_database(user_id: str):
        settings = get_settings()

        database_name = f"trakt-user-{user_id}"

        headers = {
            "Authorization": f"Bearer {settings.turso_api_token}",
        }

        response = requests.delete(
            f"https://api.turso.tech/v1/organizations/{settings.turso_org}/databases/{database_name}",
            headers=headers,
            timeout=30,
        )

        # Treat "already deleted" as success
        if response.status_code == 404:
            return

        response.raise_for_status()


def get_tenant_service(meta_session: MetaSessionDep) -> TenantService:
    return TenantService(meta_session)


TenantServiceDep = Annotated[TenantService, Depends(get_tenant_service)]
