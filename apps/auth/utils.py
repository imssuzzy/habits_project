import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt, JWTError
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from apps.auth.exceptions import TokenInvalid, ProfileIsNotActive
from apps.auth.services import AuthService
from apps.core.config import settings
from apps.database import get_db
from apps.profile.models import Profile
from apps.profile.schemas import ProfileSchema

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from apps.profile.service import ProfileService
from apps.database import get_db
from apps.profile.models import Profile
from sqlalchemy.ext.asyncio import AsyncSession

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ACCESS_TOKEN_EXPIRE_DAYS = 30

http_bearer = HTTPBearer(auto_error=False)

TOKEN_TYPE_FIELD = "token_type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/profile/login-form",
)


def encode_jwt(
    payload: dict,
    secret_key: str = settings.AUTH_JWT.SECRET_KEY,
    algorithm: str = settings.AUTH_JWT.ALGORITHM,
    expiration_minutes: int = settings.AUTH_JWT.ACCESS_TOKEN_EXPIRATION_MINUTES,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expiration_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
        jti=str(uuid.uuid4()),
    )
    encoded = jwt.encode(
        to_encode,
        secret_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(token: str, secret_key: str = settings.AUTH_JWT.SECRET_KEY,) -> dict:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token decode failed")


def hash_password(
    password: str,
) -> str:
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode('utf-8')


def validate_password(
    password: str,
    hashed_password: str,
) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


async def generate_jwt_token(
    token_type: str,
    token_data: dict,
    expiration_minutes: int = settings.AUTH_JWT.ACCESS_TOKEN_EXPIRATION_MINUTES,
    expire_timedelta: timedelta | None = None,
) -> str:
    jwt_payload = {
        TOKEN_TYPE_FIELD: token_type
    }
    jwt_payload.update(token_data)
    return encode_jwt(
        jwt_payload,
        expiration_minutes=expiration_minutes,
        expire_timedelta=expire_timedelta,
    )


async def create_access_token(profile: Profile):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(profile.id),
        "exp": expire,
        "token_type": "refresh",
    }

    token = jwt.encode(payload, settings.SECRET_KEY.get_secret_value(), algorithm=ALGORITHM)
    return token


async def create_refresh_token(profile: Profile):
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(profile.id),
        "exp": expire,
    }

    token = jwt.encode(payload, settings.SECRET_KEY.get_secret_value(), algorithm=ALGORITHM)
    return token


def validate_token_type(payload: dict, token_type: str):
    if payload.get(TOKEN_TYPE_FIELD) == token_type:
        return True
    raise TokenInvalid


async def get_current_token_payload(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_jwt(token=token)
    except jwt.InvalidTokenError as e:
        raise TokenInvalid(str(e))
    return payload


class ProfileGetterFromToken:
    def __init__(self, token_type: str):
        self.token_type = token_type

    async def __call__(self, token: str = Depends(oauth2_scheme)):
        # Здесь должна быть логика получения профиля по токену
        return Profile()


get_current_profile = ProfileGetterFromToken(token_type=ACCESS_TOKEN_TYPE)
get_current_profile_by_refresh = ProfileGetterFromToken(token_type=REFRESH_TOKEN_TYPE)


async def get_user_by_token_sub(
        payload: dict,
        db: AsyncSession = Depends(get_db)
):
    login: str | None = payload.get("sub")
    auth_service: AuthService = AuthService(db)
    profile: Profile = await auth_service.get_by_login(login)
    if profile:
        return profile
    raise TokenInvalid


async def get_current_active_profile(
    request: Request,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
) -> Profile:
    token = None

    # 1. Authorization header
    if credentials:
        token = credentials.credentials
    # 2. Cookie fallback
    elif "access_token" in request.cookies:
        token = request.cookies["access_token"]

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = decode_jwt(token)
        profile_id = payload.get("sub")
        if not profile_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token decode failed")

    profile_service = ProfileService(db)
    profile = await profile_service.get_one(int(profile_id))
    if not profile or not profile.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing profile")

    return profile


# async def get_access_token_from_cookies(access_token: str = Cookie(None)):
#     if access_token is None:
#         raise TokenInvalid("No access token found in cookies")
#     return access_token
#
# async def get_refresh_token_from_cookies(refresh_token: str = Cookie(None)):
#     if refresh_token is None:
#         raise TokenInvalid("No refresh token found in cookies")
#     return refresh_token
