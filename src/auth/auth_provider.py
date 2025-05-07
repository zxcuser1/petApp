from authx import AuthX, AuthXConfig
import os

from fastapi import Depends, HTTPException

config = AuthXConfig()

config.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
config.JWT_ALGORITHM = os.getenv("JWT_ALG")

token_provider = AuthX(config=config)


def require_role(role: str):
    def role_checker(user=Depends(token_provider.get_current_subject)):
        if user.get("role") != role:
            raise HTTPException(
                status_code=403,
                detail="Permission denied"
            )
        return user

    return role_checker
