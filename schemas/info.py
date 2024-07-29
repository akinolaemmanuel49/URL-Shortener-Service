from pydantic import BaseModel


class Info(BaseModel):
    app_name: str
    admin_email: str
    items_per_page: int
    database: str
