from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.payment import PaymentResponse, PaymentSimulateRequest
from app.services.payment_service import simulate_payment

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Simulate payment for a booking",
)
async def process_simulated_payment(
    payload: PaymentSimulateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    payment = await simulate_payment(db, current_user.id, payload)
    return PaymentResponse.model_validate(payment)
