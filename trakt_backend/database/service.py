from threading import Lock
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel

from .meta_fixtures import MetaSessionDep
from .model import Tenant, create_tenant_engine

tenant_mutex = Lock()


class TenantService:
    def __init__(self, meta_session: Session):
        self.meta_session = meta_session

    def get(self, user_id: str) -> Tenant | type[Tenant] | None:
        tenant = self.meta_session.get(Tenant, user_id)
        return tenant

    def create(self, user_id: str, do_setup: bool = True) -> Tenant | type[Tenant]:
        with tenant_mutex:
            if tenant := self.get(user_id):
                return tenant

            # Create tenant
            tenant = self._create_tenant(user_id)

            # Set up database
            if do_setup:
                engine = create_tenant_engine(tenant.database_url)
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
        tenant = Tenant(user_id=user_id, database_url=f"sqlite:///data/user-{user_id}.db")

        self.meta_session.add(tenant)
        self.meta_session.commit()
        self.meta_session.refresh(tenant)
        return tenant

    @staticmethod
    def _delete_database(_user_id: str):
        # TODO: Delete the .db file
        pass


def get_tenant_service(meta_session: MetaSessionDep) -> TenantService:
    return TenantService(meta_session)


TenantServiceDep = Annotated[TenantService, Depends(get_tenant_service)]
