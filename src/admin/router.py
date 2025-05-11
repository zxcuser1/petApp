from src.database.database import session_factory, redis_factory
from src.database.models import User
from src.database.repository import AsyncBaseRepository
from time import perf_counter
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text

router = APIRouter()


@router.get("/admin/db_health_check", description="Проверка бд")
async def db_health_check():
    try:
        async with session_factory() as session:

            query = "SELECT 1;"
            start_q = perf_counter()
            res = await session.execute(query)
            res.fetchall()
            end_q = perf_counter()

            lock_query = text("SELECT * FROM pg_locks WHERE NOT granted;")
            lock_result = await session.execute(lock_query)
            deadlocks = lock_result.fetchall()

            return JSONResponse(status_code=200, content={"query_time": end_q - start_q, "deadlocks": len(deadlocks)})
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@router.get("/admin/redis_health_check", description="Проверка редис")
def redis_check():
    try:
        response = redis_factory.ping()
        if response:
            return JSONResponse(status_code=200, content={"redis_status": "OK"})
        else:
            raise HTTPException(status_code=500, detail="No response from Redis")
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/admin/users/ban_user/{user_id}", description="Забанить\\Разбанить пользователя")
async def ban_user(user_id: int, is_ban: bool):
    try:
        async with session_factory() as session:
            repo = AsyncBaseRepository(session)
            user = await repo.get_by_id(User, user_id)

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            user.is_delete = is_ban
            await repo.update()

            return JSONResponse(status_code=200, content={"user_id": user_id, "is_banned": user.is_delete})

    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
