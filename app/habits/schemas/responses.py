from .schemas import *
from ...core.schema import SuccessResponse


class HabitResponse(SuccessResponse):
    data: HabitSchema
    message: str = "success"

class HabitInstanceResponse(SuccessResponse):
    data: HabitInstanceSchema
    message: str = "success"

class HabitListResponse(SuccessResponse):
    data: List[HabitSchema]
    message: str = "success"