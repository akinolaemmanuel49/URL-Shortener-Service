from pydantic import BaseModel, HttpUrl


class APIReadResponse(BaseModel):
    """
    Represents the response for reading a URL.

    Attributes:
        shortened_url (HttpUrl): The shortened version of the original URL.
        original_url (HttpUrl): The original URL before shortening.
    """

    shortened_url: HttpUrl  # The shortened version of the original URL.
    original_url: HttpUrl  # The original URL before shortening.


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
