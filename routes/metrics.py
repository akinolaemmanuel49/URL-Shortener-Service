from fastapi import APIRouter, Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)

from settings import settings
from dal import count_top_five_hits, evaluate_performance
from utils import VerifyToken

router = APIRouter(prefix=f"{settings.BASE_URL_PATH}/metrics", tags=["metrics"])
auth = VerifyToken()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.TOKEN_URI}")
bearer_scheme = HTTPBearer()


@router.get("/performance/{key}")
async def get_performance_for_key(
    key: str, credentials: HTTPAuthorizationCredentials = Depends(auth.verify)
):
    metrics_for_key = await evaluate_performance(key=key)
    return metrics_for_key


@router.get("/top")
async def get_top_urls(
    credentials: HTTPAuthorizationCredentials = Depends(auth.verify),
):
    top_five_hits = await count_top_five_hits(owner_id=credentials["sub"])
    return top_five_hits
