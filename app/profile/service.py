from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository import BaseRepository
from app.profile.models import User


class ProfileService(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
