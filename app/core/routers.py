from fastapi import APIRouter

from app.profile.router import router as profile_router
from app.habits.router import router as habits_router

api_router_v1 = APIRouter()
api_router_v1.include_router(profile_router, prefix="/profile", tags=["Profile"])
api_router_v1.include_router(habits_router, prefix="/habits", tags=["Habits"])
