from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import feed, settings
from .database import create_db_and_tables


@asynccontextmanager
async def lifespan(_app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan
)
app.include_router(feed.router)


@app.get("/", tags=["App"])
def app_info():
    return {
        "app_name": settings.APP_NAME,
        "app_description": settings.DESCRIPTION,
        "app_version": settings.VERSION,
    }
