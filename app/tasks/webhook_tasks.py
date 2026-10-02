import asyncio
import concurrent.futures
from app.core.celery import celery_app
from app.core.database import async_session_factory
from app.core.logging import logger
from app.schemas.webhook import PaymentWebhookRequest
from app.services.webhook_service import process_payment_webhook


@celery_app.task(
    bind=True,
    name="app.tasks.webhook_tasks.process_webhook_async",
    max_retries=3,
    default_retry_delay=5,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
)
def process_webhook_async(self, payload_dict: dict, session_factory=None) -> dict:
    factory = session_factory or async_session_factory

    async def _run():
        payload = PaymentWebhookRequest(**payload_dict)
        async with factory() as db:
            status_code, msg = await process_payment_webhook(db, payload)
            return {"status": status_code, "message": msg}

    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # If called from within an active asyncio loop, run in a dedicated thread
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                return executor.submit(asyncio.run, _run()).result()
        else:
            return asyncio.run(_run())
    except Exception as exc:
        logger.error(
            f"Error processing webhook asynchronously for event {payload_dict.get('event_id')}: {exc}",
            extra={"extra_data": {"retry_count": self.request.retries if hasattr(self, "request") else 0}}
        )
        if hasattr(self, "retry"):
            raise self.retry(exc=exc)
        raise
