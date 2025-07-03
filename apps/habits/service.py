from datetime import date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, and_, func

from apps.habits.schemas.schemas import (
    HabitSchema, 
    HabitCreateSchema, 
    HabitUpdateSchema,
    HabitInstanceCreateSchema,
    HabitInstanceSchema,
    DayStatsSchema,
    HabitHistorySchema
)
from apps.habits.models import Habit, HabitInstance, HabitStatus
from typing import List, Optional
from apps.core.exceptions import NotFoundException
from fastapi import HTTPException
class HabitService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_one(self, data: HabitCreateSchema, profile_id: int) -> HabitSchema:
        """Создание новой привычки"""
        habit = Habit(
            name=data.name,
            description=data.description,
            duration_days=data.duration_days,
            days_of_week=data.days_of_week,
            start_date=data.start_date,
            end_date=data.start_date + timedelta(days=data.duration_days - 1),
            profile_id=profile_id
        )
        self.db.add(habit)
        await self.db.commit()
        await self.db.refresh(habit)
        
        # Создаем экземпляры привычки для всех запланированных дней
        await self._create_habit_instances(habit)
        
        return HabitSchema.from_orm(habit)

    async def _create_habit_instances(self, habit: Habit) -> None:
        """Создание экземпляров привычки для всех запланированных дней"""
        current_date = habit.start_date
        end_date = habit.end_date or (habit.start_date + timedelta(days=habit.duration_days - 1))
        
        while current_date <= end_date:
            weekday = str(current_date.weekday())
            if weekday in habit.days_of_week:
                instance = HabitInstance(
                    habit_id=habit.id,
                    date=current_date,
                    status=HabitStatus.pending
                )
                self.db.add(instance)
            current_date += timedelta(days=1)
        
        await self.db.commit()

    async def get_one(self, habit_id: int, profile_id: int) -> Optional[HabitSchema]:
        """Получение одной привычки"""
        result = await self.db.execute(
            select(Habit).where(
                and_(Habit.id == habit_id, Habit.profile_id == profile_id)
            )
        )
        habit = result.scalar_one_or_none()
        if not habit:
            return None
        
        instance_result = await self.db.execute(
            select(HabitInstance)
            .where(HabitInstance.habit_id == habit_id)
            .order_by(HabitInstance.date.desc())
            .limit(1)
        )
        instance = instance_result.scalar_one_or_none()
        
        habit_dict = HabitSchema.from_orm(habit).dict()
        if instance:
            habit_dict['habit_status'] = instance.status.value
        
        return HabitSchema(**habit_dict)

    async def find_all(self, profile_id: int, is_active: Optional[bool] = None) -> List[HabitSchema]:
        """Получение всех привычек профиля"""
        query = select(Habit).where(Habit.profile_id == profile_id)
        if is_active is not None:
            query = query.where(Habit.is_active == is_active)
        
        result = await self.db.execute(query)
        habits = result.scalars().all()
        
        habits_with_status = []
        for habit in habits:
            instance_result = await self.db.execute(
                select(HabitInstance)
                .where(HabitInstance.habit_id == habit.id)
                .order_by(HabitInstance.date.desc())
                .limit(1)
            )
            instance = instance_result.scalar_one_or_none()
            
            habit_dict = HabitSchema.from_orm(habit).dict()
            if instance:
                habit_dict['habit_status'] = instance.status.value
            
            habits_with_status.append(HabitSchema(**habit_dict))
        return habits_with_status

    async def update_one(self, habit_id: int, data: HabitUpdateSchema, profile_id: int) -> Optional[HabitSchema]:
        """Обновление привычки"""
        habit = await self.get_one(habit_id, profile_id)
        if not habit:
            return None
        update_data = data.dict(exclude_unset=True)
        if update_data:
            stmt = (
            update(Habit)
                .where(and_(Habit.id == habit_id, Habit.profile_id == profile_id))
                .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(stmt)
        await self.db.commit()
        return await self.get_one(habit_id, profile_id)

    async def delete_one(self, habit_id: int, profile_id: int) -> bool:
        """Удаление привычки"""
        stmt = delete(Habit).where(
            and_(Habit.id == habit_id, Habit.profile_id == profile_id)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def get_habits_for_date(self, profile_id: int, target_date: date) -> List[HabitSchema]:
        """Получение привычек для конкретной даты"""
        weekday = str(target_date.weekday())
        stmt = select(Habit).where(
            and_(
                Habit.profile_id == profile_id,
                Habit.is_active == True,
                Habit.start_date <= target_date,
                Habit.end_date >= target_date,
                Habit.days_of_week.contains([weekday])
            )
        )
        result = await self.db.execute(stmt)
        habits = result.scalars().all()
        habits_with_instances = []
        for habit in habits:
            instance_result = await self.db.execute(
                select(HabitInstance).where(
                    and_(
                        HabitInstance.habit_id == habit.id,
                        HabitInstance.date == target_date
                    )
                )
            )
            instance = instance_result.scalar_one_or_none()
            habit_dict = HabitSchema.from_orm(habit).dict()
            if instance:
                habit_dict['habit_status'] = instance.status.value
            else:
                habit_dict['habit_status'] = HabitStatus.pending.value
            habits_with_instances.append(HabitSchema(**habit_dict))
        return habits_with_instances

    async def mark_habit_instance(
        self,
            habit_id: int,
            instance_date: date,
            status: HabitStatus,
        reason: Optional[str] = None,
        profile_id: int = None
    ) -> HabitInstance:
        """Отметка статуса привычки на конкретную дату"""
        if profile_id:
            habit = await self.get_one(habit_id, profile_id)
        if not habit:
                raise NotFoundException("Habit not found")
        instance_result = await self.db.execute(
            select(HabitInstance).where(
                and_(
                    HabitInstance.habit_id == habit_id,
                    HabitInstance.date == instance_date
                )
            )
        )
        instance = instance_result.scalar_one_or_none()
        if instance:
            instance.status = status
            instance.reason = reason
        else:
            instance = HabitInstance(
                habit_id=habit_id,
                date=instance_date,
                status=status,
                reason=reason
            )
            self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance

    from sqlalchemy import select

    async def get_day_stats(self, profile_id: int, target_date: date) -> DayStatsSchema:
        q = select(Habit).where(
            Habit.profile_id == profile_id,
            Habit.is_active == True,
            Habit.start_date <= target_date,
            (Habit.end_date == None) | (Habit.end_date >= target_date)
        )
        result = await self.db.execute(q)
        habits = result.scalars().all()

        completed_habits = 0
        skipped_habits = 0
        pending_habits = 0

        for habit in habits:
            q2 = select(HabitInstance).where(
                HabitInstance.habit_id == habit.id,
                HabitInstance.date == target_date
            )
            res2 = await self.db.execute(q2)
            instance = res2.scalar_one_or_none()
            status = instance.status if instance else HabitStatus.pending
            if isinstance(status, str):
                try:
                    status = HabitStatus(status)
                except ValueError:
                    status = HabitStatus.pending

            if status == HabitStatus.done:
                completed_habits += 1
            elif status == HabitStatus.skipped:
                skipped_habits += 1
            else:
                pending_habits += 1

        total_habits = len(habits)
        completion_percentage = (completed_habits / total_habits * 100) if total_habits > 0 else 0

        if completion_percentage == 0:
            color_intensity = "none"
        elif completion_percentage <= 33:
            color_intensity = "light"
        elif completion_percentage <= 66:
            color_intensity = "medium"
        else:
            color_intensity = "dark"

        return DayStatsSchema(
            date=target_date,
            total_habits=total_habits,
            completed_habits=completed_habits,
            skipped_habits=skipped_habits,
            pending_habits=pending_habits,
            completion_percentage=completion_percentage,
            color_intensity=color_intensity
        )

    async def get_calendar_stats(self, profile_id: int, start_date: date, end_date: date) -> List[DayStatsSchema]:
        """Получение статистики календаря за период"""
        stats = []
        current_date = start_date
        while current_date <= end_date:
            day_stat = await self.get_day_stats(profile_id, current_date)
            stats.append(day_stat)
            current_date += timedelta(days=1)
        return stats
