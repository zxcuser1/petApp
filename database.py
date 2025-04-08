from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import config

engine = create_async_engine(
    url=config.setting.DB_URL,
    echo=True,
)

session = async_sessionmaker(engine)


class Base(DeclarativeBase):
    pass
