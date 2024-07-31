from pydantic import BaseModel

class Info(BaseModel):
    """
    Represents the configuration settings for an application.
    
    Attributes:
        app_name (str): The name of the application.
        admin_email (str): The email address of the application administrator.
        items_per_page (int): The number of items to be displayed per page.
        database (str): The database connection string or name.
    """

    app_name: str  # The name of the application, used for display and identification.
    admin_email: str  # The email address of the application administrator, used for administrative contact.
    items_per_page: int  # The default number of items to be displayed per page in paginated views.
    database: str  # The database connection string or name used for connecting to the application's database.
