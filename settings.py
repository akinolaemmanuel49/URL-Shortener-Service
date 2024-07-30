from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", ".local.env", ".env.prod"))

    VERSION: str = "v1"
    BASE_URL: str = f"/api/{VERSION}"
    TOKEN_URI: str = f"http://localhost:8000{BASE_URL}/auth/token"
    LOGOUT_REDIRECT_URI: str = f"http://localhost:8000{BASE_URL}/info"
    APP_SECRET_KEY: str

    # Application details
    APP_NAME: str = "Shorten API"
    ADMIN_EMAIL: str
    ITEMS_PER_PAGE: int = 10
    DATABASE: str

    # Database information
    PG_USERNAME: str
    PG_PASSWORD: str
    PG_DATABASE_NAME: str
    PG_HOST: str

    # Auth0 details
    AUTH0_DOMAIN: str
    AUTH0_CLIENT_ID: str
    AUTH0_CLIENT_SECRET: str
    AUTH0_ALGORITHMS: str
    AUTH0_API_AUDIENCE: str
    AUTH0_ISSUER: str


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
