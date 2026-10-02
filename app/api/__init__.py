from app.api.auth import router as auth_router
from app.api.centres import router as centres_router
from app.api.bookings import router as bookings_router
from app.api.payments import router as payments_router
from app.api.webhooks import router as webhooks_router

__all__ = [
    "auth_router",
    "centres_router",
    "bookings_router",
    "payments_router",
    "webhooks_router",
]
