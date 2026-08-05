import pytest
from fastapi import Request
from sqlmodel import Session

from trakt_backend.feeds import Feed, FeedService, get_feed_service
from trakt_backend.groups import FeedGroup
from trakt_backend.jobs import JobsDep

from .factory import FeedFactory


@pytest.fixture
def feed_service(
    client,
    session: Session,
    jobs: JobsDep,
):
    mock_service = FeedService(
        session,
        jobs,
        Request(
            {
                "type": "http",
                "method": "GET",
                "path": "/",
                "headers": [],
            }
        ),
    )

    def override_get_feed_service():
        return mock_service

    client.app.dependency_overrides[get_feed_service] = override_get_feed_service

    yield mock_service


def add_feed(feed: Feed, session: Session):
    session.add(feed)
    session.commit()
    session.refresh(feed)

    return feed


@pytest.fixture
def nrk_feed(session: Session, news_group: FeedGroup):
    feed = FeedFactory.build(name="NRK", link="nrk.no/toppsaker.rss", groups=[news_group])
    return add_feed(feed, session)


@pytest.fixture
def google_feed(session: Session, news_group: FeedGroup):
    feed = FeedFactory.build(name="Google", link="google.com/not_real.rss", groups=[news_group])
    return add_feed(feed, session)


@pytest.fixture
def tekno_feed(session: Session, technology_group: FeedGroup):
    feed = FeedFactory.build(name="Tek.no", link="tek.no/feed.rss", groups=[technology_group])
    return add_feed(feed, session)


@pytest.fixture
def feed_batch(session: Session):
    feeds = FeedFactory.batch(40)

    session.add_all(feeds)
    session.commit()

    for feed in feeds:
        session.refresh(feed)

    return feeds
