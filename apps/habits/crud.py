from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional
from . import models, schemas

def create_habit(db: Session, habit: schemas.HabitCreate) -> models.Habit:
    try:
        db_habit = models.Habit(**habit.dict())
        db.add(db_habit)
        db.commit()
        db.refresh(db_habit)

        for i in range(habit.duration_days):
            dt = habit.start_date + timedelta(days=i)
            if dt.weekday() in [int(d) for d in habit.days_of_week]:
                db.add(models.HabitInstance(habit_id=db_habit.id, date=dt))
        db.commit()
        return db_habit
    except Exception as e:
        db.rollback()
        raise e

def get_instances_by_date(db: Session, target_date) -> List[models.HabitInstance]:
    return db.query(models.HabitInstance).filter(models.HabitInstance.date == target_date).all()

def update_instance_status(db: Session, inst_id: int, new_status: str) -> Optional[models.HabitInstance]:
    if new_status not in ['pending', 'completed', 'skipped']:
        raise ValueError("Invalid status. Must be one of: pending, completed, skipped")
    
    try:
        inst = db.query(models.HabitInstance).get(inst_id)
        if not inst:
            return None
            
        inst.status = new_status
        if new_status == 'skipped':
            nxt = inst.date + timedelta(days=1)
            db.add(models.HabitInstance(habit_id=inst.habit_id, date=nxt))
        db.commit()
        return inst
    except Exception as e:
        db.rollback()
        raise e

def delete_habit(db: Session, habit_id: int) -> None:
    try:
        db.query(models.Habit).filter(models.Habit.id == habit_id).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        raise e


