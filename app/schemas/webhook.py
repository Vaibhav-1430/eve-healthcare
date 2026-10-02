from datetime import datetime
from pydantic import BaseModel, Field
from app.models.payment import PaymentStatus


class PaymentWebhookRequest(BaseModel):
    event_id: str = Field(min_length=1, description="Unique identifier for the external webhook event")
    payment_reference: str = Field(min_length=1, description="Provider reference corresponding to payment")
    status: PaymentStatus = Field(description="Final payment outcome: SUCCESS or FAILED")
    timestamp: datetime | str | None = None


class WebhookResponse(BaseModel):
    status: str
    message: str
    event_id: str
