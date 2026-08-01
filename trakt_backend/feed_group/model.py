from sqlmodel import Field, SQLModel


class FeedGroupLink(SQLModel, table=True):
    __tablename__ = "feed_group"

    feed_id: int | None = Field(
        default=None, foreign_key="feed.id", primary_key=True, ondelete="CASCADE"
    )

    group_id: int | None = Field(
        default=None, foreign_key="group.id", primary_key=True, ondelete="CASCADE"
    )
