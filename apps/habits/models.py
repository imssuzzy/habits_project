import enum
from datetime import date, datetime
from sqlalchemy import ForeignKey, Integer, String, Date, UniqueConstraint, Enum, Text, DateTime
from sqlalchemy.dialects.postgresql import ARRAY

from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

from apps.database import Base


class HabitStatus(enum.Enum):
    pending = 'pending'
    done = 'done'
    skipped = 'skipped'
    deleted = 'deleted'


class HabitInstance(Base):
    __tablename__ = 'habitinstances'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    habit_id: Mapped[int] = mapped_column(Integer, ForeignKey('habits.id', ondelete='CASCADE'), nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    status: Mapped[HabitStatus] = mapped_column(Enum(HabitStatus), default=HabitStatus.pending, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Причина пропуска или удаления
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    habit: Mapped["Habit"] = relationship('Habit', back_populates="instances")

    __table_args__ = (
        UniqueConstraint('habit_id', 'date', name='uq_habit_date'),
    )


class Habit(Base):
    __tablename__ = 'habits'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    days_of_week: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)  # ["1", "3", "5"] для Пн, Ср, Пт
    start_date: Mapped[Date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)  # Дата окончания привычки
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey('profile.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    instances: Mapped[list[HabitInstance]] = relationship("HabitInstance", cascade="all, delete-orphan", back_populates="habit")
    profile: Mapped["Profile"] = relationship("Profile", back_populates="habits")