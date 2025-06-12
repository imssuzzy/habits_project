from app.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship

class Habit(Base):
    __tablename__ = 'habits'

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    duration_days = Column(Integer)
    days_of_week = Column(String)
    description = Column(String, nullable=True)
    start_date = Column(Date)

    instances = relationship("HabitInstance", cascade="all, delete")

class HabitInstance(Base):
    __tablename__ = 'habitinstances'
    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habits.id'))
    date = Column(Date)
    status = Column(String, default='pending')
    habit = relationship('Habit')