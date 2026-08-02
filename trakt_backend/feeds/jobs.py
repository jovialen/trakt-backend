from logging import debug, info

import feedparser
from database import engine
from sqlmodel import Session

from ..jobs import Job
from .model import Feed


class FeedSyncJob(Job):
    def __init__(self, feed: Feed):
        self.feed = feed

    def execute(self):
        from ..items import FeedItem

        info(f"Starting sync job for feed {self.feed.id} ({self.feed.name})")

        rss = feedparser.parse(self.feed.link)

        new_items = []
        for entry in rss.entries:
            item = FeedItem(feed_id=self.feed.id).import_from_parsed(entry)

            debug(f"Fetched entry {item.id} from feed {self.feed.id}")

            # This does not discover if items get changed, but that is acceptable for now
            # In the future, a possible fix to this might be to check if the published_at
            # or updated_at has been moved forward
            if item.id not in [item.id for item in self.feed.items]:
                debug(f"Item {item.id} is new. Adding item to feed {self.feed.id}")
                new_items.append(item)

        with Session(engine) as session:
            session.add_all(new_items)
            session.commit()
