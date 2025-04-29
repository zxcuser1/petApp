from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from geoalchemy2.functions import ST_Distance, ST_DWithin
from src.database.models import User


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

    async def user_list(self, user_id, user_location, radius_min, radius_max, limit=50, offset=0):

        user_point = func.ST_SetSRID(func.ST_GeomFromText(user_location, 4326), 4326)

        stmt = (
            select(User, ST_Distance(User.location, user_point).label("distance"))
            .where(
                User.id != user_id,
                ST_DWithin(User.location, user_point, radius_max),
                ST_Distance(User.location, user_point) >= radius_min,
            )
            .order_by("distance")
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)

        return result.all()