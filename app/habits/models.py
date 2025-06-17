import enum

from sqlalchemy.testing.pickleable import User

from app.database import Base
from sqlalchemy import ForeignKey, Integer, String, Date, ARRAY, UniqueConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

class HabitStatus(enum.Enum):
    pending = 'pending'
    done = 'done'
    skipped = 'skipped'

class Habit(Base):
    __tablename__ = 'habits'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    duration_days: Mapped[int] = mapped_column(Integer)
    days_of_week: Mapped[List[str]] = mapped_column(ARRAY(String))
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    start_date: Mapped[Date] = mapped_column(Date)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('profile.id'), nullable=True)

    instances: Mapped[list["HabitInstance"]] = relationship("HabitInstance", cascade="all, delete-orphan", back_populates="habit")
    user: Mapped[User] = relationship("User", back_populates="habits")

class HabitInstance(Base):
    __tablename__ = 'habitinstances'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    habit_id: Mapped[int] = mapped_column(Integer, ForeignKey('habits.id', ondelete='CASCADE'), nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    status: Mapped[HabitStatus] = mapped_column(Enum(HabitStatus), default=HabitStatus.pending, nullable=False)

    habit: Mapped["Habit"] = relationship('Habit', back_populates="instances")

    __table_args__ = (
        UniqueConstraint('habit_id', 'date', name='uq_habit_date'),
    )