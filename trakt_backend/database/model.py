from functools import lru_cache
from logging import info

from pydantic import computed_field
from sqlalchemy import Engine, MetaData
from sqlmodel import Field, SQLModel

from ..settings import get_settings
from .engine import create_secure_engine

registry_metadata = MetaData()


@lru_cache
def create_tenant_engine(connection_url: str, auth_token: str | None) -> Engine:
    info(f"Connecting to tenant db at {connection_url}")
    return create_secure_engine(connection_url, auth_token)


class Tenant(SQLModel, table=True):
    metadata = registry_metadata

    user_id: str = Field(primary_key=True)

    turso_url: str
    turso_token: str | None = None

    @computed_field
    @property
    def connection_url(self) -> str:
        settings = get_settings()

        # Dev mode override which allows us to use local sqlite files instead
        if settings.dev_mode:
            return self.turso_url

        return f"sqlite+libsql://{self.turso_url}/?authToken={self.turso_token}&secure=true"
