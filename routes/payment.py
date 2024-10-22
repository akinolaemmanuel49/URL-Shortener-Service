import logging
from fastapi import APIRouter, HTTPException, status
from square.client import Client
from square.exceptions.api_exception import APIException
from uuid import uuid4

from schemas.payment import PaymentRequest
from settings import settings

router = APIRouter(prefix=f"{settings.BASE_URL_PATH}/payment", tags=["payments"])

# Initialize Square Client
square_client = Client(
    access_token=settings.SQUARE_ACCESS_TOKEN,
    environment=settings.SQUARE_ENVIRONMENT,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/create")
async def create_payment(payment_request: PaymentRequest):
    try:
        # Log received request data
        print(f"Received payment request: {payment_request}")
        logger.info(f"Payment Request Data: {payment_request.dict()}")

        # Build the Square payment payload
        payment_payload = {
            "source_id": payment_request.source_id,
            "amount_money": {
                "amount": payment_request.amount,
                "currency": "USD",
            },
            "idempotency_key": str(uuid4()),  # Unique key per request
        }

        # Log the payload sent to Square API
        print(f"Sending payment payload: {payment_payload}")
        logger.info(f"Payment Payload: {payment_payload}")

        # Make the Square API request
        result = square_client.payments.create_payment(payment_payload)

        # Log the Square API response
        if result.is_success():
            logger.info(f"Payment Success: {result.body}")
            return {"status": "success", "payment": result.body}
        else:
            logger.error(f"Payment Failed: {result.errors}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=result.errors
            )
    except APIException as e:
        logger.exception(f"Square API Exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
