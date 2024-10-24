from datetime import datetime, timedelta
import logging
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from square.exceptions.api_exception import APIException

from dal import subscribe as dal_subscribe
from settings import settings
from utils import get_square_client, VerifyToken
from logger import logger

router = APIRouter(
    prefix=f"{settings.BASE_URL_PATH}/subscriptions", tags=["subscriptions"]
)
auth = VerifyToken()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.TOKEN_URI}")
bearer_scheme = HTTPBearer()


@router.post("/pay")
async def subscribe(
    req: dict,
    credentials: HTTPAuthorizationCredentials = Depends(auth.verify),
):
    print(req)
    square_client = get_square_client(settings=settings)
    amount = 300 if req["plan_type"] == "standard" else 500  # In cents (USD)
    try:
        # Log received request data
        logger.info(
            f"Payment Request Data: source_id={req['source_id']}, plan_type={req['plan_type']}"
        )

        # Build the Square payment payload
        payment_payload = {
            "source_id": req["source_id"],
            "amount_money": {
                "amount": amount,
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
            start_date = datetime.now()
            end_date = start_date + timedelta(days=30)  # 1-month subscription
            owner_id = credentials["sub"]
            await dal_subscribe(
                owner_id=owner_id,
                plan_type=req['plan_type'],
                start_date=start_date,
                end_date=end_date,
            )
            return {"status": "success", "payment": result.body}
        else:
            logger.error(f"Payment Failed: {result.errors}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=result.errors
            )
    except APIException as e:
        logger.exception(f"Square API Exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment service is currently unavailable.",
        )
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your payment.",
        )
