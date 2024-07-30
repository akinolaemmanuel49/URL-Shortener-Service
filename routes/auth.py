from fastapi import APIRouter, Depends, Security
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
import requests

from settings import settings
from utils import VerifyToken

router = APIRouter(prefix=f"{settings.BASE_URL}/auth", tags=["auth"])
auth = VerifyToken()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.TOKEN_URI}")
bearer_scheme = HTTPBearer()

@router.get("/login", include_in_schema=False)
def login():
    return RedirectResponse(
        f"https://{settings.AUTH0_DOMAIN}/authorize"
        "?response_type=code"
        f"&client_id={settings.AUTH0_CLIENT_ID}"
        f"&redirect_uri={settings.TOKEN_URI}"
        "&scope=offline_access openid profile email"
        f"&audience=https://shortenapi.com"
    )

@router.get("/logout", include_in_schema=False)
def logout():
    return RedirectResponse(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout"
        f"?client_id={settings.AUTH0_CLIENT_ID}"
        f"&returnTo={settings.LOGOUT_REDIRECT_URI}"
    )

@router.get("/token")
def get_access_token(code:str):
    payload = (
        "grant_type=authorization_code"
        f"&client_id={settings.AUTH0_CLIENT_ID}"
        f"&client_secret={settings.AUTH0_CLIENT_SECRET}"
        f"&code={code}"
        f"&redirect_uri={settings.TOKEN_URI}"
    )
    headers = {"content-type": "application/x-www-form-urlencoded"}
    response = requests.post(f"https://{settings.AUTH0_DOMAIN}/oauth/token", payload, headers=headers)
    return response.json()

# Test Endpoint
@router.get("/private")
def private(credentials: HTTPAuthorizationCredentials = Depends(auth.verify)):
    return {"message": "This is a protected endpoint", "user": credentials}