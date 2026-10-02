import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from app.models.booking import BookingStatus


class BookingCreateRequest(BaseModel):
    diagnostic_centre_id: uuid.UUID
    diagnostic_test_id: uuid.UUID
    appointment_datetime: datetime


class BookingResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    diagnostic_centre_id: uuid.UUID
    diagnostic_test_id: uuid.UUID
    appointment_datetime: datetime
    amount: Decimal
    status: BookingStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
