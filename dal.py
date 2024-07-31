from typing import Optional
from pydantic import HttpUrl

from database import database as db
from databases.interfaces import Record

from schemas.url import APIReadResponse
from settings import settings


async def fetch_key(original_url: HttpUrl, owner_id: str) -> Record:
    # Retrieve key from url using original_url and owner_id
    query = """SELECT key FROM urls WHERE original_url = :original_url AND owner_id = :owner_id"""
    values = {
        "original_url": str(original_url),
        "owner_id": owner_id,
    }

    result = await db.fetch_one(query=query, values=values)
    return result


async def fetch_original_url(key: str) -> Optional[HttpUrl]:
    # Retrieve original url from database using key.
    query = """SELECT original_url FROM urls WHERE key = :key"""
    result = await db.fetch_one(query=query, values={"key": key})
    if result:
        return HttpUrl(result["original_url"])
    else:
        return None


async def fetch_multiple_urls(owner_id: str, limit: int = 10, offset: int = 0):
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
        result.append(APIReadResponse(shortened_url=f"{settings.SHORTENED_URL_BASE}{record["key"]}", original_url=record["original_url"]))

    return result


async def create_record(original_url: HttpUrl, owner_id: str, unique_key: str):
    # Check if the key already exists in the database
    query_select = """SELECT key FROM urls WHERE original_url = :original_url AND owner_id = :owner_id"""
    values_select = {
        "original_url": str(original_url),
        "owner_id": owner_id,
    }
    existing_url = await db.fetch_one(query=query_select, values=values_select)

    if existing_url:
        # If the URL exists, return the existing shortened key
        return (str(existing_url["key"]), False)

    # Otherwise store the key and URL value in the database
    query_insert = """INSERT INTO urls (key, original_url, owner_id) VALUES (:key, :original_url, :owner_id)"""
    values_insert = {
        "key": unique_key,
        "original_url": str(original_url),
        "owner_id": owner_id,
    }
    await db.execute(query=query_insert, values=values_insert)
    return (unique_key, True)


async def remove_record(key: str, owner_id: str) -> bool:
    # Check if the key already exists in the database
    query = """SELECT key, original_url FROM urls WHERE key = :key AND owner_id = :owner_id"""
    values = {
        "key": key,
        "owner_id": owner_id,
    }
    existing_url = await db.fetch_one(query=query, values=values)

    if existing_url:
        # If the URL exists, delete it
        query = """DELETE FROM urls WHERE key = :key"""
        values = {
            "key": key,
        }
        await db.execute(query=query, values=values)
        return True
    return False
