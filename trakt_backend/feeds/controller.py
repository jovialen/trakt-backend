from fastapi import APIRouter, HTTPException, status

from .. import items
from ..utils import PaginationQuery
from .dto import FeedCreate, FeedPatch, FeedRead, FeedUpdate
from .service import FeedServiceDep

router = APIRouter(prefix="/feeds", tags=["Feed"])

router.include_router(items.router, prefix="/{feed_id}", tags=["Feed"])


@router.get("/new", response_model=FeedCreate)
def new_feed():
    return FeedCreate(name="New Feed", link="https://new.feed", groups=[1])


@router.get("/", response_model=list[FeedRead])
def list_feeds(pagination: PaginationQuery, feeds: FeedServiceDep):
    return map(lambda feed: FeedRead.from_feed(feed), feeds.all(pagination))


@router.post("/", response_model=FeedRead, status_code=status.HTTP_201_CREATED)
def create_feed(feed: FeedCreate, feeds: FeedServiceDep):
    feed = feeds.create(feed)
    return FeedRead.from_feed(feed)


@router.get("/{feed_id}", response_model=FeedRead)
def get_feed(feed_id: int, feeds: FeedServiceDep):
    feed = feeds.get(feed_id)

    if feed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")

    return FeedRead.from_feed(feed)


@router.put("/{feed_id}", response_model=FeedRead)
def update_feed(feed_id: int, update: FeedUpdate, feeds: FeedServiceDep):
    feed = feeds.get(feed_id)

    if feed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")

    feed = feeds.update(feed, update)
    return FeedRead.from_feed(feed)


@router.patch("/{feed_id}", response_model=FeedRead)
def patch_feed(feed_id: int, patch: FeedPatch, feeds: FeedServiceDep):
    feed = feeds.get(feed_id)

    if feed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")

    feed = feeds.patch(feed, patch)
    return FeedRead.from_feed(feed)


@router.delete("/{feed_id}")
def delete_feed(feed_id: int, feeds: FeedServiceDep):
    feed = feeds.get(feed_id)

    if feed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")

    feeds.delete(feed)
    return {"ok": True}


@router.post("/{feed_id}/sync")
async def sync_feed(feed_id: int, feeds: FeedServiceDep):
    feed = feeds.get(feed_id)

    if feed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")

    await feeds.queue_sync(feed)
    return {"ok": True}


@router.post("/sync")
async def sync_feeds(feeds: FeedServiceDep):
    for feed in feeds.all():
        await feeds.queue_sync(feed)

    return {"ok": True}
