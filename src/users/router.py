import os
from fastapi import APIRouter, UploadFile, HTTPException
from src.users.schemas import UserSchema, UserSettingsSchema
from src.database.database import session_factory, s3_factory
from src.database.models import User, Settings
from src.database.repository import AsyncBaseRepository

BUCKET_NAME = os.getenv("BUCKET_NAME")

router = APIRouter()


@router.post("/users/create_user")
async def reg_user(user: UserSchema):
    try:
        async with session_factory() as session:
            repo = AsyncBaseRepository(session)
            new_user = User(
                name=user.name,
                city=user.city,
                age=user.age,
                geo_sh=user.geo_sh,
                geo_dolg=user.geo_dolg,
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


@router.put("/user/{user_id}/update_user_settings")
async def update_UserSettings(user_id: int, settings: UserSettingsSchema):
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


@router.post("/users/{user_id}/upload_images")
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
