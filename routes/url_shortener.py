from typing import Dict, List, Union

from fastapi import APIRouter, Depends, HTTPException, Query
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

# Initialize the API router for URL shortening endpoints
router = APIRouter(prefix=f"{settings.BASE_URL_PATH}/shorten", tags=["url shortener"])
auth = VerifyToken()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.TOKEN_URI}")
bearer_scheme = HTTPBearer()


@router.post("/")
async def shorten_url(
    url: HttpUrl = Query(),
    credentials: HTTPAuthorizationCredentials = Depends(auth.verify),
) -> APICreateResponse:
    """
    Shorten the provided URL and store it in the database.

    Args:
        original_url (HttpUrl): The URL to be shortened.
        credentials (HTTPAuthorizationCredentials): The credentials of the authenticated user.

    Returns:
        APICreateResponse: A response containing the shortened URL, the original URL, and a flag indicating if the URL was newly created.
    """
    # Initialize URLShortener with the provided URL and the authenticated user's ID
    shortener = URLShortener(original_url=url, owner_id=credentials["sub"])

    # Generate a unique key and store the URL in the database
    key, created = await shortener.shorten_url()

    # Construct the full shortened URL
    shortened_url = f"{str(settings.SHORTENED_URL_BASE)}{key}"

    # Return the response with the shortened URL details
    return APICreateResponse(
        shortened_url=shortened_url, original_url=url, created=created
    )


@router.get("/")
async def list_shortened_urls(
    credentials: HTTPAuthorizationCredentials = Depends(auth.verify),
    limit: int = Query(10, gt=0),
    offset: int = Query(0, ge=0),
) -> Dict[str, Union[int, List[APIReadResponse]]]:
    """
    List all shortened URLs for the authenticated user with pagination support.

    Args:
        credentials (HTTPAuthorizationCredentials): The credentials of the authenticated user.
        limit (int): The number of results to return per page (default is 10).
        offset (int): The starting point for pagination (default is 0).

    Returns:
        Dict[str, Union[int, List[APIReadResponse]]]: A dictionary containing total count and a list of
        responses with shortened URLs.
    """
    try:
        total_count, urls = await fetch_multiple_urls(
            owner_id=credentials["sub"], limit=limit, offset=offset
        )
        # Convert URL instances to strings if necessary
        response_data = {
            "total": total_count,
            "urls": [
                url.model_dump() for url in urls
            ],  # Ensure URLs are serialized to dicts
        }
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{key}")
async def delete_shortened_url(
    key: str,
    credentials: HTTPAuthorizationCredentials = Depends(auth.verify),
) -> APIDeleteResponse:
    """
    Delete a shortened URL from the database.

    Args:
        key (str): The unique key associated with the shortened URL.
        credentials (HTTPAuthorizationCredentials): The credentials of the authenticated user.

    Returns:
        APIDeleteResponse: A response indicating the result of the deletion operation.
    """
    # Remove the record associated with the key for the authenticated user
    await remove_record(key=key, owner_id=credentials["sub"])

    # Return a response indicating successful deletion
    return APIDeleteResponse()
