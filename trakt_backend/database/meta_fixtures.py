from functools import lru_cache
from logging import info
from threading import Lock
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Engine
from sqlmodel import Session

from ..settings import SettingsDep
from .engine import create_secure_engine
from .model import registry_metadata

engine_lock = Lock()


@lru_cache
def get_meta_engine(settings: SettingsDep):
    connection_url = (
        (f"sqlite+{settings.registry_db_url}?secure=true")
        if not settings.dev_mode
        else settings.registry_db_url
    )

    info(f"Connecting to registry at {connection_url}")
    engine = create_secure_engine(connection_url, settings.registry_db_token)

    with engine_lock:
        registry_metadata.create_all(engine)

    return engine


MetaEngineDep = Annotated[Engine, Depends(get_meta_engine)]


def get_meta_session(meta_engine: MetaEngineDep):
    with Session(meta_engine) as session:
        yield session


MetaSessionDep = Annotated[Session, Depends(get_meta_session)]
