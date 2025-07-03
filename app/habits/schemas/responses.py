from .schemas import *
from ...core.schema import SuccessResponse
from typing import List


class HabitResponse(SuccessResponse):
    data: HabitSchema
    message: str = "success"

class HabitCreateResponse(SuccessResponse):
    data: HabitSchema
    message: str = "Habit created successfully"


class HabitInstanceResponse(SuccessResponse):
    data: HabitInstanceSchema
    message: str = "success"


class HabitListResponse(SuccessResponse):
    data: List[HabitSchema]
    message: str = "success"


class HabitWithInstancesResponse(SuccessResponse):
    data: HabitWithInstancesSchema
    message: str = "success"


class DayStatsResponse(SuccessResponse):
    data: DayStatsSchema
    message: str = "success"


class DayStatsListResponse(SuccessResponse):
    data: List[DayStatsSchema]
    message: str = "success"


class HabitHistoryResponse(SuccessResponse):
    data: List[HabitHistorySchema]
    message: str = "success"

class HabitDeleteResponse(SuccessResponse):
    deleted_habit_id: int
    message: str = "Habit deleted successfully"