import requests
import time

from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse

from dal import set_metrics
from utils import URLShortener

# Initialize the API router
router = APIRouter()


@router.get("/{key}", include_in_schema=False)
async def resolve_url(request: Request, key: str) -> RedirectResponse:
    """
    Resolve the shortened URL to its original URL and redirect to it.

    Args:
        request (Request): The FastAPI request object to retrieve client IP address.
        key (str): The unique key associated with the shortened URL.

    Returns:
        RedirectResponse: A response that redirects the client to the original URL.
    """
    # Measure the start time
    start_time = time.time()

    # Retrieve the original URL associated with the provided key
    original_url = await URLShortener.retrieve_original_url(key=key)
    if not original_url:
        return Response("URL not found", status_code=404)

    # Get the client IP address
    client_ip = request.client.host

    # Check for X-Forwarded-For header for proxies
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(",")[0].strip()

    # Query ipinfo.io to get geolocation data
    # For testing purposes set client_ip to a public address
    client_ip = "8.8.8.8"
    ipinfo_url = f"https://ipinfo.io/{client_ip}/json"
    try:
        response = requests.get(ipinfo_url)
        ip_info = response.json()
        country = ip_info.get("country", "Unknown")
        region = ip_info.get("region", "Unknown")
        city = ip_info.get("city", "Unknown")
    except Exception as e:
        country = "Unknown"
        region = "Unknown"
        city = "Unknown"

    # Calculate the response time
    response_time = int((time.time() - start_time) * 1000)  # Time in milliseconds

    # Store metrics in a dictionary
    metrics = {
        "client_ip": client_ip,
        "response_time": response_time,
        "country": country,
        "region": region,
        "city": city,
    }

    try:
        # Store metrics in a database
        await set_metrics(key=key, **metrics)
    except Exception as e:
        print(e)

    

    # Redirect the client to the original URL
    return RedirectResponse(url=original_url)
