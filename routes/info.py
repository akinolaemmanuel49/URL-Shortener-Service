from fastapi import APIRouter

from settings import settings

router = APIRouter(prefix='', tags=['info'])

@router.get('/info')
async def info():
    return {
        'app_name': settings.APP_NAME,
        'admin_email': settings.ADMIN_EMAIL,
        'items_per_page': settings.ITEMS_PER_PAGE,
        'database': settings.DATABASE
    }