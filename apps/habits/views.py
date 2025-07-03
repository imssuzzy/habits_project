from sentry_sdk.session import Session

from apps.habits.models import Habit
from apps.habits.service import HabitService


class HabitView:
    def __init__(self, db):
        self.habit_service = HabitService(db)
