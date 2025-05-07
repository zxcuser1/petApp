from fastapi import APIRouter, HTTPException, Depends
from starlette.responses import JSONResponse

from src.database.models import Likes
from src.database.database import session_factory
from src.database.repository import AsyncBaseRepository
from sqlalchemy import select
from src.notification.router import notify
from src.auth.auth_provider import require_role

router = APIRouter()


@router.post("/swipe/{source}_{target}", description="Свайп от пользователя")
async def swipe(source: int, target: int, is_liked: bool, user=Depends(require_role("User"))):
    try:
        async with session_factory() as session:
            if source <= 0 or target <= 0:
                raise HTTPException(status_code=400, detail="Invalid Id")
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
                    user1_like=is_liked if ids[0] == source else None,
                    user2_like=is_liked if ids[1] == source else None
                )
                await notify(target)
                await repo.add(new_like)
            else:
                like.user1_like = is_liked if ids[0] == source else like.user1_like
                like.user2_like = is_liked if ids[1] == source else like.user2_like
                await repo.update()

            return JSONResponse(status_code=200, content={"message": "Swipe recorded"})
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(ex)}")
