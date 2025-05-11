import json
import os
from fastapi import APIRouter, UploadFile, HTTPException, Query, Depends
from starlette.responses import JSONResponse

from src.users.schemas import UserSchema, UserSettingsSchema, UserInfoSchema, UserListSchema, UserProfileSchema
from src.database.database import session_factory, s3_factory, redis_factory
from src.database.models import User, Settings
from src.database.repository import AsyncBaseRepository
from src.auth.auth_provider import token_provider

BUCKET_NAME = os.getenv("BUCKET_NAME")

router = APIRouter()


@router.post("/users", description="Создание пользователя")
async def create_user(user: UserSchema):
    try:
        async with session_factory() as session:
            repo = AsyncBaseRepository(session)
            role = await repo.get_role("User")
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
                ),
                role_id=role.id,
                role=role

            )
            await repo.add(new_user)
            token = token_provider.create_access_token(uid=user.id, role=role.name)
            headers = {"access_token": token}

            return JSONResponse(status_code=200,
                                content={"message": "OK", "user_id": new_user.id},
                                headers=headers)

    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(ex)}")


@router.put("/user/{user_id}/update_user_settings", description="Обновление настроек поиска")
async def update_user_settings(user_id: int, settings: UserSettingsSchema):
    try:
        async with session_factory() as session:
            repo = AsyncBaseRepository(session)
            user = await repo.get_user_with_settings(user_id)
            if user is None:
                raise HTTPException(status_code=404, detail=f"User not found")

            for key, val in settings.dict().items():
                setattr(user.settings, key, val)

            await repo.update()

    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(ex)}")


@router.post("/users/{user_id}/upload_images", description="Загрузка изображений")
async def upload_images(user_id: int, images: list[UploadFile]):
    try:
        async with session_factory() as session:
            repo = AsyncBaseRepository(session)

            if not (1 <= len(images) <= 4):
                raise HTTPException(status_code=400, detail=f"Number of images should be between 1 and 4")

            allowed_file_extension = [".jpg", ".jpeg", ".png"]
            urls = []

            for num, file in enumerate(images, 1):
                file_extension = file.filename.split('.')[-1]

                if not (file_extension in allowed_file_extension):
                    raise HTTPException(status_code=400, detail="Unsupported file")

                key = f"user_photos/{user_id}/{num}.{file_extension}"
                content = await file.read()

                try:
                    s3_factory.put_object(Bucket=BUCKET_NAME, Key=key, Body=content, ContentType=file.content_type)
                    file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}"
                    urls.append(file_url)
                except Exception as ex:
                    raise HTTPException(status_code=500, detail=str(ex))

            user = await repo.get_by_id(User, user_id)

            if user is None:
                raise HTTPException(status_code=404, detail=f"User not found")

            user.images = '\n'.join(urls)

            await repo.update()

            return JSONResponse(status_code=200, content={"message": "OK", "user_files": urls})

    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(ex)}")


@router.put("/users/{user_id}/update_user_info", description="Обновленние данных пользователя")
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

            return JSONResponse(status_code=200, content={"message": "Updated successfully"})
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(ex)}")


@router.get("/users/{user_id}/swipe_list", description="Заполнение кэша для свайпа")
async def get_swipe_list(user_id: int, limit: int = Query(50, le=100, gt=0),
                         offset: int = Query(0, ge=0)):
    try:
        async with session_factory() as session:

            repo = AsyncBaseRepository(session)

            redis_key = f"user_list:{user_id}"

            current_user = await repo.get_user_with_settings(user_id)

            if current_user is None:
                raise HTTPException(status_code=404, detail="User not found")

            result = await repo.user_list(
                user_id,
                current_user.location,
                current_user.settings.radiusL,
                current_user.settings.radiusR,
                limit=limit,
                offset=offset
            )

            swipe_list = [UserListSchema(**user) for user in result]
            serialized = json.dumps([user.dict() for user in swipe_list])
            redis_factory.set(redis_key, serialized)

            return JSONResponse(status_code=200, content={"message": "Cached"})

    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(ex)}")


@router.get("/users/{user_id}/next_profile", description="Получить следующего пользователя из свайп-листа")
async def get_next_profile(user_id: int, prev_user_id: int | None = None):
    try:
        redis_key = f"user_list:{user_id}"

        if not redis_factory.exists(redis_key):
            raise HTTPException(status_code=404, detail="Swipe list not found")

        cached_data = redis_factory.get(redis_key)
        swipe_list = [UserListSchema(**data) for data in json.loads(cached_data)]

        if not swipe_list:
            raise HTTPException(status_code=404, detail="Swipe list is empty")

        if prev_user_id is None:
            return JSONResponse(status_code=200, content=swipe_list[0].dict())

        for index, user in enumerate(swipe_list):
            if user.id == prev_user_id:
                next_index = index + 1

                if next_index >= len(swipe_list):
                    redis_factory.delete(redis_key)
                    raise HTTPException(status_code=404, detail="No more users")

                return JSONResponse(status_code=200, content=swipe_list[next_index].dict())

        raise HTTPException(status_code=404, detail="Previous user not found in list")

    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(ex)}")


@router.get("/users/user_profile/{user_id}", description="Получить профиль пользователя")
async def user_profile(user_id: int):
    try:
        redis_key = f"user:{user_id}"
        if not redis_factory.exists(redis_key):
            async with session_factory() as session:
                repo = AsyncBaseRepository(session)

                current_user = await repo.get_by_id(User, user_id)

                if current_user is None:
                    raise HTTPException(status_code=404, detail="User not found")

                exp_time_sec = 86400

                profile = UserProfileSchema.from_orm(current_user)
                serialized = json.dumps(profile.dict())
                redis_factory.set(redis_key, serialized, ex=exp_time_sec)

                return JSONResponse(status_code=200, content={"profile": profile.dict()})

        cached_data = redis_factory.get(redis_key)
        profile = UserProfileSchema(**json.loads(cached_data))

        return JSONResponse(status_code=200, content={"profile": profile.dict()})

    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(ex)}")
