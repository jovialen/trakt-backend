import pytest
from sqlmodel import Session

from trakt_backend.groups import FeedGroup, FeedGroupService

from .factory import FeedGroupFactory


@pytest.fixture
def group_service(session: Session):
    return FeedGroupService(session)


def add_group(group: FeedGroup, session: Session):
    session.add(group)
    session.commit()
    session.refresh(group)

    return group


@pytest.fixture
def news_group(session: Session):
    group = FeedGroupFactory.build(name="News")
    return add_group(group, session)


@pytest.fixture
def technology_group(session: Session):
    group = FeedGroupFactory.build(name="Technology")
    return add_group(group, session)


@pytest.fixture
def blogs_group(session: Session):
    group = FeedGroupFactory.build(name="Blogs")
    return add_group(group, session)


@pytest.fixture
def group_batch(session: Session):
    groups = FeedGroupFactory.batch(40)

    session.add_all(groups)
    session.commit()

    for group in groups:
        session.refresh(group)

    return groups
