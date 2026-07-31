from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Query, HTTPException
from sqlmodel import select, update, col

from ..database import SessionDep
from ..utils import paginate
from .model import FeedItem
from .dto import FeedItemQuery

router = APIRouter(
    prefix="/items",
    tags=["Feed items"],
)


@router.get("/", response_model=list[FeedItem])
def get_items(session: SessionDep, query: Annotated[FeedItemQuery, Query()]):
    db_query = select(FeedItem)

    if query.feed_id is not None:
        db_query = db_query.where(FeedItem.id == query.feed_id)

    if query.read_later is not None:
        db_query = db_query.where(FeedItem.read_later == query.read_later)

    if query.saved is not None:
        db_query = db_query.where(col(FeedItem.read_at).isnot(None))

    if query.unread is not None:
        db_query = db_query.where(col(FeedItem.read_at).isnot(None))

    items = session.exec(paginate(db_query, query)).all()
    return items


@router.get("/{item_id}", response_model=FeedItem)
def get_item(item_id: int, session: SessionDep):
    item = session.get(FeedItem, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


@router.post("/{item_id}/read", response_model=FeedItem)
def read_item(item_id: int, session: SessionDep):
    item = session.get(FeedItem, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.read_later = False
    item.read_at = datetime.now()

    session.add(item)
    session.commit()
    session.refresh(item)

    return item


@router.post("/{item_id}/read_later", response_model=FeedItem)
def read_item_later(item_id: int, session: SessionDep):
    item = session.get(FeedItem, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.read_later = True


@router.post("/{item_id}/save", response_model=FeedItem)
def save_item(item_id: int, session: SessionDep):
    item = session.get(FeedItem, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.saved_at = datetime.now()
    session.add(item)
    session.commit()
    session.refresh(item)

    return item


@router.post("/read", response_model=list[FeedItem])
def bulk_read_items(item_ids: list[str], session: SessionDep):
    if not item_ids:
        return []

    items = session.exec(
        update(FeedItem)
        .where(col(FeedItem.id).in_(item_ids))
        .values(read_at=datetime.now(), read_later=False)
    ).all()
    session.commit()

    return items


@router.post("/read_later", response_model=list[FeedItem])
def bulk_read_items_later(item_ids: list[str], session: SessionDep):
    if not item_ids:
        return []

    items = session.exec(
        update(FeedItem)
        .where(col(FeedItem.id).in_(item_ids))
        .values(read_later=True)
    ).all()
    session.commit()

    return items


@router.post("/save", response_model=list[FeedItem])
def bulk_save_items(item_ids: list[str], session: SessionDep):
    if not item_ids:
        return []

    items = session.exec(
        update(FeedItem)
        .where(col(FeedItem.id).in_(item_ids))
        .values(saved_at=datetime.now())
    ).all()
    session.commit()

    return items