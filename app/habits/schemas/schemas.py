from enum import Enum

from pydantic import BaseModel
from datetime import date
from typing import Optional, List

class HabitStatus(str, Enum):
    done = "DONE"
    skipped = "SKIPPED"
    pending = "PENDING"

class HabitCreateSchema(BaseModel):
    name: str
    duration_days: int
    days_of_week: list[str]
    start_date: date

    class Config:
        from_attributes = True

class HabitSchema(HabitCreateSchema):
    id: int
    habit_status: Optional[str] = None

    class Config:
        from_attributes = True

class HabitInstanceSchema(BaseModel):
    date: date
    status: str

    class Config:
        from_attributes = True
