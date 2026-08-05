import asyncio
from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel

from .model import FeedItem


class FeedItemBroadcastEvent(BaseModel):
    event_type: str
    item: FeedItem


class FeedItemBroadcaster:
    def __init__(self):
        self.subscribers: set[asyncio.Queue] = set()

    def has_subscribers(self) -> bool:
        return len(self.subscribers) > 0

    async def new_item(self, item: FeedItem):
        await self._publish("new_item", item)

    async def updated_item(self, item: FeedItem):
        await self._publish("updated_item", item)

    async def read_item(self, item: FeedItem):
        await self._publish("read_item", item)

    async def _publish(self, event_type, item):
        for queue in list(self.subscribers):
            await queue.put(FeedItemBroadcastEvent(event_type=event_type, item=item))

    async def subscribe(self) -> AsyncGenerator[FeedItemBroadcastEvent]:
        queue: asyncio.Queue[FeedItemBroadcastEvent] = asyncio.Queue()
        self.subscribers.add(queue)

        try:
            while True:
                yield await queue.get()
        finally:
            self.subscribers.remove(queue)


async def stream_feed_items(broadcaster, items):
    async for event in broadcaster.subscribe():
        if items.contains(event.item):
            yield f"event: {event.event_type}\ndata: {event.item.model_dump_json()}\n\n"


@lru_cache
def get_feed_item_broadcaster():
    return FeedItemBroadcaster()


FeedItemBroadcasterDep = Annotated[FeedItemBroadcaster, Depends(get_feed_item_broadcaster)]
