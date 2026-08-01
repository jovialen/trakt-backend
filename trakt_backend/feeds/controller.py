from fastapi import APIRouter, HTTPException
from sqlalchemy import delete
from sqlmodel import select

from ..database import SessionDep
from ..feed_group import FeedGroupLink
from ..utils import PaginationQuery, paginate
from .dto import FeedCreate, FeedPatch, FeedRead, FeedUpdate
from .model import Feed

router = APIRouter(prefix="/feeds", tags=["Feed"])


@router.get("/new", response_model=FeedCreate)
def new_feed():
    return FeedCreate(name="New Feed", link="https://new.feed", groups=[1])


@router.get("/", response_model=list[FeedRead])
def get_feeds(session: SessionDep, pagination: PaginationQuery):
    feeds = session.exec(paginate(select(Feed), pagination)).all()
    return list(map(lambda feed: FeedRead.from_feed(feed), feeds))


@router.post("/", response_model=FeedRead)
def create_feed(session: SessionDep, feed: FeedCreate):
    db_feed = Feed.model_validate(feed.model_dump(exclude={"groups"}))

    session.add(db_feed)
    session.flush()
    session.refresh(db_feed)

    for group_id in feed.groups:
        session.add(FeedGroupLink(feed_id=db_feed.id, group_id=group_id))

    session.commit()
    db_feed = session.get(Feed, db_feed.id)

    return FeedRead.from_feed(db_feed)


@router.get("/{feed_id}", response_model=FeedRead)
def get_feed(feed_id: int, session: SessionDep):
    feed = session.get(Feed, feed_id)

    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    return FeedRead.from_feed(feed)


@router.put("/{feed_id}", response_model=FeedRead)
def update_feed(feed_id: int, session: SessionDep, feed: FeedUpdate):
    db_feed = session.get(Feed, feed_id)

    if not db_feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    updates = feed.model_dump(exclude={"groups"})
    for key, value in updates.items():
        setattr(db_feed, key, value)

    session.exec(delete(FeedGroupLink).where(FeedGroupLink.feed_id == feed_id))

    for group_id in feed.groups:
        session.add(FeedGroupLink(feed_id=feed_id, group_id=group_id))

    session.add(db_feed)
    session.commit()
    db_feed = session.get(Feed, db_feed.id)

    return FeedRead.from_feed(db_feed)


@router.patch("/{feed_id}", response_model=FeedRead)
def patch_feed(feed_id: int, session: SessionDep, patch: FeedPatch):
    db_feed = session.get(Feed, feed_id)

    if not db_feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    updates = patch.model_dump(exclude_unset=True, exclude={"groups"})
    for key, value in updates.items():
        setattr(db_feed, key, value)

    if patch.groups is not None:
        session.exec(delete(FeedGroupLink).where(FeedGroupLink.feed_id == feed_id))

        for group_id in patch.groups:
            session.add(FeedGroupLink(feed_id=feed_id, group_id=group_id))

    session.add(db_feed)
    session.commit()

    db_feed = session.get(Feed, db_feed.id)

    return FeedRead.from_feed(db_feed)


@router.delete("/{feed_id}")
def delete_feed(feed_id: int, session: SessionDep):
    feed = session.get(Feed, feed_id)

    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    session.delete(feed)
    session.commit()

    return {"ok": True}
