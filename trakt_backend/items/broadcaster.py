import asyncio
from collections import deque
from collections.abc import AsyncGenerator
from functools import lru_cache
from logging import debug, info
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel

from .model import FeedItem


class FeedItemBroadcastEvent(BaseModel):
    id: int
    event_type: str
    item: FeedItem


class FeedItemBroadcaster:
    def __init__(self, history_size: int = 1000):
        self.subscribers: set[asyncio.Queue] = set()
        self.history: deque[FeedItemBroadcastEvent] = deque(maxlen=history_size)
        self.next_id = 1

    def has_subscribers(self) -> bool:
        return len(self.subscribers) > 0

    async def new_item(self, item: FeedItem):
        await self._publish("new_item", item)

    async def updated_item(self, item: FeedItem):
        await self._publish("updated_item", item)

    async def read_item(self, item: FeedItem):
        await self._publish("read_item", item)

    async def _publish(self, event_type: str, item: FeedItem):
        debug(f"Broadcasting {event_type} for feed item {item.id}")

        event = FeedItemBroadcastEvent(
            id=self.next_id,
            event_type=event_type,
            item=FeedItem.model_validate(item, from_attributes=True),
        )

        self.next_id += 1
        self.history.append(event)

        for queue in list(self.subscribers):
            await queue.put(event)

    async def subscribe(
        self,
        last_event_id: int | None = None,
    ) -> AsyncGenerator[FeedItemBroadcastEvent]:
        queue: asyncio.Queue[FeedItemBroadcastEvent] = asyncio.Queue()

        self.subscribers.add(queue)

        if last_event_id is None:
            info("New subscriber to feed item events")
        else:
            info(f"Old subscriber resubscribed to feed item events. Last event id: {last_event_id}")

        try:
            # Replay missed events
            if last_event_id is not None:
                for event in self.history:
                    if event.id > last_event_id:
                        yield event

            # Continue live events
            while True:
                yield await queue.get()

        finally:
            info("A feed item event subscriber has unsubscribed")
            self.subscribers.remove(queue)


async def stream_feed_items(broadcaster, items, last_event_id=None):
    try:
        yield ": connected\n\n"

        async for event in broadcaster.subscribe(last_event_id):
            if items.contains(event.item):
                yield (
                    f"id: {event.id}\n"
                    f"event: {event.event_type}\n"
                    f"data: {event.item.model_dump_json()}\n\n"
                )
    except asyncio.CancelledError:
        debug("stream_feed_items cancelled")
        raise
    finally:
        debug("stream_feed_items finished")


@lru_cache
def get_feed_item_broadcaster():
    return FeedItemBroadcaster()


FeedItemBroadcasterDep = Annotated[FeedItemBroadcaster, Depends(get_feed_item_broadcaster)]
