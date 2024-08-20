from typing import Dict, Optional, Tuple, List
from pydantic import HttpUrl
from databases.interfaces import Record

from database import database as db
from schemas.url import APIReadResponse
from settings import settings
from cache import cache
from logger import logger


async def fetch_key(original_url: HttpUrl, owner_id: str) -> Optional[Record]:
    """
    Retrieve the key associated with a given original URL and owner ID.

    Args:
        original_url (HttpUrl): The original URL.
        owner_id (str): The ID of the owner.

    Returns:
        Optional[Record]: The database record containing the key if found, None otherwise.
    """
    _query = """SELECT key FROM urls WHERE original_url = :original_url AND owner_id = :owner_id"""
    _values = {"original_url": str(original_url), "owner_id": owner_id}

    try:
        result = await db.fetch_one(query=_query, values=_values)
        return result
    except Exception as e:
        logger.error(f"An error occurred while fetching the key: {e}")
        return None


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
        await cache.connect()

        try:
            cached_result = await cache.get_value(key)
            # If cache hit return fetch from cache
            if cached_result:
                logger.info(f"Cache hit on key: {key}")
                return HttpUrl(cached_result)

            # If cache miss fetch from database, then save to cache
            logger.info(f"Cache miss on key: {key}")
            logger.info("Fetching from datbase")
            result = await db.fetch_one(query=_query, values=_values)
            if result:
                await cache.set_value(key=key, value=str(result["original_url"]))
                return HttpUrl(result["original_url"])
            else:
                return None
        except Exception as e:
            logger.error(f"An error occurred while fetching the original URL: {e}")

    except Exception as e:
        logger.error(f"An error occurred while connecting to redis server: {e}")
    finally:
        await cache.disconnect()


async def fetch_multiple_urls(
    owner_id: str, limit: int = 10, offset: int = 0
) -> Tuple[int, List[APIReadResponse]]:
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
    _count_query = (
        """SELECT COUNT(*) AS total_count FROM urls WHERE owner_id = :owner_id"""
    )
    _records_query = """SELECT key, original_url FROM urls WHERE owner_id = :owner_id ORDER BY created_at DESC LIMIT :limit OFFSET :offset"""
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
        logger.error(f"An error occurred while fetching multiple URLs: {e}")
        return 0, []


async def create_record(
    original_url: HttpUrl, owner_id: str, unique_key: str
) -> Tuple[str, bool]:
    """
    Create a new URL record in the database.

    Args:
        original_url (HttpUrl): The original URL to be shortened.
        owner_id (str): The ID of the owner.
        unique_key (str): The unique key for the shortened URL.

    Returns:
        Tuple[str, bool]: The unique key and a boolean indicating if a new record was created.
    """
    _query_select = """SELECT key FROM urls WHERE original_url = :original_url AND owner_id = :owner_id"""
    _values_select = {"original_url": str(original_url), "owner_id": owner_id}

    try:
        existing_url = await db.fetch_one(query=_query_select, values=_values_select)

        if existing_url:
            return str(existing_url["key"]), False

        _query_insert = """INSERT INTO urls (key, original_url, owner_id) VALUES (:key, :original_url, :owner_id)"""
        _values_insert = {
            "key": unique_key,
            "original_url": str(original_url),
            "owner_id": owner_id,
        }

        await db.execute(query=_query_insert, values=_values_insert)
        return unique_key, True
    except Exception as e:
        logger.error(f"An error occurred while creating a record: {e}")


async def remove_record(key: str, owner_id: str) -> bool:
    """
    Remove a URL record from the database.

    Args:
        key (str): The shortened URL key.
        owner_id (str): The ID of the owner.

    Returns:
        bool: True if the record was deleted, False otherwise.
    """
    _query = """SELECT key, original_url FROM urls WHERE key = :key AND owner_id = :owner_id"""
    _values = {"key": key, "owner_id": owner_id}

    try:
        existing_url = await db.fetch_one(query=_query, values=_values)

        if existing_url:
            _query_delete = """DELETE FROM urls WHERE key = :key"""
            _values_delete = {"key": key}

            try:
                await db.execute(query=_query_delete, values=_values_delete)
                return True
            except Exception as e:
                logger.error(f"An error occurred while deleting the record: {e}")
                return False

        return False

    except Exception as e:
        logger.error(f"An error occurred while removing a record: {e}")


async def set_metrics(key: str, **kwargs):
    """
    Set metrics related to the shortened URL.

    Args:
        key (str): The shortened URL key.
        **kwargs: Additional keyword arguments, including 'client_ip' and 'response_time'.
    """
    _query_select = """SELECT owner_id FROM urls WHERE key = :key"""
    _values_select = {"key": key}

    try:
        result = await db.fetch_one(query=_query_select, values=_values_select)

        if result:
            owner_id = str(result["owner_id"])

            _query_insert = """INSERT INTO metrics (key, owner_id, client_ip, response_time) VALUES (:key, :owner_id, :client_ip, :response_time)"""
            _values_insert = {
                "key": key,
                "owner_id": owner_id,
                "client_ip": kwargs.get("client_ip"),
                "response_time": kwargs.get("response_time"),
            }

            try:
                await db.execute(query=_query_insert, values=_values_insert)
            except Exception as e:
                logger.error(f"An error occurred while setting metrics: {e}")

    except Exception as e:
        logger.error(f"An error occurred while fetching owner_id for metrics: {e}")


async def get_average_resolution_time_by_key(key: str) -> int:
    """
    Calculate the average resolution time for a specific shortened URL key.

    Args:
        key (str): The shortened URL key.

    Returns:
        int: The average resolution time in milliseconds.
    """

    _query_select = """SELECT AVG(response_time) FROM metrics WHERE key = :key"""
    _values_select = {"key": key}

    try:
        result = await db.execute(query=_query_select, values=_values_select)
        return result
    except Exception as e:
        logger.error(
            f"An error occurred while calculating average resolution time for key => {key}: {e}"
        )


async def get_average_resolution_time_by_owner(owner_id: str) -> int:
    """
    Calculate the average resolution time for all URLs owned by a specific user.

    Args:
        owner_id (str): The ID of the owner.

    Returns:
        int: The average resolution time in milliseconds.
    """

    _query_select = (
        """SELECT AVG(response_time) FROM metrics WHERE owner_id = :owner_id"""
    )
    _values_select = {"owner_id": owner_id}

    try:
        result = await db.execute(query=_query_select, values=_values_select)
        return result
    except Exception as e:
        logger.error(
            f"An error occurred while calculating average resolution time for a user account: {e}"
        )


async def count_hits(key: str) -> int:
    """
    Counts the number of times a shortened URL was resolved.

    Args:
        key (str): The shortened URL key.

    Returns:
        int: The total number of hits for the given key.
    """
    _query = """SELECT COUNT(*) AS total_number_of_hits FROM metrics WHERE key = :key"""
    _values = {"key": key}

    try:
        count_result = await db.fetch_one(query=_query, values=_values)
        total_number_of_hits: int = count_result["total_number_of_hits"]
        return total_number_of_hits
    except Exception as e:
        logger.error(f"An error occurred while counting hits: {e}")
        return 0


async def count_top_five_hits(owner_id: str) -> Dict[str, int]:
    """
    Retrieve the top five most hit shortened URLs for a specific owner.

    Args:
        owner_id (str): The ID of the owner whose URLs are being queried.

    Returns:
        Dict[str, int]: A dictionary where keys are shortened URL keys and values are the number of hits.
    """
    _query = """
    SELECT key, COUNT(*) AS total_hits
    FROM metrics
    WHERE owner_id = :owner_id
    GROUP BY key
    ORDER BY total_hits DESC
    LIMIT 5
    """

    try:
        results = await db.fetch_all(query=_query, values={"owner_id": owner_id})
        top_hits = {result["key"]: result["total_hits"] for result in results}
        return top_hits
    except Exception as e:
        logger.error(f"An error occurred while counting the top five hits: {e}")
        return {}


async def count_unique_ips(key: str) -> int:
    """
    Counts the number of unique IP addresses that accessed a shortened URL.

    Args:
        key (str): The shortened URL key.

    Returns:
        int: The number of unique IPs.
    """
    _query = """SELECT COUNT(DISTINCT client_ip) AS unique_ip_count FROM metrics WHERE key = :key"""
    _values = {"key": key}

    try:
        count_result = await db.fetch_one(query=_query, values=_values)
        unique_ip_count: int = count_result["unique_ip_count"]
        return unique_ip_count
    except Exception as e:
        logger.error(f"An error occurred while counting unique IPs: {e}")
        return 0


async def evaluate_performance(key: str) -> Optional[dict]:
    """
    Evaluate performance metrics for a shortened URL.

    Args:
        key (str): The shortened URL key.

    Returns:
        Optional[dict]: A dictionary with performance metrics or None if an error occurs.
    """
    try:
        total_hits = await count_hits(key)
        unique_ips = await count_unique_ips(key)
        avg_resolution_time = await get_average_resolution_time_by_key(key=key)

        performance = {
            "total_hits": total_hits,
            "unique_ips": unique_ips,
            "avg_resolution_time": avg_resolution_time,
        }

        return performance
    except Exception as e:
        logger.error(f"An error occurred while evaluating performance: {e}")
        return None


async def get_metrics(key: str) -> Optional[dict]:
    """
    Retrieve metrics for a shortened URL.

    Args:
        key (str): The shortened URL key.

    Returns:
        Optional[dict]: A dictionary with metrics or None if an error occurs.
    """
    try:
        hits = await count_hits(key)
        unique_ips = await count_unique_ips(key)

        metrics = {"hits": hits, "unique_ips": unique_ips}

        return metrics
    except Exception as e:
        logger.error(f"An error occurred while retrieving metrics: {e}")
        return None
