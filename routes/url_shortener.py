from typing import List

from fastapi import APIRouter, Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from pydantic import HttpUrl

from schemas.url import APICreateResponse, APIDeleteResponse, APIReadResponse
from settings import settings
from utils import VerifyToken, URLShortener
from dal import fetch_multiple_urls, remove_record

router = APIRouter(prefix=f"{settings.BASE_URL_PATH}/shorten", tags=["url shortener"])
auth = VerifyToken()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.TOKEN_URI}")
bearer_scheme = HTTPBearer()


@router.post("/")
async def shorten_url(
    original_url: HttpUrl,
    credentials: HTTPAuthorizationCredentials = Depends(auth.verify),
) -> APICreateResponse:
    shortener = URLShortener(original_url=original_url, owner_id=credentials["sub"])
    key, created = await shortener.shorten_url()
    shortened_url = f"{str(settings.SHORTENED_URL_BASE)}{key}"
    return APICreateResponse(
        shortened_url=shortened_url, original_url=original_url, created=created
    )


@router.get("/")
async def list_shortened_urls(
    credentials: HTTPAuthorizationCredentials = Depends(auth.verify),
    limit: int = 10,
    offset: int = 0,
) -> List[APIReadResponse]:
    return await fetch_multiple_urls(
        owner_id=credentials["sub"], limit=limit, offset=offset
    )


@router.delete("/{key}")
async def delete_shortened_url(
    key: str,
    credentials: HTTPAuthorizationCredentials = Depends(auth.verify),
) -> APIDeleteResponse:
    await remove_record(key=key, owner_id=credentials["sub"])
    return APIDeleteResponse
