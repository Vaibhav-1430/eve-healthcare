import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class CentreCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    location: str = Field(min_length=1, max_length=255)


class CentreResponse(BaseModel):
    id: uuid.UUID
    name: str
    location: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TestCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    price: Decimal = Field(gt=0, decimal_places=2, description="Price must be strictly positive")


class TestResponse(BaseModel):
    id: uuid.UUID
    centre_id: uuid.UUID
    name: str
    description: str | None
    price: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
