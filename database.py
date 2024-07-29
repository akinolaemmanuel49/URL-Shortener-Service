from databases import Database

from settings import settings

PG_DSN: str = (
    f"postgres+asyncpg://{settings.PG_USERNAME}:{settings.PG_PASSWORD}@{settings.PG_HOST}/{settings.PG_DATABASE_NAME}"
)

database = Database(PG_DSN)
