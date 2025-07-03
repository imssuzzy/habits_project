from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository import BaseRepository
from app.profile.models import Profile


class AuthService(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(Profile, session)

    async def get_by_login(self, login: str) -> Profile:
        result = await self.session.execute(
            select(self.model).where(self.model.login == login)
        )
        return result.scalar_one_or_none()
