from pydantic import BaseModel, HttpUrl


class APIReadResponse(BaseModel):
    shortened_url: HttpUrl
    original_url: HttpUrl

class APICreateResponse(BaseModel):
    shortened_url: HttpUrl
    original_url: HttpUrl
    created: bool

class APIDeleteResponse(BaseModel):
    message: str = "successfully deleted"
