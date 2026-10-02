from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.middleware.rate_limit import RateLimiter
from app.schemas.webhook import PaymentWebhookRequest, WebhookResponse
from app.services.webhook_service import process_payment_webhook

router = APIRouter(prefix="/payments", tags=["Webhooks"])

webhook_limiter = RateLimiter(
    requests_per_minute=settings.RATE_LIMIT_WEBHOOK_PER_MINUTE,
    key_prefix="rl:webhook",
)


@router.post(
    "/webhook/",
    response_model=WebhookResponse,
    status_code=status.HTTP_200_OK,
    summary="Process external payment provider webhook (Idempotent)",
    dependencies=[Depends(webhook_limiter)],
)
async def payment_webhook(
    payload: PaymentWebhookRequest,
    db: AsyncSession = Depends(get_db),
):
    outcome_status, message = await process_payment_webhook(db, payload)
    return WebhookResponse(
        status=outcome_status,
        message=message,
        event_id=payload.event_id,
    )
