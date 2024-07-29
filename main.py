from contextlib import asynccontextmanager

from fastapi import FastAPI

from settings import settings
from database import database as db
from routes.info import router as info_router

app = FastAPI(title=settings.APP_NAME)
app.include_router(info_router)

@asynccontextmanager
async def database_lifespan(app: FastAPI):
    # Connect to the database
    db.connect()
    yield
    # Disconnect from the database
    db.disconnect()

