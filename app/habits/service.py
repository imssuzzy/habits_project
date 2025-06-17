from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, and_

from app.habits.schemas.schemas import HabitSchema, HabitCreateSchema
from app.habits.models import Habit, HabitInstance, HabitStatus
from typing import List, Optional

class HabitService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_one(self, data: HabitCreateSchema) -> HabitSchema:
        habit = Habit(**data.dict())
        self.db.add(habit)
        await self.db.commit()
        await self.db.refresh(habit)
        
        # Создаем первый экземпляр привычки со статусом pending
        instance = HabitInstance(
            habit_id=habit.id,
            date=data.start_date,
            status=HabitStatus.pending
        )
        self.db.add(instance)
        await self.db.commit()
        
        # Получаем обновленную привычку со статусом
        habit_dict = HabitSchema.from_orm(habit).dict()
        habit_dict['habit_status'] = HabitStatus.pending.value
        return HabitSchema(**habit_dict)

    async def get_one(self, habit_id: int) -> Optional[HabitSchema]:
        result = await self.db.execute(
            select(Habit).where(Habit.id == habit_id)
        )
        habit = result.scalar_one_or_none()
        if not habit:
            return None
            
        # Получаем последний статус привычки
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

    async def find_all(self) -> List[HabitSchema]:
        result = await self.db.execute(select(Habit))
        habits = result.scalars().all()
        
        habits_with_status = []
        for habit in habits:
            # Получаем последний статус для каждой привычки
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

    async def update_one(self, habit_id: int, data: dict) -> Optional[HabitSchema]:
        stmt = (
            update(Habit)
            .where(Habit.id == habit_id)
            .values(**data)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(stmt)
        await self.db.commit()
        
        return await self.get_one(habit_id)

    async def delete_one(self, habit_id: int) -> bool:
        stmt = delete(Habit).where(Habit.id == habit_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def get_habits_by_date(self, user_id: int, target_date: date) -> List[HabitSchema]:
        weekday = target_date.weekday()
        stmt = select(Habit).where(
            and_(
                Habit.user_id == user_id,
                Habit.start_date <= target_date,
                Habit.start_date + timedelta(days=Habit.duration_days) >= target_date,
                Habit.days_of_week.contains([str(weekday)])
            )
        )
        result = await self.db.execute(stmt)
        habits = result.scalars().all()
        return [HabitSchema.from_orm(habit) for habit in habits]

    @staticmethod
    async def get_habit_instance(habit_id: int, instance_date: date, db: AsyncSession) -> Optional[HabitInstance]:
        result = await db.execute(
            select(HabitInstance).filter_by(habit_id=habit_id, date=instance_date)
        )
        return result.scalars().first()

    @staticmethod
    async def mark_habit(
            habit_id: int,
            instance_date: date,
            status: HabitStatus,
            db: AsyncSession
    ) -> HabitInstance:
        result = await db.execute(
            select(Habit).filter(Habit.id == habit_id)
        )
        habit = result.scalars().first()
        if not habit:
            raise ValueError("Habit not found")

        instance = await HabitService.get_habit_instance(habit_id, instance_date, db)
        if instance:
            instance.status = status
        else:
            instance = HabitInstance(
                habit_id=habit_id,
                date=instance_date,
                status=status,
            )
            db.add(instance)

        await db.commit()
        await db.refresh(instance)
        return instance




