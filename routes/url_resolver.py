from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from utils import URLShortener

router = APIRouter()


@router.get("/{key}", include_in_schema=False)
async def resolve_url(key: str) -> str:
    original_url = await URLShortener.retrieve_original_url(key=key)
    return RedirectResponse(url=original_url)
