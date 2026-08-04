from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import Engine
from sqlmodel import Session

from ..auth import UserDep
from ..settings import SettingsDep
from .model import create_tenant_engine
from .service import TenantServiceDep


def get_engine(user: UserDep, tenants: TenantServiceDep, settings: SettingsDep):
    # For production instances, we use webhooks for identifying new users so we can create tenants,
    # but since webhooks don't work for localhost (which I totally didn't forget) we have to
    # lazily create tenants as users make requests here.
    tenant = tenants.get(user.user_id) if not settings.dev_mode else tenants.create(user.user_id)

    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No tenant found"
        )

    return create_tenant_engine(tenant.database_url)


EngineDep = Annotated[Engine, Depends(get_engine)]


def get_session(engine: EngineDep):
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
