from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository import BaseRepository
from app.profile.models import User


class AuthService(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_login(self, login: str):
        stmt = select(self.model).where(self.model.login == login)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
