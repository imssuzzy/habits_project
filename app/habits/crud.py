from sqlalchemy.orm import Session
from datetime import timedelta
from . import models, schemas

def create_habit(db: Session, habit: schemas.HabitCreate):
    db_habit = models.Habit(**habit.dict(), days_of_week=','.join(map(str,habit.days_of_week)))
    db.add(db_habit); db.commit(); db.refresh(db_habit)

    for i in range(habit.duration_days):
        dt = habit.start_date + timedelta(days=i)
        if dt.weekday() in habit.days_of_week:
            db.add(models.HabitInstance(habit_id=db_habit.id, date=dt))
    db.commit()
    return db_habit

def get_instances_by_date(db: Session, target_date):
    return db.query(models.HabitInstance).filter(models.HabitInstance.date == target_date).all()

def update_instance_status(db: Session, inst_id: int, new_status: str):
    inst = db.query(models.HabitInstance).get(inst_id)
    if not inst: return None
    inst.status = new_status
    if new_status == 'skipped':
        nxt = inst.date + timedelta(days=1)
        db.add(models.HabitInstance(habit_id=inst.id, date=nxt))
    db.commit()
    return inst

def delete_habit(db: Session, habit_id: int):
    db.query(models.Habit).filter(models.Habit.id == habit_id).delete()
    db.commit()


