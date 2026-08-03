from logging import info

from ..jobs import Job
from . import FeedService


class FeedSyncJob(Job):
    def __init__(self, feed_id: int, feeds: FeedService):
        self.feed_id = feed_id
        self.feeds = feeds

    def execute(self):
        info(f"Starting sync job for feed {self.feed_id}")

        feed = self.feeds.get(self.feed_id)
        self.feeds.sync(feed)
