from typing import Optional
from pydantic import HttpUrl
from databases.interfaces import Record

from database import database as db
from schemas.url import APIReadResponse
from settings import settings


async def fetch_key(original_url: HttpUrl, owner_id: str) -> Record:
    """
    Retrieve the key associated with a given original URL and owner ID.

    Args:
        original_url (HttpUrl): The original URL.
        owner_id (str): The ID of the owner.

    Returns:
        Record: The database record containing the key.
    """
    query = """SELECT key FROM urls WHERE original_url = :original_url AND owner_id = :owner_id"""
    values = {"original_url": str(original_url), "owner_id": owner_id}
    result = await db.fetch_one(query=query, values=values)
    return result


async def fetch_original_url(key: str) -> Optional[HttpUrl]:
    """
    Retrieve the original URL associated with a given key.

    Args:
        key (str): The shortened URL key.

    Returns:
        Optional[HttpUrl]: The original URL if found, None otherwise.
    """
    query = """SELECT original_url FROM urls WHERE key = :key"""
    result = await db.fetch_one(query=query, values={"key": key})
    if result:
        return HttpUrl(result["original_url"])
    else:
        return None


async def fetch_multiple_urls(owner_id: str, limit: int = 10, offset: int = 0):
    """
    Fetch multiple URLs associated with a given owner ID, with pagination.

    Args:
        owner_id (str): The ID of the owner.
        limit (int, optional): The maximum number of records to return. Defaults to 10.
        offset (int, optional): The number of records to skip. Defaults to 0.

    Returns:
        List[APIReadResponse]: A list of APIReadResponse objects containing shortened and original URLs.
    """
    query = """
        SELECT key, original_url 
        FROM urls 
        WHERE owner_id = :owner_id 
        ORDER BY created_at
        LIMIT :limit OFFSET :offset 
    """
    values = {"owner_id": owner_id, "limit": limit, "offset": offset}
    records = await db.fetch_all(query=query, values=values)

    result = []
    for record in records:
        result.append(
            APIReadResponse(
                shortened_url=f"{settings.SHORTENED_URL_BASE}{record['key']}",
                original_url=record["original_url"],
            )
        )

    return result


async def create_record(original_url: HttpUrl, owner_id: str, unique_key: str):
    """
    Create a new URL record in the database.

    Args:
        original_url (HttpUrl): The original URL to be shortened.
        owner_id (str): The ID of the owner.
        unique_key (str): The unique key for the shortened URL.

    Returns:
        Tuple[str, bool]: The unique key and a boolean indicating if a new record was created.
    """
    # Check if the URL already exists for the owner
    query_select = """SELECT key FROM urls WHERE original_url = :original_url AND owner_id = :owner_id"""
    values_select = {"original_url": str(original_url), "owner_id": owner_id}
    existing_url = await db.fetch_one(query=query_select, values=values_select)

    if existing_url:
        # If the URL exists, return the existing shortened key
        return (str(existing_url["key"]), False)

    # Otherwise, store the key and URL value in the database
    query_insert = """INSERT INTO urls (key, original_url, owner_id) VALUES (:key, :original_url, :owner_id)"""
    values_insert = {
        "key": unique_key,
        "original_url": str(original_url),
        "owner_id": owner_id,
    }
    await db.execute(query=query_insert, values=values_insert)
    return (unique_key, True)


async def remove_record(key: str, owner_id: str) -> bool:
    """
    Remove a URL record from the database.

    Args:
        key (str): The shortened URL key.
        owner_id (str): The ID of the owner.

    Returns:
        bool: True if the record was deleted, False otherwise.
    """
    # Check if the URL exists in the database
    query = """SELECT key, original_url FROM urls WHERE key = :key AND owner_id = :owner_id"""
    values = {"key": key, "owner_id": owner_id}
    existing_url = await db.fetch_one(query=query, values=values)

    if existing_url:
        # If the URL exists, delete it
        query = """DELETE FROM urls WHERE key = :key"""
        values = {"key": key}
        await db.execute(query=query, values=values)
        return True

    return False
