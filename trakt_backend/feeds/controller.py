from fastapi import APIRouter, HTTPException
from sqlmodel import select

from ..database import SessionDep
from ..utils import PaginationQuery, paginate
from .dto import FeedCreate, FeedPatch, FeedRead, FeedUpdate
from .model import Feed

router = APIRouter(prefix="/feeds", tags=["Feed"])


@router.get("/new", response_model=FeedCreate)
def new_feed():
    return Feed(name="New Feed", link="https://new.feed")


@router.get("/", response_model=list[FeedRead])
def get_feeds(session: SessionDep, pagination: PaginationQuery):
    feeds = session.exec(paginate(select(Feed), pagination)).all()
    return list(
        map(
            lambda feed: FeedRead(
                **feed.model_dump(),
                groups=[group.id for group in feed.groups],
            ),
            feeds,
        )
    )


@router.post("/", response_model=Feed)
def create_feed(session: SessionDep, feed: FeedCreate):
    db_feed = Feed.model_validate(feed)

    session.add(db_feed)
    session.commit()
    session.refresh(db_feed)

    return db_feed


@router.get("/{feed_id}", response_model=FeedRead)
def get_feed(feed_id: int, session: SessionDep):
    feed = session.get(Feed, feed_id)

    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    return FeedRead(**feed.model_dump(), groups=[group.id for group in feed.groups])


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
