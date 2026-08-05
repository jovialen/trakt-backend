from logging import exception, info

from ..jobs import Job
from .service import FeedItemService


class FeedItemPullJob(Job):
    def __init__(self, item_id, items: FeedItemService):
        self.item_id = item_id
        self.items = items

    async def execute(self):
        info(f"Pulling item content for feed item {self.item_id}")

        item = self.items.get(self.item_id)

        if item is None:
            exception(f"Feed item {self.item_id} doesn't exist")
            return

        original_content = item.content
        item = await self.items.fetch_content(item)
        new_content = item.content

        if original_content != new_content:
            info(f"Feed item {self.item_id} updated with new content")
        else:
            info(f"Feed item {self.item_id} had no new content")
