from sqlalchemy.ext.asyncio import AsyncSession

from apps.database.repository import BaseRepository
from apps.profile.models import Profile


class ProfileService(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(Profile, session)
