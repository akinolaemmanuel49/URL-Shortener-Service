from databases import Database

from settings import settings

# PostgreSQL DSN
PG_DSN: str = (
    f"postgresql+asyncpg://{settings.PG_USERNAME}:{settings.PG_PASSWORD}@{settings.PG_HOST}/{settings.PG_DATABASE_NAME}"
)

# Initialize the database
database = Database(PG_DSN)


async def create_tables(database: Database):
    """Create tables

    Args:
        database (Database): database object.
    """
    query = """CREATE TABLE IF NOT EXISTS urls (key VARCHAR(6) , original_url TEXT NOT NULL, owner_id VARCHAR(255) NOT NULL, created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP)"""
    await database.execute(query=query)


# Pydantic models (if needed)
from pydantic import BaseModel, HttpUrl


class Url(BaseModel):
    original_url: HttpUrl
    owner_id: str
