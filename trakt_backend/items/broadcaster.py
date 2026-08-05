import asyncio
from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from .model import FeedItem


class FeedItemBroadcaster:
    def __init__(self):
        self.subscribers: set[asyncio.Queue] = set()

    def has_subscribers(self) -> bool:
        return len(self.subscribers) > 0

    async def publish(self, item):
        for queue in list(self.subscribers):
            await queue.put(item)

    async def subscribe(self) -> AsyncGenerator[FeedItem]:
        queue: asyncio.Queue[FeedItem] = asyncio.Queue()
        self.subscribers.add(queue)

        try:
            while True:
                yield await queue.get()
        finally:
            self.subscribers.remove(queue)


async def stream_feed_items(broadcaster, items):
    async for item in broadcaster.subscribe():
        if items.contains(item):
            yield f"event: new_item\ndata: {item.model_dump_json()}\n\n"


@lru_cache
def get_feed_item_broadcaster():
    return FeedItemBroadcaster()


FeedItemBroadcasterDep = Annotated[FeedItemBroadcaster, Depends(get_feed_item_broadcaster)]
