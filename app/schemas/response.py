from typing import Any, Optional

from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class APIErrorResponse(BaseModel):
    success: bool
    message: str
    error: dict | None = None