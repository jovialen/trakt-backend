from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import feeds, items
from .settings import *
from .database import create_db_and_tables


@asynccontextmanager
async def lifespan(_app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title=APP_NAME,
    description=DESCRIPTION,
    version=VERSION,
    lifespan=lifespan
)

app.include_router(feeds.router)
app.include_router(items.router)


@app.get("/", tags=["App"])
def app_info():
    return {
        "app_name": APP_NAME,
        "app_description": DESCRIPTION,
        "app_version": VERSION,
    }
