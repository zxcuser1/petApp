from typing import List
from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    name: str = Field(max_length=100)
    city: str
    age: int = Field(gt=17, le=120)
    coordinates: List[float]
    gender: bool


class UserSettingsSchema(BaseModel):
    ageL: int = Field(gt=17, le=120)
    ageR: int = Field(ge=ageL, le=120)
    radiusL: int = Field(ge=0, le=200)
    radiusR: int = Field(ge=radiusL, le=200)
    gender: bool


class UserListSchema(BaseModel):
    id: int
    name: str = Field(max_length=100)
    city: str
    description: str = Field(max_length=150)
    age: int = Field(gt=17, le=120)


class UserInfoSchema(BaseModel):
    city: str
    description: str = Field(max_length=150)
