import jwt
from dotenv import load_dotenv
from fastapi import Request, HTTPException
from src.database.database import session_factory
from src.database.models import User, Roles
from src.database.repository import AsyncBaseRepository
import os

load_dotenv()


async def middleware(request: Request, call_next):
    if request.url.path == "/users" and request.method == "POST":
        return await call_next(request)

    token = request.headers.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authorised")

    token = token.split(" ")[1] if token.startswith("Bearer") else token

    try:
        decoded = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=os.getenv("JWT_ALG"))
        sub = decoded.get("sub")

        if not sub:
            raise HTTPException(status_code=400, detail="Invalid token")

        async with session_factory() as session:
            repo = AsyncBaseRepository(session)
            user = await repo.get_by_id(User, sub)

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            user_role = await repo.get_by_id(Roles, user.role_id)

            if request.url.path.startswith("/admin") and user_role.name != "Admin":
                raise HTTPException(status_code=403, detail="Access denied")

            return await call_next(request)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")