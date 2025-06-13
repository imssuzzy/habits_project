from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

from app.habits.schemas.schemas import (
    HabitCreateSchema,
    HabitSchema,
    HabitInstanceSchema,
)
from .schemas.responses import HabitResponse, HabitListResponse
from .service import HabitService
from ..core.exceptions import NotFoundException

router = APIRouter()


@router.post("/", response_model=HabitSchema, status_code=status.HTTP_201_CREATED)
async def create_habit(
    habit_data: HabitCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    habit_service = HabitService(db)
    new_habit = await habit_service.add_one(habit_data.model_dump())
    return HabitResponse(data=new_habit)


@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(
    habit_id: int,
    db: AsyncSession = Depends(get_db)
):
    habit_service = HabitService(db)
    habit = await habit_service.get_one(habit_id)
    if not habit:
        raise NotFoundException("Habit not found")
    return HabitResponse(data=habit)


@router.get("/", response_model=HabitListResponse)
async def get_habits(db: AsyncSession = Depends(get_db)):
    habit_service = HabitService(db)
    habits = await habit_service.find_all()
    return HabitListResponse(data=habits)


@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: int,
    habit_data: HabitCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    habit_service = HabitService(db)
    updated_habit = await habit_service.update_one(habit_id, habit_data.model_dump())
    if not updated_habit:
        raise NotFoundException("Habit not found")
    return HabitResponse(data=updated_habit)


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    habit_id: int,
    db: AsyncSession = Depends(get_db)
):
    habit_service = HabitService(db)
    deleted = await habit_service.delete_one(habit_id)
    if not deleted:
        raise NotFoundException("Habit not found")
    return
