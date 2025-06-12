from pydantic import BaseModel
from datetime import date
from typing import Optional, List

class HabitCreateSchema(BaseModel):
    name: str
    duration_days: int
    days_of_week: List[str]
    start_date: date

class HabitSchema(HabitCreateSchema):
    id: int

    class Config:
        orm_mode = True

class HabitInstanceSchema(BaseModel):
    id: int
    habit_id: int
    date: date
    status: str
    class Config:
        orm_mode = True
