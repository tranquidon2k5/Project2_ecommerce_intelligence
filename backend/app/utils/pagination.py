from typing import TypeVar, Generic, List
from pydantic import BaseModel


T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int


def paginate(total: int, page: int, per_page: int) -> PaginationMeta:
    total_pages = (total + per_page - 1) // per_page
    return PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
    )
