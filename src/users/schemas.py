from typing import List
from pydantic import BaseModel, Field, model_validator


class OrmBaseModel(BaseModel):
    class Config:
        orm_mode = True


class UserSchema(OrmBaseModel):
    name: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1)
    age: int = Field(gt=17, le=120)
    coordinates: List[float]
    gender: bool


class UserSettingsSchema(OrmBaseModel):
    ageL: int = Field(gt=17, le=120)
    ageR: int = Field(gt=17, le=120)
    radiusL: int = Field(ge=0, le=200)
    radiusR: int = Field(ge=0, le=200)
    gender: bool

    @model_validator(mode="after")
    def check_ranges(self):
        if self.ageL > self.ageR:
            raise ValueError("ageL must be less than or equal to ageR")
        if self.radiusL > self.radiusR:
            raise ValueError("radiusL must be less than or equal to radiusR")
        return self


class UserListSchema(OrmBaseModel):
    id: int
    name: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=150)
    age: int = Field(gt=17, le=120)


class UserInfoSchema(OrmBaseModel):
    city: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=150)


class UserProfileSchema(OrmBaseModel):
    name: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=150)
    age: int = Field(gt=17, le=120)
    images: List[str]
