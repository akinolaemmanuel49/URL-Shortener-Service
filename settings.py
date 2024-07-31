from functools import lru_cache
from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings class to manage application configurations, including database and Auth0 details.

    Attributes:
        VERSION (str): The version of the application.
        BASE_URL_PATH (str): The base URL path for the API.
        SHORTENED_URL_BASE (HttpUrl): The base URL for shortened URLs.
        TOKEN_URI (HttpUrl): The URI for token retrieval.
        LOGOUT_REDIRECT_URI (HttpUrl): The URI to redirect to after logout.
        APP_SECRET_KEY (str): The secret key for the application.
        APP_NAME (str): The name of the application.
        ADMIN_EMAIL (str): The admin email address.
        ITEMS_PER_PAGE (int): The number of items per page for pagination. Default is 10.
        DATABASE (str): The database connection string.
        PG_USERNAME (str): The PostgreSQL username.
        PG_PASSWORD (str): The PostgreSQL password.
        PG_DATABASE_NAME (str): The name of the PostgreSQL database.
        PG_HOST (str): The host of the PostgreSQL database.
        AUTH0_DOMAIN (str): The Auth0 domain.
        AUTH0_CLIENT_ID (str): The Auth0 client ID.
        AUTH0_CLIENT_SECRET (str): The Auth0 client secret.
        AUTH0_ALGORITHMS (str): The algorithms used by Auth0.
        AUTH0_API_AUDIENCE (str): The audience for the Auth0 API.
        AUTH0_ISSUER (str): The issuer for the Auth0 tokens.
    """

    model_config = SettingsConfigDict(env_file=(".env", ".local.env", ".env.prod"))

    VERSION: str
    BASE_URL_PATH: str
    SHORTENED_URL_BASE: HttpUrl
    TOKEN_URI: HttpUrl
    LOGOUT_REDIRECT_URI: HttpUrl
    APP_SECRET_KEY: str

    # Application details
    APP_NAME: str
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
def get_settings() -> Settings:
    """
    Retrieve the cached settings instance.

    Returns:
        Settings: The settings instance.
    """
    return Settings()


# Initialize the settings
settings = get_settings()
