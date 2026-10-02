from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api import (
    auth_router,
    bookings_router,
    centres_router,
    payments_router,
    webhooks_router,
)
from app.core.database import async_session_factory
from app.core.logging import logger
from app.core.redis import close_redis_client, get_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize redis connection pool on startup
    try:
        redis = get_redis_client()
        await redis.ping()
        logger.info("Connected to Redis successfully.")
    except Exception as e:
        logger.warning(f"Could not connect to Redis on startup: {e}")

    yield

    # Clean up on shutdown
    await close_redis_client()
    logger.info("Application shutdown complete.")


app = FastAPI(
    title="EVE Healthcare API",
    version="1.0.0",
    description="Backend service for diagnostic test bookings, simulated payments, and idempotent webhooks.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_details = []
    for err in errors:
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        error_details.append(f"{loc}: {err.get('msg')}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "; ".join(error_details)},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    headers = getattr(exc, "headers", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."},
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    db_status = "unhealthy"
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
            db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {e}"

    redis_status = "unhealthy"
    try:
        redis = get_redis_client()
        if await redis.ping():
            redis_status = "healthy"
    except Exception as e:
        redis_status = f"unhealthy: {e}"

    return {
        "status": "ok" if db_status == "healthy" and redis_status == "healthy" else "degraded",
        "database": db_status,
        "redis": redis_status,
    }


# Register API Routers
app.include_router(auth_router)
app.include_router(centres_router)
app.include_router(bookings_router)
app.include_router(payments_router)
app.include_router(webhooks_router)
