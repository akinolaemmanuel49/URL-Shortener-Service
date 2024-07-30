from contextlib import asynccontextmanager

from fastapi import FastAPI

from settings import settings
from database import database as db
from routes.info import router as info_router
from routes.auth import router as auth_router

app = FastAPI(title=settings.APP_NAME)

app.include_router(info_router)
app.include_router(auth_router)

@asynccontextmanager
async def database_lifespan(app: FastAPI):
    # Connect to the database
    db.connect()
    yield
    # Disconnect from the database
    db.disconnect()

