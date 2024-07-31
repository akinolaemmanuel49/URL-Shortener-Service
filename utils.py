import hashlib
from typing import Optional, Tuple
import jwt

from fastapi import HTTPException, status, Depends
from fastapi.security import SecurityScopes, HTTPAuthorizationCredentials, HTTPBearer
from pydantic import HttpUrl

from settings import get_settings
from dal import create_record, fetch_original_url


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str, **kwargs):
        """Custom exception for HTTP 403 Forbidden status."""
        super().__init__(status.HTTP_403_FORBIDDEN, detail=detail)


class UnauthenticatedException(HTTPException):
    def __init__(self):
        """Custom exception for HTTP 401 Unauthorized status."""
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Requires authentication"
        )


class VerifyToken:
    """Class to verify JWT tokens using PyJWT."""

    def __init__(self):
        self.config = get_settings()

        # URL to retrieve JSON Web Key Set (JWKS) from Auth0
        jwks_url = f"https://{self.config.AUTH0_DOMAIN}/.well-known/jwks.json"
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    async def verify(
        self,
        security_scopes: SecurityScopes,
        token: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer()),
    ):
        """
        Verify the provided JWT token.

        Args:
            security_scopes (SecurityScopes): Security scopes required.
            token (Optional[HTTPAuthorizationCredentials]): Bearer token to verify.

        Raises:
            UnauthenticatedException: If the token is not provided.
            UnauthorizedException: If the token cannot be verified.

        Returns:
            dict: Decoded JWT payload.
        """
        if token is None:
            raise UnauthenticatedException()

        # Get the signing key from the JWKS endpoint
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(
                token.credentials
            ).key
        except jwt.exceptions.PyJWKClientError as error:
            raise UnauthorizedException(str(error))
        except jwt.exceptions.DecodeError as error:
            raise UnauthorizedException(str(error))

        # Decode the JWT token using the signing key
        try:
            payload = jwt.decode(
                token.credentials,
                signing_key,
                algorithms=self.config.AUTH0_ALGORITHMS,
                audience=self.config.AUTH0_API_AUDIENCE,
                issuer=self.config.AUTH0_ISSUER,
            )
        except Exception as error:
            raise UnauthorizedException(str(error))

        return payload


class URLShortener:
    """Class to shorten URLs using Key-Value pairs."""

    def __init__(
        self, original_url: Optional[HttpUrl] = None, owner_id: Optional[str] = None
    ):
        self.original_url = original_url
        self.owner_id = owner_id

    async def shorten_url(self) -> Tuple[str, bool]:
        """
        Generate a unique key for the URL using a hash function and store it in the database.

        Returns:
            Tuple[str, bool]: The unique key and a boolean indicating whether a new record was created.
        """
        unique_key = self._generate_key(str(self.original_url), self.owner_id)

        try:
            result = await create_record(
                original_url=self.original_url,
                owner_id=self.owner_id,
                unique_key=unique_key,
            )
            return result
        except Exception as e:
            raise e

    @staticmethod
    async def retrieve_original_url(key: str) -> Optional[HttpUrl]:
        """
        Retrieve the original URL using the hashed key.

        Args:
            key (str): Hashed URL string.

        Returns:
            Optional[HttpUrl]: Original URL if found, otherwise None.
        """
        result = await fetch_original_url(key=key)
        return result

    def _generate_key(self, original_url: str, owner_id: str) -> str:
        """
        Create a unique key using a hash function.

        Args:
            original_url (str): The original URL to be hashed.
            owner_id (str): The owner ID to include in the hash.

        Returns:
            str: Hashed URL string of length 6.
        """
        string = str(original_url + owner_id)
        hash_object = hashlib.md5(string.encode())
        return hash_object.hexdigest()[:6]
