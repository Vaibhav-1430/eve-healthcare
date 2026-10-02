from app.core.celery import celery_app
from app.core.logging import logger


@celery_app.task(name="app.tasks.payment_tasks.send_payment_receipt_async")
def send_payment_receipt_async(payment_id: str, booking_id: str, amount: str, recipient_email: str) -> bool:
    # Simulates sending an email receipt in the background
    logger.info(
        f"Simulating payment receipt dispatch for payment {payment_id}",
        extra={
            "extra_data": {
                "payment_id": payment_id,
                "booking_id": booking_id,
                "amount": amount,
                "recipient": recipient_email,
            }
        }
    )
    return True
