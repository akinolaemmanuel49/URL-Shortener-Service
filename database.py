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
    # Enable the pgcrypto extension to use gen_random_uuid() for UUID generation
    extension = """CREATE EXTENSION IF NOT EXISTS pgcrypto"""

    # SQL query to create the 'urls' table if it does not exist
    urls_table_query = """
    CREATE TABLE IF NOT EXISTS urls (
        key VARCHAR(7) PRIMARY KEY, 
        original_url TEXT NOT NULL, 
        owner_id VARCHAR(255) NOT NULL, 
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP, 
    );
    """

    # SQL query to create the 'metrics' table if it does not exist
    metrics_table_query = """
    CREATE TABLE IF NOT EXISTS metrics (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
        key VARCHAR(7) NOT NULL REFERENCES urls(key) ON DELETE CASCADE, 
        owner_id VARCHAR(255) NOT NULL, 
        client_ip VARCHAR(45) NOT NULL, 
        response_time INTEGER NOT NULL,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );
    """

    try:
        # Execute the queries to create the tables
        await database.execute(query=urls_table_query)
        await database.execute(query=metrics_table_query)
    except Exception as e:
        print(f"An error occurred: {e}")


async def create_triggers(database: Database):
    # SQL query to create update_updated_at_column function
    update_function_query = """
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """

    # Check if trigger exists before creation
    check_update_trigger_query = """
    SELECT EXISTS (
        SELECT 1
        FROM pg_trigger
        WHERE tgname = 'update_urls_updated_at'
    );
    """

    # SQL query to create update_urls_updated_at trigger
    update_trigger_query = """
    CREATE TRIGGER update_urls_updated_at
    BEFORE UPDATE ON urls
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """

    try:
        # Execute query to create function
        await database.execute(update_function_query)

        # Check if trigger exists
        update_trigger_exists = await database.execute(check_update_trigger_query)

        # Create trigger if it does not exist
        if not update_trigger_exists:
            await database.execute(update_trigger_query)
    except Exception as e:
        print(f"An error occurred: {e}")


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

