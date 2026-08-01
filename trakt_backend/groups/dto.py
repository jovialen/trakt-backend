from sqlmodel import Field, SQLModel

from .model import FeedGroupBase


class FeedGroupCreate(FeedGroupBase):
    pass


class FeedGroupUpdate(FeedGroupBase):
    pass


class FeedGroupPatch(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
