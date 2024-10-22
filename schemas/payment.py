from pydantic import BaseModel


class PaymentRequest(BaseModel):
    source_id: str
    amount: int
