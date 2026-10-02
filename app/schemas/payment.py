import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from app.models.payment import PaymentStatus


class PaymentSimulateRequest(BaseModel):
    booking_id: uuid.UUID
    # Client specifies simulation outcome; amount is never accepted from client
    simulated_status: PaymentStatus = PaymentStatus.SUCCESS


class PaymentResponse(BaseModel):
    id: uuid.UUID
    booking_id: uuid.UUID
    amount: Decimal
    status: PaymentStatus
    provider_reference: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
