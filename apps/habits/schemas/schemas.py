from enum import Enum
from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Optional, List


class HabitStatus(str, Enum):
    done = "done"
    skipped = "skipped"
    pending = "pending"
    deleted = "deleted"


class HabitCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Название привычки")
    description: Optional[str] = Field(None, max_length=1000, description="Описание привычки")
    duration_days: int = Field(..., gt=0, le=365, description="Длительность привычки в днях")
    days_of_week: List[str] = Field(..., description="Дни недели (0-6, где 0=Понедельник)")
    start_date: date = Field(..., description="Дата начала привычки")

    class Config:
        from_attributes = True


class HabitUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    duration_days: Optional[int] = Field(None, gt=0, le=365)
    days_of_week: Optional[List[str]] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class HabitSchema(HabitCreateSchema):
    id: int
    end_date: Optional[date] = None
    is_active: bool
    profile_id: int
    created_at: datetime
    updated_at: datetime
    habit_status: Optional[str] = None

    class Config:
        from_attributes = True


class HabitInstanceCreateSchema(BaseModel):
    instance_date: date = Field(..., description="Дата экземпляра привычки")
    status: HabitStatus = Field(..., description="Статус привычки")
    reason: Optional[str] = Field(None, max_length=500, description="Причина пропуска или удаления")

    class Config:
        from_attributes = True


class HabitInstanceSchema(BaseModel):
    id: int
    habit_id: int
    instance_date: date = Field(alias="date")
    status: HabitStatus
    reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


    class Config:
        from_attributes = True


class HabitWithInstancesSchema(HabitSchema):
    instances: List[HabitInstanceSchema] = []

    class Config:
        from_attributes = True


class DayStatsSchema(BaseModel):
    instance_date: date = Field(alias="date")
    total_habits: int
    completed_habits: int
    skipped_habits: int
    pending_habits: int
    completion_percentage: float
    color_intensity: str  

    class Config:
        from_attributes = True


class HabitHistorySchema(BaseModel):
    habit_id: int
    habit_name: str
    instance_date: date
    status: HabitStatus
    reason: Optional[str] = None

    class Config:
        from_attributes = True
