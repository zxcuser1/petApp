from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from src.database.database import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    images: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String)
    age: Mapped[int] = mapped_column()
    geo_sh: Mapped[float] = mapped_column()
    geo_dolg: Mapped[float] = mapped_column()
    gender: Mapped[bool]
    settings: Mapped["Settings"] = relationship(back_populates="user", uselist=False)


class Likes(Base):
    __tablename__ = 'likes'

    user1_id: Mapped[int] = mapped_column(primary_key=True)
    user2_id: Mapped[int] = mapped_column(primary_key=True)
    user1_like: Mapped[bool] = mapped_column()
    user2_like: Mapped[bool] = mapped_column()


class Settings(Base):
    __tablename__ = 'settings'

    userId: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    ageL: Mapped[int] = mapped_column()
    ageR: Mapped[int] = mapped_column()
    radiusL: Mapped[int] = mapped_column()
    radiusR: Mapped[int] = mapped_column()
    gender: Mapped[bool] = mapped_column()
    user: Mapped["User"] = relationship(back_populates="settings")
