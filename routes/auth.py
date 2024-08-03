from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
import requests

from settings import settings
from utils import VerifyToken

router = APIRouter(prefix=f"{settings.BASE_URL_PATH}/auth", tags=["auth"])
auth = VerifyToken()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.TOKEN_URI}")
bearer_scheme = HTTPBearer()


@router.get("/login", include_in_schema=False)
def login():
    """
    Redirects the user to the Auth0 login page.

    This endpoint handles the user login by redirecting them to the Auth0 login page,
    where they can authenticate themselves. The redirect URI and client ID are included
    in the URL to specify where the user should be redirected after successful authentication.
    """
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
    """
    Redirects the user to the Auth0 logout page.

    This endpoint handles the user logout by redirecting them to the Auth0 logout page,
    where their session will be terminated. The client ID and return URL are included
    in the URL to specify where the user should be redirected after logout.
    """
    return RedirectResponse(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout"
        f"?client_id={settings.AUTH0_CLIENT_ID}"
        f"&returnTo={settings.LOGOUT_REDIRECT_URI}"
    )


@router.get("/token", include_in_schema=False)
def get_access_token(code: str):
    """
    Exchanges the authorization code for an access token.

    This endpoint handles the token exchange process. It receives the authorization
    code from the Auth0 login response and exchanges it for an access token by making
    a POST request to the Auth0 token endpoint.

    Args:
        code (str): The authorization code received from Auth0 after successful login.

    Returns:
        JSON response containing the access token and other token details.
    """
    payload = (
        "grant_type=authorization_code"
        f"&client_id={settings.AUTH0_CLIENT_ID}"
        f"&client_secret={settings.AUTH0_CLIENT_SECRET}"
        f"&code={code}"
        f"&redirect_uri={settings.TOKEN_URI}"
    )
    headers = {"content-type": "application/x-www-form-urlencoded"}
    response = requests.post(
        f"https://{settings.AUTH0_DOMAIN}/oauth/token", payload, headers=headers
    )
    return response.json()
