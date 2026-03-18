from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel


T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int


class BaseResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    meta: Optional[PaginationMeta] = None
    message: Optional[str] = None

    model_config = {"from_attributes": True}


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    data: None = None
    error: ErrorDetail
