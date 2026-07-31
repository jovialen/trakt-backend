from fastapi import APIRouter, HTTPException
from sqlmodel import select

from ..database import SessionDep
from ..utils import PaginationQuery, paginate
from .dto import FeedGroupCreate, FeedGroupUpdate
from .model import FeedGroup

router = APIRouter(
    prefix="/groups",
    tags=["Groups"],
)


@router.get("/new", response_model=FeedGroupCreate)
def new_group():
    return FeedGroupCreate(name="New Group")


@router.get("/", response_model=list[FeedGroup])
def get_groups(pagination: PaginationQuery, session: SessionDep):
    groups = session.exec(paginate(select(FeedGroup), pagination)).all()
    return groups


@router.post("/", response_model=FeedGroup)
def create_group(group: FeedGroupCreate, session: SessionDep):
    db_group = FeedGroup.model_validate(group)

    session.add(db_group)
    session.commit()
    session.refresh(db_group)

    return db_group


@router.get("/{group_id}", response_model=FeedGroup)
def get_group(group_id: int, session: SessionDep):
    group = session.get(FeedGroup, group_id)

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    return group


@router.put("/{group_id}", response_model=FeedGroup)
def update_group(group_id: int, group: FeedGroupUpdate, session: SessionDep):
    db_group = session.get(FeedGroup, group_id)

    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")

    updates = group.model_dump()
    for key, value in updates.values():
        setattr(db_group, key, value)

    session.add(db_group)
    session.commit()
    session.refresh(db_group)

    return db_group


@router.patch("/{group_id}", response_model=FeedGroup)
def patch_group(group_id: int, group: FeedGroupUpdate, session: SessionDep):
    db_group = session.get(FeedGroup, group_id)

    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")

    updates = group.model_dump(exclude_unset=True)
    for key, value in updates.values():
        setattr(db_group, key, value)

    session.add(db_group)
    session.commit()
    session.refresh(db_group)

    return db_group


@router.delete("/{group_id}", response_model=FeedGroup)
def delete_group(group_id: int, session: SessionDep):
    group = session.get(FeedGroup, group_id)

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    session.delete(group)
    session.commit()

    return {"ok": True}
