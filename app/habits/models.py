from app.database import Base
from sqlalchemy import ForeignKey, Integer, String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Habit(Base):
    __tablename__ = 'habits'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    duration_days: Mapped[int] = mapped_column(Integer)
    days_of_week: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    start_date: Mapped[Date] = mapped_column(Date)

    instances: Mapped[list["HabitInstance"]] = relationship("HabitInstance", cascade="all, delete")

class HabitInstance(Base):
    __tablename__ = 'habitinstances'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    habit_id: Mapped[int] = mapped_column(Integer, ForeignKey('habits.id'))
    date: Mapped[Date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String, default='pending')
    habit: Mapped["Habit"] = relationship('Habit')