from fastapi import APIRouter

from schemas.info import Info
from settings import settings

# Initialize the API router with a base path and tag
router = APIRouter(prefix="", tags=["info"])


@router.get(f"{settings.BASE_URL_PATH}/info")
async def info() -> Info:
    """
    Returns application configuration information.

    This endpoint retrieves and returns the current application configuration settings,
    including the application name, admin email, items per page, and database connection string.

    Returns:
        Info: An object containing the application configuration settings.
    """
    return Info(
        app_name=settings.APP_NAME,  # The name of the application
        admin_email=settings.ADMIN_EMAIL,  # The email address of the application administrator
        items_per_page=settings.ITEMS_PER_PAGE,  # The number of items to be displayed per page
        database=settings.DATABASE,  # The database connection string or name
    )
