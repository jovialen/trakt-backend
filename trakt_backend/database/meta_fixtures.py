from functools import lru_cache
from logging import info
from threading import Lock
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from ..settings import SettingsDep
from .engine import create_database_engine
from .model import registry_metadata

engine_lock = Lock()


@lru_cache
def get_meta_engine(connection_url: str):
    info(f"Connecting to registry at {connection_url}")
    engine = create_database_engine(connection_url)

    with engine_lock:
        registry_metadata.create_all(engine)

    return engine


def get_meta_session(settings: SettingsDep):
    meta_engine = get_meta_engine(settings.registry_db_url)

    with Session(meta_engine) as session:
        yield session


MetaSessionDep = Annotated[Session, Depends(get_meta_session)]
