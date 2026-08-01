from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

# Circular import here, but since its only because of type checking, this is an acceptable solution
if TYPE_CHECKING:
    from ..feeds import Feed
from ..feed_group.model import FeedGroupLink


class FeedGroupBase(SQLModel):
    name: str = Field(min_length=1, max_length=50)


class FeedGroup(FeedGroupBase, table=True):
    __tablename__ = "group"

    id: int = Field(default=None, primary_key=True)

    feeds: list[Feed] = Relationship(
        back_populates="groups",
        link_model=FeedGroupLink,
        sa_relationship_kwargs={"passive_deletes": True},
    )
