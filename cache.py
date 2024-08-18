from pydantic import HttpUrl
import redis.asyncio as redis

from settings import settings


class RedisClient:
    def __init__(self, **kwargs) -> None:
        # self.redis_url = f"redis://{kwargs.get('username')}:{kwargs.get('password')}@{kwargs.get('host')}:{kwargs.get('port')}"
        self.username: str = kwargs.get("username")
        self.password: str = kwargs.get("password")
        self.host: str = kwargs.get("host")
        self.port: int = kwargs.get("port")
        self.db: str = kwargs.get("db")
        self.redis = None

    async def connect(self) -> None:
        # self.redis = await redis.from_url(
        #     self.redis_url, encoding="utf-8", decode_responses=True
        # )
        self.redis = await redis.Redis(
            host=self.host,
            port=self.port,
            password=self.password,
            username=self.username,
            db=self.db,
        )

    async def set_value(self, key: str, value: str) -> None:
        await self.redis.set(key, value)

    async def get_value(self, key: str) -> str:
        url = await self.redis.get(key)
        return url

    async def disconnect(self) -> None:
        await self.redis.close()


cache = RedisClient(
    username=settings.CACHE_USERNAME,
    password=settings.CACHE_PASSWORD,
    host=settings.CACHE_HOST,
    port=settings.CACHE_PORT,
    db=settings.CACHE_DB,
)
