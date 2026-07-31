from pydantic import BaseModel, Field


class PaginationQuery(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, gt=0)


def paginate(select, pagination: PaginationQuery):
    return select.offset(pagination.offset).limit(pagination.limit)
