from fastapi import APIRouter

from schemas.info import Info
from settings import settings

router = APIRouter(prefix="", tags=["info"])


@router.get(f"{settings.BASE_URL_PATH}/info")
async def info() -> Info:
    return Info(
        app_name=settings.APP_NAME,
        admin_email=settings.ADMIN_EMAIL,
        items_per_page=settings.ITEMS_PER_PAGE,
        database=settings.DATABASE,
    )
