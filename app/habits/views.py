from sentry_sdk.session import Session

from app.habits.models import Habit
from app.habits.service import HabitService


class HabitView:
    def __init__(self, db):
        self.habit_service = HabitService(db)
