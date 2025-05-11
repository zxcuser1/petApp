from src.database.database import rabbit_manager
from fastapi import FastAPI
from src.api.init_routs import main_router
from src.notification.consumer import start_consumer
import asyncio
from src.middleware.auth_middleware import middleware

app = FastAPI()
app.middleware("http")(middleware)
app.include_router(main_router)


@app.on_event("startup")
async def startup_event():
    await rabbit_manager.connect()
    asyncio.create_task(start_consumer())


@app.on_event("shutdown")
async def shutdown_event():
    await rabbit_manager.close()
