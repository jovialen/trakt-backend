from fastapi import APIRouter

from .. import items
from ..feeds import Feed, FeedServiceDep
from ..utils import PaginationQuery
from .dto import FeedGroupCreate, FeedGroupUpdate
from .model import FeedGroup
from .service import FeedGroupServiceDep

router = APIRouter(
    prefix="/groups",
    tags=["Feed groups"],
)

router.include_router(items.router, prefix="/{group_id}", tags=["Feed groups"])


@router.get("/new", response_model=FeedGroupCreate)
def new_group():
    return FeedGroupCreate(name="New Group")


@router.get("/", response_model=list[FeedGroup])
def list_groups(pagination: PaginationQuery, groups: FeedGroupServiceDep):
    return groups.all(pagination)


@router.post("/", response_model=FeedGroup)
def create_group(group: FeedGroupCreate, groups: FeedGroupServiceDep):
    return groups.create(group)


@router.get("/{group_id}", response_model=FeedGroup)
def get_group(group_id: int, groups: FeedGroupServiceDep):
    return groups.get(group_id)


@router.put("/{group_id}", response_model=FeedGroup)
def update_group(group_id: int, group: FeedGroupUpdate, groups: FeedGroupServiceDep):
    return groups.update(group_id, group)


@router.patch("/{group_id}", response_model=FeedGroup)
def patch_group(group_id: int, group: FeedGroupUpdate, groups: FeedGroupServiceDep):
    return groups.patch(group_id, group)


@router.delete("/{group_id}", response_model=FeedGroup)
def delete_group(group_id: int, groups: FeedGroupServiceDep):
    return groups.delete(group_id)


@router.get("/{group_id}/feeds", response_model=list[Feed])
def get_group_feeds(group_id: int, groups: FeedGroupServiceDep):
    group = groups.get(group_id)
    return groups.get_feeds(group)


@router.put("/{group_id}/feeds/{feed_id}", response_model=Feed)
def add_feed_to_group(
    group_id: int, feed_id: int, groups: FeedGroupServiceDep, feeds: FeedServiceDep
):
    group = groups.get(group_id)
    feed = feeds.get(feed_id)
    groups.add_feed(group, feed)
    return groups.get_feeds(group)


@router.delete("/{group_id}/feeds/{feed_id}", response_model=Feed)
def remove_feed_from_group(
    group_id: int, feed_id: int, groups: FeedGroupServiceDep, feeds: FeedServiceDep
):
    group = groups.get(group_id)
    feed = feeds.get(feed_id)
    groups.remove_feed(group, feed)
    return groups.get_feeds(group)
