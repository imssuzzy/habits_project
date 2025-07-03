from datetime import datetime
from typing import List
from pydantic import BaseModel, EmailStr
from apps.core.schema import SuccessResponse


class ProfileSchema(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None

    class Config:
        from_attributes = True


class ProfileCreateSchema(BaseModel):
    login: str
    password: str
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None

    class Config:
        from_attributes = True


class ProfileResponse(SuccessResponse):
    data: ProfileSchema


class ProfileListResponse(SuccessResponse):
    data: List[ProfileSchema]
