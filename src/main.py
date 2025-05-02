from fastapi import FastAPI
from src.api import main_router
from src.database.rabbitmq import RabbitMQManager
from src.notification.consumer import start_consumer
import asyncio
import os

HOST = os.getenv("RABBIT_MQ_HOST")
PORT = int(os.getenv("RABBIT_MQ_PORT"))

app = FastAPI()
app.include_router(main_router)

rabbit_manager = RabbitMQManager(host=HOST, port=PORT)


@app.on_event("startup")
async def startup_event():
    await rabbit_manager.connect()
    asyncio.create_task(start_consumer())


@app.on_event("shutdown")
async def shutdown_event():
    await rabbit_manager.close()
