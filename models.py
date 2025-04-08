from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[String]
    image: Mapped[String]
    city: Mapped[String]
    age: Mapped[int]
    geo_sh: Mapped[float]
    geo_dolg: Mapped[float]


class Likes(Base):
    __tablename__ = 'likes'

    user1_id: Mapped[UUID] = mapped_column(primary_key=True)
    user2_id: Mapped[UUID] = mapped_column(primary_key=True)
    user1_like: Mapped[bool]
    user2_like: Mapped[bool]
