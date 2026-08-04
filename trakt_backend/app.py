import logging
from contextlib import asynccontextmanager
from logging import error, info

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware

from . import auth, feeds, groups, items
from .database import create_db_and_tables
from .jobs import get_jobs
from .settings import APP_NAME, DESCRIPTION, VERSION, get_settings

# ---- Logger -----


class Formatter(logging.Formatter):
    def format(self, record):
        record.levelname_padded = f"{record.levelname}:".ljust(9)
        return super().format(record)


settings = get_settings()

handler = logging.StreamHandler()
handler.setFormatter(Formatter("%(levelname_padded)s %(message)s"))

logging.basicConfig(
    level=logging.DEBUG if settings.dev_mode else logging.INFO,
    handlers=[handler],
)


# ----- App -----


info(f"Starting app in {settings.app_environment} mode")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    jobs = get_jobs()

    # Set up
    create_db_and_tables()
    jobs.start()

    # Run
    yield

    # Clean up
    await jobs.stop()


app = FastAPI(title=APP_NAME, description=DESCRIPTION, version=VERSION, lifespan=lifespan)

app.include_router(auth.router)
app.include_router(feeds.router)
app.include_router(items.router)
app.include_router(groups.router)


@app.get("/", tags=["App"])
def app_info():
    return {
        "app_name": APP_NAME,
        "app_description": DESCRIPTION,
        "app_version": VERSION,
    }


# ----- Development mode -----

if settings.dev_mode:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.clerk_authorized_parties_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def app_exception_handler(request: Request, exception: Exception):
        error(f"request: {request.url}, headers: {request.headers} - {exception}")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=str(exception))
