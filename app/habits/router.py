from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth.router import get_current_active_profile

from app.habits.schemas.schemas import (
    HabitCreateSchema,
    HabitUpdateSchema,
    HabitInstanceCreateSchema,
    HabitStatus, HabitSchema,
)
from .schemas.responses import (
    HabitResponse,
    HabitListResponse,
    HabitInstanceResponse,
    DayStatsResponse,
    DayStatsListResponse,
    HabitHistoryResponse, HabitDeleteResponse, HabitCreateResponse
)
from .service import HabitService
from app.core.exceptions import NotFoundException
from app.profile.models import Profile


router = APIRouter()


@router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(
    habit_data: HabitCreateSchema,
    current_profile: Profile = Depends(get_current_active_profile),
    db: AsyncSession = Depends(get_db)
):
    """Создание новой привычки"""
    habit_service = HabitService(db)
    new_habit = await habit_service.add_one(habit_data, current_profile.id)
    return HabitCreateResponse(data=new_habit)


@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(
    habit_id: int,
    current_profile: Profile = Depends(get_current_active_profile),
    db: AsyncSession = Depends(get_db)
):
    """Получение одной привычки"""
    habit_service = HabitService(db)
    habit = await habit_service.get_one(habit_id, current_profile.id)
    if not habit:
        raise NotFoundException("Habit not found")
    return HabitResponse(data=habit)


@router.get("/", response_model=HabitListResponse)
async def get_habits(
    is_active: Optional[bool] = Query(None, description="Фильтр по активности привычек"),
    current_profile: Profile = Depends(get_current_active_profile),
    db: AsyncSession = Depends(get_db)
):
    """Получение всех привычек профиля"""
    habit_service = HabitService(db)
    habits = await habit_service.find_all(current_profile.id, is_active)
    return HabitListResponse(data=habits)


@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: int,
    habit_data: HabitUpdateSchema,
    current_profile: Profile = Depends(get_current_active_profile),
    db: AsyncSession = Depends(get_db)
):
    """Обновление привычки"""
    habit_service = HabitService(db)
    updated_habit = await habit_service.update_one(habit_id, habit_data, current_profile.id)
    if not updated_habit:
        raise NotFoundException("Habit not found")
    return HabitResponse(data=updated_habit)


@router.delete("/{habit_id}", response_model=HabitDeleteResponse)
async def delete_habit(
    habit_id: int,
    current_profile: Profile = Depends(get_current_active_profile),
    db: AsyncSession = Depends(get_db)
):
    """Удаление привычки"""
    habit_service = HabitService(db)
    deleted = await habit_service.delete_one(habit_id, current_profile.id)
    if not deleted:
        raise NotFoundException("Habit not found")
    return HabitDeleteResponse(deleted_habit_id=habit_id)


@router.get("/date/{target_date}", response_model=HabitListResponse)
async def get_habits_for_date(
    target_date: date,
    current_profile: Profile = Depends(get_current_active_profile),
    db: AsyncSession = Depends(get_db)
):
    """Получение привычек для конкретной даты (главный экран)"""
    habit_service = HabitService(db)
    habits = await habit_service.get_habits_for_date(current_profile.id, target_date)
    return HabitListResponse(data=habits)


@router.put("/{habit_id}/instance", response_model=HabitResponse)
async def mark_habit_instance(
        habit_id: int,
    payload: HabitInstanceCreateSchema,
    current_profile: Profile = Depends(get_current_active_profile),
        db: AsyncSession = Depends(get_db)
):
    """Отметка статуса привычки (выполнено/пропущено)"""
    try:
        habit_service = HabitService(db)
        await habit_service.mark_habit_instance(
            habit_id=habit_id,
            instance_date=payload.instance_date,
            status=payload.status,
            reason=payload.reason,
            profile_id=current_profile.id
        )
        habit = await habit_service.get_one(habit_id, current_profile.id)
        return HabitResponse(data=habit)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Habit not found")


@router.get("/stats/day/{target_date}", response_model=DayStatsResponse)
async def get_day_stats(
    target_date: date,
    current_profile: Profile = Depends(get_current_active_profile),
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики для конкретного дня"""
    habit_service = HabitService(db)
    stats = await habit_service.get_day_stats(current_profile.id, target_date)
    return DayStatsResponse(data=stats)


@router.get("/stats/calendar", response_model=DayStatsListResponse)
async def get_calendar_stats(
    start_date: date = Query(..., description="Начальная дата периода"),
    end_date: date = Query(..., description="Конечная дата периода"),
    current_profile: Profile = Depends(get_current_active_profile),
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики календаря за период"""
    habit_service = HabitService(db)
    stats = await habit_service.get_calendar_stats(current_profile.id, start_date, end_date)
    return DayStatsListResponse(data=stats)
