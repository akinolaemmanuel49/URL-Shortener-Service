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
    """
    Manage the lifespan of the FastAPI application, including connecting to and disconnecting from the database.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None
    """
    # Connect to the database
    await db.connect()
    # Create tables in the database
    await create_tables(database=db)

    try:
        # Provide control back to the application
        yield
    finally:
        # Disconnect from the database
        await db.disconnect()


# Initialize the FastAPI application with the specified title and lifespan manager
app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# Include routers for different endpoints
app.include_router(info_router)  # Router for general information endpoints
app.include_router(auth_router)  # Router for authentication-related endpoints
app.include_router(url_shortener_router)  # Router for URL shortening endpoints
app.include_router(url_resolver_router)  # Router for URL resolving endpoints
