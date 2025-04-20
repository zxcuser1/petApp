from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import config
import redis
import os
import boto3

REDIS_HOST = os.getenv("REDIS_DB_HOST")
REDIS_PORT = os.getenv("REDIS_DB_PORT")

S3_KEY = os.getenv("S3_KEY")
S3_SECRET = os.getenv("S3_SECRET")
S3_REGION = os.getenv("S3_REGION")

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


class Base(DeclarativeBase):
    pass
