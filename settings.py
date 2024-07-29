from pydantic import BaseModel, PostgresDsn

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", ".local.env", ".env.prod"))

    VERSION: str = "v1"
    BASE_URL: str = f"/api/{VERSION}"

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


settings = Settings()
