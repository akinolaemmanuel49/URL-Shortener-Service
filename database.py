from databases import Database
from settings import settings

# PostgreSQL Data Source Name (DSN) for connecting to the database
PG_DSN: str = (
    f"postgresql+asyncpg://{settings.PG_USERNAME}:{settings.PG_PASSWORD}@{settings.PG_HOST}/{settings.PG_DATABASE_NAME}"
)

# Initialize the database connection
database = Database(PG_DSN)

async def create_tables(database: Database):
    """
    Create tables in the database if they do not already exist.

    Args:
        database (Database): The database connection object.
    """
    # SQL query to create the 'urls' table if it does not exist
    query = """
    CREATE TABLE IF NOT EXISTS urls (
        key VARCHAR(6) PRIMARY KEY, 
        original_url TEXT NOT NULL, 
        owner_id VARCHAR(255) NOT NULL, 
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    )
    """
    # Execute the query to create the table
    await database.execute(query=query)

# Pydantic models (if needed)
from pydantic import BaseModel, HttpUrl

class Url(BaseModel):
    """
    Pydantic model for URL data.

    Attributes:
        original_url (HttpUrl): The original URL to be shortened.
        owner_id (str): The ID of the owner/user who owns the URL.
    """
    original_url: HttpUrl
    owner_id: str
