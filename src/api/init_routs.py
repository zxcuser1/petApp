from fastapi import APIRouter

from src.users.router import router as user_router
from src.swipe.router import router as like_router
from src.notification.notify import router as notify_router

main_router = APIRouter()

main_router.include_router(user_router)
main_router.include_router(like_router)
main_router.include_router(notify_router)