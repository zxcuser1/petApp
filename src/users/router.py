import json
import os
from fastapi import APIRouter, UploadFile, HTTPException
from src.users.schemas import UserSchema, UserSettingsSchema, UserInfoSchema, UserListSchema
from src.database.database import session_factory, s3_factory, redis_factory
from src.database.models import User, Settings
from src.database.repository import AsyncBaseRepository

BUCKET_NAME = os.getenv("BUCKET_NAME")

router = APIRouter()


@router.post("/users/create_user", description="Создание пользователя")
async def create_user(user: UserSchema):
    try:
        async with session_factory() as session:
            repo = AsyncBaseRepository(session)
            new_user = User(
                name=user.name,
                city=user.city,
                age=user.age,
                location=f"POINT({user.coordinates[0]} {user.coordinates[1]})",
                gender=user.gender,
                settings=Settings(
                    ageL=18,
                    ageR=120,
                    radiusL=0,
                    radiusR=200,
                    gender=not user.gender
                )
            )
            await repo.add(new_user)
    except Exception as ex:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(ex)}")


@router.put("/user/{user_id}/update_user_settings", description="Обновление настроек поиска")
async def update_user_settings(user_id: int, settings: UserSettingsSchema):
    try:
        async with session_factory() as session:
            repo = AsyncBaseRepository(session)
            user = await repo.get_user_with_settings(user_id)
            if user is None:
                raise HTTPException(status_code=404, detail=f"User not found")

            for key, val in settings.dict():
                setattr(user.settings, key, val)

            await repo.update()

    except Exception as ex:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(ex)}")


@router.post("/users/{user_id}/upload_images", description="Загрузка изображений")
async def upload_images(user_id: int, images: list[UploadFile]):
    try:
        async with session_factory() as session:
            repo = AsyncBaseRepository(session)

            if not (1 <= len(images) <= 4):
                raise HTTPException(status_code=400, detail=f"Number of images should be between 1 and 4")

            num = 1
            urls = []
            for file in images:
                file_extension = file.filename.split('.')[-1]
                key = f"user_photos/{user_id}/{num}.{file_extension}"
                content = await file.read()
                s3_factory.put_object(Bucket=BUCKET_NAME, Key=key, Body=content, ContentType=file.content_type)
                file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}"
                urls.append(file_url)
                num += 1

            user = await repo.get_by_id(User, user_id)

            if user is None:
                raise HTTPException(status_code=404, detail=f"User not found")

            user.images = '\n'.join(urls)

            await repo.update()

    except Exception as ex:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(ex)}")


@router.put("users/{user_id}/update_user_info", description="Обновленние данных пользователя")
async def update_user_info(user_id: int, user_info: UserInfoSchema):
    try:
        async with session_factory() as session:

            repo = AsyncBaseRepository(session)
            current_user = await repo.get_by_id(User, user_id)
            if current_user is None:
                raise HTTPException(status_code=404, detail="User not found")

            current_user.description = user_info.description
            current_user.city = user_info.city

            await repo.update()

    except Exception as ex:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(ex)}")


@router.get("/users/{user_id}/get_swipe_list", description="Список пользователей для свайпа")
async def get_get_swipe_list_list(user_id: int):
    try:
        async with session_factory() as session:
            repo = AsyncBaseRepository(session)
            redis_key = f"user_list_{user_id}"
            if redis_factory.exists(redis_key):
                cached_data = redis_factory.get(redis_key)
                users_data = json.loads(cached_data)
                users = [UserListSchema(**data) for data in users_data]
                return users

            current_user = await repo.get_user_with_settings(user_id)
            if current_user is None:
                raise HTTPException(status_code=404, detail="User not found")

            result = await repo.user_list(user_id, current_user.location, current_user.settings.radiusL,
                                          current_user.settings.radiusR)

            data = [UserListSchema(**user) for user in result]
            serialized = json.dumps([user.dict() for user in data])
            redis_factory.set(redis_key, serialized)
            return data

    except Exception as ex:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(ex)}")
