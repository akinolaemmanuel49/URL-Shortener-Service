from pydantic import BaseModel, HttpUrl


class APIReadOriginalURLResponse(BaseModel):
    """
    Represents the response for reading a URL.

    Attributes:
        original_url (HttpUrl): The original URL before shortening.
    """

    original_url: HttpUrl  # The original URL before shortening.


class APIReadResponse(APIReadOriginalURLResponse):
    """
    Represents the response for reading a URL.

    Inherits Attributes:
        original_url (HttpUrl): The original URL before shortening.

    Additional Attributes:
        shortened_url (HttpUrl): The shortened version of the original URL.
    """

    shortened_url: HttpUrl  # The shortened version of the original URL.


class APICreateResponse(BaseModel):
    """
    Represents the response for creating a shortened URL.

    Attributes:
        shortened_url (HttpUrl): The newly created shortened URL.
        original_url (HttpUrl): The original URL that was shortened.
        created (bool): Indicates whether the URL was newly created or already existed.
    """

    shortened_url: HttpUrl  # The newly created shortened URL.
    original_url: HttpUrl  # The original URL that was shortened.
    created: bool  # Indicates whether the URL was newly created or already existed.


class APIDeleteResponse(BaseModel):
    """
    Represents the response for deleting a shortened URL.

    Attributes:
        message (str): The result message of the delete operation.
    """

    message: str = "successfully deleted"  # The result message of the delete operation.
