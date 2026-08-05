from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.sse import EventSourceResponse

from .broadcaster import FeedItemBroadcasterDep
from .dto import FeedItemQuery
from .model import FeedItem
from .service import FeedItemServiceDep

router = APIRouter(
    prefix="/items",
    tags=["Feed items"],
)


@router.get("/", response_model=list[FeedItem])
def list_items(query: Annotated[FeedItemQuery, Depends()], items: FeedItemServiceDep):
    return items.all(query)


@router.get("/stream")
async def stream_items(broadcaster: FeedItemBroadcasterDep, items: FeedItemServiceDep):
    async def events():
        async for item in broadcaster.subscribe():
            if not items.contains(item):
                continue

            yield f"event: new_item\ndata: {item.model_dump_json()}\n\n"

    return EventSourceResponse(events(), status_code=status.HTTP_200_OK)


@router.get("/{item_id}", response_model=FeedItem)
def get_item(item_id: str, items: FeedItemServiceDep):
    item = items.get(item_id)

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    return item


@router.post("/{item_id}/read", response_model=FeedItem)
def read_item(item_id: str, items: FeedItemServiceDep):
    item = items.get(item_id)

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    return items.mark_read(item)


@router.post("/{item_id}/read_later", response_model=FeedItem)
def read_item_later(item_id: str, items: FeedItemServiceDep):
    item = items.get(item_id)

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    return items.read_later(item)


@router.post("/{item_id}/save", response_model=FeedItem)
def save_item(item_id: str, items: FeedItemServiceDep):
    item = items.get(item_id)

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    return items.save(item)


@router.post("/read", response_model=list[FeedItem])
def bulk_read_items(item_ids: list[str], items: FeedItemServiceDep):
    return items.bulk_mark_read(item_ids)


@router.post("/read_later", response_model=list[FeedItem])
def bulk_read_items_later(item_ids: list[str], items: FeedItemServiceDep):
    return items.bulk_read_later(item_ids)


@router.post("/save", response_model=list[FeedItem])
def bulk_save_items(item_ids: list[str], items: FeedItemServiceDep):
    return items.bulk_save(item_ids)
