from datetime import datetime
from typing import List
from pydantic import BaseModel
from app.core.schema import SuccessResponse


class ProfileSchema(BaseModel):
    id: int
    user_type: str | None = None
    phone_number: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    email: str | None = None
    gender: bool | None = None
    created_date: datetime | None = None
    date_of_birth: datetime | None = None
    updated_date: datetime | None = None

    class Config:
        from_attributes = True


class ProfileCreateSchema(BaseModel):
    user_type: str
    phone_number: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    email: str | None = None
    gender: bool | None = None
    date_of_birth: datetime | None = None

    class Config:
        from_attributes = True


class ProfileResponse(SuccessResponse):
    data: ProfileSchema


class ProfileListResponse(SuccessResponse):
    data: List[ProfileSchema]
