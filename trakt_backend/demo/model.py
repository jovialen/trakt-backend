from sqlmodel import SQLModel, Field


class Movie(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None, default_factory=None)
    title: str = Field(min_length=1, max_length=100, description="Movie title")
