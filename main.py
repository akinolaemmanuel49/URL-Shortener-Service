from contextlib import asynccontextmanager

from fastapi import FastAPI

from settings import settings
from database import database as db, create_tables
from routes.info import router as info_router
from routes.auth import router as auth_router
from routes.url_shortener import router as url_shortener_router
from routes.url_resolver import router as url_resolver_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to the database
    await db.connect()
    # Create tables
    print("CREATING TABLES !!!")
    await create_tables(database=db)

    try:
        yield
    finally:
        # Disconnect from the database
        await db.disconnect()


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.include_router(info_router)
app.include_router(auth_router)
app.include_router(url_shortener_router)
app.include_router(url_resolver_router)
