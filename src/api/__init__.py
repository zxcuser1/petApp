from fastapi import APIRouter

from src.users.router import router as user_router
from src.likes.router import router as like_router

main_router = APIRouter()

main_router.include_router(user_router)
main_router.include_router(like_router)