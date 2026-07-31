from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from ..database import SessionDep
from ..utils import PaginationQuery, paginate
from .dto import FeedCreate, FeedPatch, FeedUpdate
from .model import Feed

router = APIRouter(prefix="/feeds", tags=["Feed"])


@router.get("/new", response_model=FeedCreate)
def new_feed():
    return Feed(name="New Feed", link="https://new.feed")


@router.get("/", response_model=list[Feed])
def get_routers(session: SessionDep, pagination: Annotated[PaginationQuery, Query()]):
    routers = session.exec(paginate(select(Feed), pagination)).all()
    return routers


@router.post("/", response_model=Feed)
def create_feed(session: SessionDep, feed: FeedCreate):
    db_feed = Feed.model_validate(feed)

    session.add(db_feed)
    session.commit()
    session.refresh(db_feed)

    return db_feed


@router.get("/{feed_id}", response_model=Feed)
def get_feed(feed_id: int, session: SessionDep):
    feed = session.get(Feed, feed_id)

    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    return feed


@router.put("/{feed_id}", response_model=Feed)
def update_feed(feed_id: int, session: SessionDep, feed: FeedUpdate):
    db_feed = session.get(Feed, feed_id)

    if not db_feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    updates = feed.model_dump()
    for key, value in updates.items():
        setattr(db_feed, key, value)

    session.add(db_feed)
    session.commit()
    session.refresh(db_feed)

    return db_feed


@router.patch("/{feed_id}", response_model=Feed)
def patch_feed(feed_id: int, session: SessionDep, patch: FeedPatch):
    db_feed = session.get(Feed, feed_id)

    if not db_feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    updates = patch.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(db_feed, key, value)

    session.add(db_feed)
    session.commit()
    session.refresh(db_feed)

    return db_feed


@router.delete("/{feed_id}")
def delete_feed(feed_id: int, session: SessionDep):
    feed = session.get(Feed, feed_id)

    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    session.delete(feed)
    session.commit()

    return {"ok": True}
