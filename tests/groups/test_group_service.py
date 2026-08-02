import pytest
from fastapi import HTTPException

from trakt_backend.feeds import Feed
from trakt_backend.groups import (
    FeedGroup,
    FeedGroupCreate,
    FeedGroupPatch,
    FeedGroupService,
    FeedGroupUpdate,
)


def test_list_groups(group_service: FeedGroupService, group_batch: list[FeedGroup]):
    groups = group_service.all()

    assert len(groups) == len(group_batch)
    assert groups[0].id is not None


def test_create_group(group_service: FeedGroupService):
    group = FeedGroupCreate(name="New group")

    created = group_service.create(group)

    assert created.id is not None
    assert created.name == "New group"


def test_get_group(group_service: FeedGroupService, news_group: FeedGroup):
    group = group_service.get(news_group.id)

    assert group.id == news_group.id
    assert group.name == "News"


def test_get_missing_group(group_service: FeedGroupService):
    with pytest.raises(HTTPException) as exc_info:
        group_service.get(99999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Group not found"


def test_update_group(group_service: FeedGroupService, news_group: FeedGroup):
    update = FeedGroupUpdate(name="Updated news_group")

    updated = group_service.update(news_group.id, update)

    assert updated.name == "Updated news_group"


def test_update_missing_group(group_service: FeedGroupService):
    update = FeedGroupUpdate(name="Missing")

    with pytest.raises(HTTPException) as exc_info:
        group_service.update(99999, update)

    assert exc_info.value.status_code == 404


def test_patch_group(group_service: FeedGroupService, news_group: FeedGroup):
    patch = FeedGroupPatch(name="Patched news_group")

    updated = group_service.patch(news_group.id, patch)

    assert updated.name == "Patched news_group"


def test_patch_missing_group(group_service: FeedGroupService):
    patch = FeedGroupPatch(name="Missing")

    with pytest.raises(HTTPException) as exc_info:
        group_service.patch(99999, patch)

    assert exc_info.value.status_code == 404


def test_delete_group(group_service: FeedGroupService, news_group: FeedGroup):
    result = group_service.delete(news_group.id)

    assert result == {"ok": True}

    with pytest.raises(HTTPException):
        group_service.get(news_group.id)


def test_delete_missing_group(group_service: FeedGroupService):
    with pytest.raises(HTTPException) as exc_info:
        group_service.delete(99999)

    assert exc_info.value.status_code == 404


def test_add_feed(
    group_service: FeedGroupService,
    blogs_group,
    nrk_feed: Feed,
):
    group_service.add_feed(blogs_group, nrk_feed)

    feeds = group_service.get_feeds(blogs_group)

    assert len(feeds) == 1
    assert nrk_feed.id in [feed.id for feed in feeds]


def test_remove_feed(
    group_service: FeedGroupService,
    news_group: FeedGroup,
    nrk_feed: Feed,
):
    group_service.remove_feed(news_group, nrk_feed)

    feeds = group_service.get_feeds(news_group)

    assert nrk_feed.id not in [feed.id for feed in feeds]


def test_remove_missing_feed_from_group(
    group_service: FeedGroupService,
    technology_group: FeedGroup,
    nrk_feed: Feed,
):
    with pytest.raises(HTTPException) as exc_info:
        group_service.remove_feed(technology_group, nrk_feed)

    assert exc_info.value.status_code == 404
