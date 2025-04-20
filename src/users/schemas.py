from fastapi import UploadFile
from pydantic import BaseModel, Field, conlist


class UserSchema(BaseModel):
    name: str = Field(max_length=100)
    city: str
    age: int = Field(gt=17, le=120)
    geo_sh: float
    geo_dolg: float
    gender: bool


class UserSettingsSchema(BaseModel):
    ageL: int = Field(gt=17, le=120)
    ageR: int = Field(ge=ageL, le=120)
    radiusL: int = Field(ge=0, le=200)
    radiusR: int = Field(ge=radiusL, le=200)
    gender: bool
