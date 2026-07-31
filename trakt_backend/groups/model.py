from sqlmodel import Field, SQLModel


class FeedGroupBase(SQLModel):
    name: str = Field(min_length=1, max_length=50)


class FeedGroup(FeedGroupBase, table=True):
    id: int = Field(default=None, primary_key=True)
