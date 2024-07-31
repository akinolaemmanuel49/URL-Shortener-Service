from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from utils import URLShortener

# Initialize the API router
router = APIRouter()


@router.get("/{key}", include_in_schema=False)
async def resolve_url(key: str) -> str:
    """
    Resolve the shortened URL to its original URL and redirect to it.

    Args:
        key (str): The unique key associated with the shortened URL.

    Returns:
        RedirectResponse: A response that redirects the client to the original URL.
    """
    # Retrieve the original URL associated with the provided key
    original_url = await URLShortener.retrieve_original_url(key=key)

    # Redirect the client to the original URL
    return RedirectResponse(url=original_url)
