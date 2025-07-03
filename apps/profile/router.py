from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.core.exceptions import NotFoundException
from apps.database import get_db
from apps.profile.schemas import ProfileCreateSchema, ProfileResponse, ProfileListResponse
from apps.profile.service import ProfileService
from apps.auth.utils import hash_password

router = APIRouter()


@router.get("/profile-list", response_model=ProfileListResponse)
async def get_profile_list(db: AsyncSession = Depends(get_db)):
    auth_service: ProfileService = ProfileService(db)
    profile = await auth_service.find_all()
    if not profile:
        raise NotFoundException("Profile not found")
    return ProfileListResponse(data=profile)


@router.get("/profile/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    auth_service: ProfileService = ProfileService(db)
    profile = await auth_service.get_one(profile_id)
    if not profile:
        raise NotFoundException("Profile not found")
    return ProfileResponse(data=profile)


@router.post("/profile", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreateSchema,
    db: AsyncSession = Depends(get_db)):
    auth_service: ProfileService = ProfileService(db)

    profile_dict = profile_data.model_dump()
    profile_dict["password"] = hash_password(profile_dict["password"])
    profile_dict["is_active"] = True

    new_profile = await auth_service.add_one(profile_dict)
    print("PROFILE ID", new_profile.id)
    return ProfileResponse(data=new_profile)


@router.put("/profile/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: int, profile_data: ProfileCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    auth_service: ProfileService = ProfileService(db)
    data = profile_data.model_dump()
    updated_profile = await auth_service.update_one(profile_id, data)
    if not updated_profile:
        raise NotFoundException("Profile not found")
    return ProfileResponse(data=updated_profile)


@router.delete("/profile/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    auth_service: ProfileService = ProfileService(db)
    deleted = await auth_service.delete_one(profile_id)
    if not deleted:
        raise NotFoundException("Profile not found")
    return
