from typing import List, Any, Dict, Union, Optional
from pydantic import BaseModel


class Pagination(BaseModel):
    total: int
    per_page: int
    current_page: int
    last_page: int


class SuccessResponse(BaseModel):
    status: str = "success"
    pagination: Pagination | None = None
    message: str = ""


class ErrorDetails(BaseModel):
    field: Optional[str] = None
    issue: Optional[str] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    error: Dict[str, Any] = {
        "code": str,
        "message": str,
        "details": Optional[List[ErrorDetails]]
    }
