from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import feed
from .database import create_db_and_tables


@asynccontextmanager
async def lifespan(_app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(feed.router)
