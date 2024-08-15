import logging

from logging.handlers import RotatingFileHandler
from uvicorn.config import LOGGING_CONFIG

# Get the default FastAPI logger (used by Uvicorn)
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)
LOGGING_CONFIG["formatters"]["default"][
    "fmt"
] = "%(asctime)s %(levelprefix)s %(message)s"

LOGGING_CONFIG["formatters"]["access"][
    "fmt"
] = "%(asctime)s %(levelprefix)s %(message)s"

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Create a file handler
file_handler = RotatingFileHandler("app.log", maxBytes=10000, backupCount=3)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Add file handler to logging handlers
logger.addHandler(file_handler)
