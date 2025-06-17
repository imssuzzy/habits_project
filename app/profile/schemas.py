from datetime import datetime
from typing import List
from pydantic import BaseModel
from app.core.schema import SuccessResponse


class ProfileSchema(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None

    class Config:
        from_attributes = True


class ProfileCreateSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None

    class Config:
        from_attributes = True


class ProfileResponse(SuccessResponse):
    data: ProfileSchema


class ProfileListResponse(SuccessResponse):
    data: List[ProfileSchema]
