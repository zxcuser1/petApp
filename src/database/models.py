from typing import Any
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geography
from sqlalchemy import String, ForeignKey, SmallInteger
from src.database.database import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    images: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String)
    age: Mapped[int] = mapped_column()
    location: Mapped[Any] = mapped_column(Geography(geometry_type='POINT', srid=4326))
    gender: Mapped[bool] = mapped_column()
    settings: Mapped["Settings"] = relationship(back_populates="user", uselist=False)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.role_id'))
    role: Mapped["Roles"] = relationship("Roles", back_populates="users", uselist=False)

class Likes(Base):
    __tablename__ = 'swipe'

    user1_id: Mapped[int] = mapped_column(primary_key=True)
    user2_id: Mapped[int] = mapped_column(primary_key=True)
    user1_like: Mapped[bool] = mapped_column(nullable=True)
    user2_like: Mapped[bool] = mapped_column(nullable=True)


class Settings(Base):
    __tablename__ = 'settings'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    ageL: Mapped[int] = mapped_column(SmallInteger)
    ageR: Mapped[int] = mapped_column(SmallInteger)
    radiusL: Mapped[int] = mapped_column(SmallInteger)
    radiusR: Mapped[int] = mapped_column(SmallInteger)
    gender: Mapped[bool] = mapped_column()

    user: Mapped["User"] = relationship(back_populates="settings")


class Roles(Base):
    __tablename__ = 'roles'

    role_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    users: Mapped["User"] = relationship("User", back_populates="role")