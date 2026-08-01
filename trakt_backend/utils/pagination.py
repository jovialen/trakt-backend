from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, Field


class Pagination(BaseModel):
    limit: int = Field(100, ge=0, le=100)
    offset: int = Field(0, ge=0)

    def query(self, query):
        return paginate(query, self)


PaginationQuery = Annotated[Pagination, Query()]


def paginate(select, pagination: PaginationQuery):
    return select.offset(pagination.offset).limit(pagination.limit)
