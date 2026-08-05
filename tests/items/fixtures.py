import pytest
from sqlmodel import Session

from tests.items.factory import FeedItemFactory
from trakt_backend.feeds import Feed
from trakt_backend.items import FeedItem, FeedItemService


@pytest.fixture
def feed_item_service(session: Session, jobs):
    return FeedItemService(session, jobs)


def add_feed_item(item: FeedItem, session: Session):
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@pytest.fixture
def news_article(session: Session, nrk_feed: Feed):
    article = FeedItemFactory.build(feed=nrk_feed, read_at=None, read_later=False, saved_at=None)
    return add_feed_item(article, session)


@pytest.fixture
def tech_article(session: Session, tekno_feed: Feed):
    article = FeedItemFactory.build(feed=tekno_feed, read_at=None, read_later=False, saved_at=None)
    return add_feed_item(article, session)


@pytest.fixture
def google_article(session: Session, google_feed: Feed):
    article = FeedItemFactory.build(feed=google_feed, read_at=None, read_later=False, saved_at=None)
    return add_feed_item(article, session)


@pytest.fixture
def article_batch(session: Session, feed_batch: list[FeedItem]):
    articles = []

    for feed in feed_batch:
        articles += FeedItemFactory.batch(5, feed=feed)

    session.add_all(articles)
    session.commit()

    for article in articles:
        session.refresh(article)

    return articles
