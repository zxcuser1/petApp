from fastapi import APIRouter, HTTPException
from src.database.models import Likes
from src.database.database import session_factory
from src.database.repository import AsyncBaseRepository
from sqlalchemy import select

router = APIRouter()


@router.post("/like/{source}_{target}")
async def liked(source: int, target: int, is_liked: bool):
    try:
        async with session_factory() as session:
            repo = AsyncBaseRepository(session)
            ids = [source, target]
            ids.sort()
            stmt = select(Likes).where(
                Likes.user1_id == ids[0],
                Likes.user2_id == ids[1]
            )
            like = await session.execute(stmt)
            if like in None:
                new_like = Likes(
                    user1_id=ids[0],
                    user2_id=ids[1],
                    user1_like=is_liked if ids[0] == source else False,
                    user2_like=is_liked if ids[1] == source else False
                )
                await repo.add(new_like)
            else:
                like.user1_like = is_liked if ids[0] == source else like.user1_like
                like.user2_like = is_liked if ids[1] == source else like.user2_like
                await repo.update()

    except Exception as ex:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(ex)}")
