from fastapi import APIRouter

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
    return feeds.all(pagination)


@router.post("/", response_model=FeedRead)
def create_feed(feed: FeedCreate, feeds: FeedServiceDep):
    return feeds.create(feed)


@router.get("/{feed_id}", response_model=FeedRead)
def get_feed(feed_id: int, feeds: FeedServiceDep):
    return feeds.get(feed_id)


@router.put("/{feed_id}", response_model=FeedRead)
def update_feed(feed_id: int, feed: FeedUpdate, feeds: FeedServiceDep):
    return feeds.update(feed_id, feed)


@router.patch("/{feed_id}", response_model=FeedRead)
def patch_feed(feed_id: int, patch: FeedPatch, feeds: FeedServiceDep):
    return feeds.patch(feed_id, patch)


@router.delete("/{feed_id}")
def delete_feed(feed_id: int, feeds: FeedServiceDep):
    return feeds.delete(feed_id)
