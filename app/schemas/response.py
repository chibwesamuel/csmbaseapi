from typing import Any, Optional

from pydantic import BaseModel


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    meta: Optional[PaginationMeta] = None


class APIErrorResponse(BaseModel):
    success: bool
    message: str
    errors: Optional[Any] = None