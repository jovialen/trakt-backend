from functools import lru_cache
from logging import info

from sqlalchemy import Engine, MetaData
from sqlmodel import Field, SQLModel

from .engine import create_database_engine

registry_metadata = MetaData()


@lru_cache
def create_tenant_engine(connection_url: str) -> Engine:
    info(f"Connecting to tenant db at {connection_url}")
    return create_database_engine(connection_url)


class Tenant(SQLModel, table=True):
    metadata = registry_metadata

    user_id: str = Field(primary_key=True)
    database_url: str
