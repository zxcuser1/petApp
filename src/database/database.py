import datetime

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import text
import src.database.config as config
import redis
import os
import boto3

from src.database.rabbitmq import RabbitMQManager

load_dotenv()
REDIS_HOST = os.getenv("REDIS_DB_HOST")
REDIS_PORT = os.getenv("REDIS_DB_PORT")

S3_KEY = os.getenv("S3_KEY")
S3_SECRET = os.getenv("S3_SECRET")
S3_REGION = os.getenv("S3_REGION")

HOST = os.getenv("RABBIT_MQ_HOST")
PORT = int(os.getenv("RABBIT_MQ_PORT"))

engine = create_async_engine(
    url=config.setting.DB_URL,
    echo=True,
)

session_factory = async_sessionmaker(engine)

redis_factory = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

s3_factory = boto3.client(
    's3',
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=S3_SECRET,
    region_name=S3_REGION
)

rabbit_manager = RabbitMQManager(host=HOST, port=PORT)


class Base(DeclarativeBase):
    __abstract__ = True

    is_delete: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow()
    )
