from typing import Annotated

from fastapi import APIRouter, Depends, Response, Form
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from apps.auth.exceptions import ProfileIsNotActive, WrongCredentials
from apps.auth.schema import LoginSchema, TokenInfo
from apps.auth.services import AuthService
from apps.auth.utils import (
    create_access_token,
    create_refresh_token,
    get_current_active_profile,
    get_current_profile_by_refresh,
    validate_password,
)
from apps.core.exceptions import NotFoundException
from apps.database import get_db
from apps.profile.models import Profile
from apps.profile.schemas import ProfileSchema

http_bearer = HTTPBearer(auto_error=False)
router = APIRouter(dependencies=[Depends(http_bearer)])


@router.post("/refresh", response_model=TokenInfo)
async def refresh_token(
    current_profile: Profile = Depends(get_current_profile_by_refresh),
):
    access_token = await create_access_token(current_profile)
    refresh_token = await create_refresh_token(current_profile)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get("/me", response_model=ProfileSchema)
async def get_me(
    current_profile: Profile = Depends(get_current_active_profile),
):
    return current_profile

from fastapi import Form

@router.post("/login-form", response_model=TokenInfo)
async def auth_profile_issue_jwt_form(
    username: str = Form(...),
    password: str = Form(...),
    response: Response = None,
    db: AsyncSession = Depends(get_db),
):
    auth_service: AuthService = AuthService(db)
    profile: Profile = await auth_service.get_by_login(username)
    if not profile:
        raise NotFoundException("Profile not found")

    if not validate_password(
        password=password,
        hashed_password=profile.password,
    ):
        raise WrongCredentials()

    if not profile.is_active:
        raise ProfileIsNotActive()

    access_token = await create_access_token(profile)
    refresh_token = await create_refresh_token(profile)

    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )
