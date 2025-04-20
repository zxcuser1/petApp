from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.users.models import User


class AsyncBaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, obj):
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get_by_id(self, model, obj_id):
        return await self.session.get(model, obj_id)

    async def get_user_with_settings(self, user_id: int):
        result = await self.session.execute(
            select(User).options(joinedload(User.settings)).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def list(self, model):
        result = await self.session.execute(
            select(model)
        )
        return result.scalars().all()

    async def delete(self, obj):
        await self.session.delete(obj)
        await self.session.commit()

    def update(self):
        self.session.commit()
