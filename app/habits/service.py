from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.habits.models import Habit  # твоя модель Habit
from typing import List, Optional

class HabitService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_one(self, data: dict) -> Habit:
        habit = Habit(**data)
        self.db.add(habit)
        await self.db.commit()
        await self.db.refresh(habit)
        return habit

    async def get_one(self, habit_id: int) -> Optional[Habit]:
        result = await self.db.execute(select(Habit).where(Habit.id == habit_id))
        habit = result.scalar_one_or_none()
        return habit

    async def find_all(self) -> List[Habit]:
        result = await self.db.execute(select(Habit))
        habits = result.scalars().all()
        return habits

    async def update_one(self, habit_id: int, data: dict) -> Optional[Habit]:
        habit = await self.get_one(habit_id)
        if not habit:
            return None
        for key, value in data.items():
            setattr(habit, key, value)
        self.db.add(habit)
        await self.db.commit()
        await self.db.refresh(habit)
        return habit

    async def delete_one(self, habit_id: int) -> bool:
        habit = await self.get_one(habit_id)
        if not habit:
            return False
        await self.db.delete(habit)
        await self.db.commit()
        return True
