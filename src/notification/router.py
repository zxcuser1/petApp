from aio_pika import IncomingMessage
from src.database.database import session_factory
from src.database.models import User
from src.database.repository import AsyncBaseRepository
from src.main import rabbit_manager
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/notify/{user_id}", description="Уведомление для пользователя")
async def notify(user_id: int):
    try:
        with session_factory() as session:
            repo = AsyncBaseRepository(session)
            user = await repo.get_by_id(User, user_id)
            await rabbit_manager.publish("messages", f"Notification for {user.Name}. Someone liked you!!")
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(ex)}")


