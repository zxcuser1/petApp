from src.database.database import session_factory
from src.database.models import User
from src.database.repository import AsyncBaseRepository
from src.database.database import rabbit_manager
from fastapi import APIRouter, HTTPException

router = APIRouter()


async def notification(user_id: int):
    try:
        with session_factory() as session:
            repo = AsyncBaseRepository(session)
            user = await repo.get_by_id(User, user_id)
            await rabbit_manager.publish("messages", f"Notification for {user.Name}. Someone liked you!!")
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(ex)}")


