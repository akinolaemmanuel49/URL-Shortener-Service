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
    _query = """SELECT key FROM urls WHERE original_url = :original_url AND owner_id = :owner_id"""
    _values = {"original_url": str(original_url), "owner_id": owner_id}

    try:
        result = await db.fetch_one(query=_query, values=_values)
        return result
    except Exception as e:
        print(f"An error occurred: {e}")


async def fetch_original_url(key: str) -> Optional[HttpUrl]:
    """
    Retrieve the original URL associated with a given key.

    Args:
        key (str): The shortened URL key.

    Returns:
        Optional[HttpUrl]: The original URL if found, None otherwise.
    """
    _query = """SELECT original_url FROM urls WHERE key = :key"""
    _values = {"key": key}

    try:
        result = await db.fetch_one(query=_query, values=_values)
        if result:
            return HttpUrl(result["original_url"])
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {e}")


async def fetch_multiple_urls(owner_id: str, limit: int = 10, offset: int = 0):
    """
    Fetch multiple URLs associated with a given owner ID, with pagination.

    Args:
        owner_id (str): The ID of the owner.
        limit (int, optional): The maximum number of records to return. Defaults to 10.
        offset (int, optional): The number of records to skip. Defaults to 0.

    Returns:
        Tuple[int, List[APIReadResponse]]: A tuple where the first element is the total count of matching rows,
                                           and the second element is a list of APIReadResponse objects containing
                                           shortened and original URLs.
    """
    _count_query = """
        SELECT COUNT(*) AS total_count 
        FROM urls 
        WHERE owner_id = :owner_id
    """

    _records_query = """
        SELECT key, original_url 
        FROM urls 
        WHERE owner_id = :owner_id 
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset 
    """

    _count_values = {"owner_id": owner_id}
    _record_values = {"owner_id": owner_id, "limit": limit, "offset": offset}

    try:
        count_result = await db.fetch_one(query=_count_query, values=_count_values)
        total_count: int = count_result["total_count"]

        records = await db.fetch_all(query=_records_query, values=_record_values)

        result = [
            APIReadResponse(
                shortened_url=f"{settings.SHORTENED_URL_BASE}{record['key']}",
                original_url=record["original_url"],
            )
            for record in records
        ]

        return total_count, result
    except Exception as e:
        print(f"An error occurred: {e}")


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
    _query_select = """SELECT key FROM urls WHERE original_url = :original_url AND owner_id = :owner_id"""
    _values_select = {"original_url": str(original_url), "owner_id": owner_id}

    try:
        existing_url = await db.fetch_one(query=_query_select, values=_values_select)

        if existing_url:
            # If the URL exists, return the existing shortened key
            return (str(existing_url["key"]), False)

        # Otherwise, store the key and URL value in the database
        _query_insert = """INSERT INTO urls (key, original_url, owner_id) VALUES (:key, :original_url, :owner_id)"""
        _values_insert = {
            "key": unique_key,
            "original_url": str(original_url),
            "owner_id": owner_id,
        }

        try:
            await db.execute(query=_query_insert, values=_values_insert)
            return (unique_key, True)
        except Exception as e:
            print(f"An error occurred: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")


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
    _query = """SELECT key, original_url FROM urls WHERE key = :key AND owner_id = :owner_id"""
    _values = {"key": key, "owner_id": owner_id}

    try:
        existing_url = await db.fetch_one(query=_query, values=_values)

        if existing_url:
            # If the URL exists, delete it
            _query = """DELETE FROM urls WHERE key = :key"""
            _values = {"key": key}

            try:
                await db.execute(query=_query, values=_values)
                return True
            except Exception as e:
                print(f"An error occurred: {e}")

        return False

    except Exception as e:
        print(f"An error occurred: {e}")


async def set_metrics(key: str, **kwargs):
    _query_select = """SELECT owner_id FROM urls WHERE key = :key;"""
    _values_select = {"key": key}

    try:
        result = await db.fetch_one(query=_query_select, values=_values_select)

        if result:
            owner_id = str(result["owner_id"])

            _query_insert = """INSERT INTO metrics (key, owner_id, client_ip, response_time) VALUES (:key, :owner_id, :client_ip, :response_time);"""
            _values_insert = {
                "key": key,
                "owner_id": owner_id,
                "client_ip": kwargs["client_ip"],
                "response_time": kwargs["response_time"],
            }

            try:
                await db.execute(query=_query_insert, values=_values_insert)
            except Exception as e:
                print(f"An error occurred: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")


async def count_hits(key: str):
    """
    Counts the number of times a shortened URL was resolved

    Args:
        key (str): The shortened URL key.
    """
    _query = """SELECT COUNT(*) AS total_number_of_hits FROM urls WHERE key = :key;"""
    _values = {"key": key}

    try:
        count_result = await db.execute(query=_query, values=_values)
        total_number_of_hits: int = count_result["total_number_of_hits"]
        return total_number_of_hits
    except Exception as e:
        print(f"An error occurred: {e}")


async def count_unique_ips(key: str):
    pass


async def evaluate_performance(key: str):
    pass


async def get_metrics(key: str):
    pass
