# EVE Healthcare

> A diagnostic test booking platform built as an SDE Intern Backend Engineering Assignment, featuring an asynchronous FastAPI backend and a modern React demonstration frontend.

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-In--Memory-DC382D?style=flat&logo=redis&logoColor=white)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-5.4%2B-37814A?style=flat&logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tests](https://img.shields.io/badge/Tests-35%20Passing-success?style=flat&logo=pytest&logoColor=white)](tests/)

---

## 🔗 Quick Links

- [🎥 Watch Demo Video](#-demo)
- [🏗 System Architecture](#system-architecture)
- [📖 API Reference](#api-reference)
- [⚡ Local Setup (PowerShell)](#local-setup)
- [🧪 Automated Testing](#testing)
- [🛡 Security & IDOR Protection](#security-considerations)
- [Interactive Swagger UI (Local)](http://127.0.0.1:8000/docs)

---

## 🎥 Demo

A complete developer-guided walkthrough demonstrating user authentication, diagnostic lab discovery, appointment scheduling with server-derived pricing, payment simulation, idempotent webhook deduplication, Redis caching, Celery workers, and automated test execution.

[![EVE Healthcare Demo](docs/demo/demo-thumbnail.png)](docs/demo/EVE_Healthcare_Backend_Demo.mp4)

- **[▶ Watch Full Technical Walkthrough (05:56)](docs/demo/EVE_Healthcare_Backend_Demo.mp4)** — Comprehensive step-by-step walkthrough covering all 17 assignment requirements.
- **[▶ Watch Highlights Demo (02:45)](docs/demo/EVE_Healthcare_Backend_Demo_Short.mp4)** — Concise summary for rapid evaluation.

> **Local Playback Note**: The video files are stored directly in this repository under [`docs/demo/`](docs/demo/) (~4.48 MB). GitHub renders the MP4 directly in the browser upon clicking, or you can play them locally via VLC / QuickTime.

---

## Table of Contents

1. [Overview](#overview)
2. [What This Project Does](#what-this-project-does)
3. [Key Features](#key-features)
4. [System Architecture](#system-architecture)
5. [Application Flow](#application-flow)
6. [Tech Stack](#tech-stack)
7. [Project Structure](#project-structure)
8. [Backend Architecture](#backend-architecture)
9. [Authentication](#authentication)
10. [Diagnostic Centres & Tests](#diagnostic-centres--tests)
11. [Booking System & State Machine](#booking-system--state-machine)
12. [Payment Flow & Simulation](#payment-flow--simulation)
13. [Webhook Idempotency](#webhook-idempotency)
14. [Redis & Celery Infrastructure](#redis--celery-infrastructure)
15. [Database Design](#database-design)
16. [API Reference](#api-reference)
17. [Testing](#testing)
18. [Local Setup](#local-setup)
19. [Environment Variables](#environment-variables)
20. [Example API Flow](#example-api-flow)
21. [Design Decisions](#design-decisions)
22. [Assumptions](#assumptions)
23. [Security Considerations](#security-considerations)
24. [Future Improvements](#future-improvements)

---

## Overview

**EVE Healthcare** is a diagnostic test management platform engineered to model how real-world healthcare companies handle lab catalogues, appointment scheduling, and asynchronous payment settlement.

In modern diagnostic workflows, test bookings depend on strict scheduling constraints, immutable pricing snapshots, and third-party webhook callbacks that may experience retries, network delays, or out-of-order delivery. This project implements a backend that guarantees data integrity, prevents duplicate financial transactions through **atomic database idempotency**, and isolates patient records against **Insecure Direct Object Reference (IDOR)** attacks.

The backend is built with **FastAPI** and **PostgreSQL (asyncpg + SQLAlchemy 2.0)**, supported by **Redis** (caching and rate limiting) and **Celery** (asynchronous worker queues). A dedicated **React 18 + TypeScript** dashboard provides a demonstration interface to interact with the backend APIs.

---

## What This Project Does

- **For Patients & Clinics**: Allows registering accounts, discovering accredited diagnostic laboratories, exploring testing packages with transparent pricing, scheduling appointment slots, and tracking booking statuses.
- **For Backend Engineers & Evaluators**: Demonstrates production-grade backend engineering practices—stateless JWT authentication, sliding-window rate limiting, relational schema design with foreign key constraints, an explicit booking state machine, server-derived pricing, and idempotent payment webhook handling.
- **For Payment Simulation**: Provides a simulated gateway environment to trigger `SUCCESS` or `FAILED` payment events and observe live asynchronous database mutations without connecting real banking credentials.

---

## Key Features

### 🔐 Authentication & Access Control
- **Bcrypt Password Hashing**: Passwords are securely hashed with random salts using `bcrypt` (enforcing minimum 8 characters).
- **Stateless JWT Tokens**: Issues signed HS256 JWT access tokens containing user identity and expiration timestamps.
- **Server-Side Authorization**: Built-in IDOR protection guarantees users can only view, cancel, or pay for their own bookings (`HTTP 403 Forbidden` on unauthorized access).

### 🏥 Diagnostic Catalog & Discovery
- **Centres & Tests Directory**: Manages diagnostic centres and lab tests with decimal price validation (`price > 0`).
- **In-Memory Caching**: Redis caches centre and test listings with automatic cache invalidation when new resources are created.
- **Standardized Pagination**: Uniform `page`, `page_size`, `total`, and `pages` metadata on all collection queries.

### 📅 Booking System & State Machine
- **Server-Derived Pricing**: Test prices are captured on the server at booking time as an immutable snapshot. The frontend cannot manipulate or supply booking amounts.
- **Future Date Validation**: Appointments must be scheduled in the future; historical and invalid timestamps are rejected.
- **Deterministic State Machine**: Strict lifecycle rules (`PENDING → CONFIRMED`, `PENDING → FAILED`, `PENDING → CANCELLED`). Disallows illegal transitions or modifying closed bookings.

### 💳 Payments & Webhook Idempotency
- **Simulated Payment Gateway**: Initiates simulated transactions and issues unique provider references (`pay_sim_...`).
- **Atomic Idempotent Webhooks**: Payment gateway webhooks are deduplicated against a `webhook_events` database table using a unique `event_id` constraint. Replayed or duplicated webhooks return `HTTP 200 OK` with `status: "already_processed"`, ensuring exactly-once execution.

### ⚡ Infrastructure & Quality
- **Redis Rate Limiting**: Sliding-window rate limiter protecting sensitive authentication endpoints (10 req/min).
- **Celery Background Workers**: Offloads webhook processing and payment receipt dispatch to asynchronous worker threads.
- **Structured JSON Logging**: Standard JSON-formatted application logs with timestamps, log levels, and contextual metadata, automatically scrubbing passwords and tokens.
- **Complete Test Suite**: **35 automated unit and integration tests** passing with pytest, plus a **17-step end-to-end verification script**.

---

## System Architecture

The application adopts a decoupled, multi-tier architecture separating synchronous API traffic from asynchronous task execution and relational persistence.

```mermaid
flowchart TD
    subgraph ClientLayer["Presentation Layer"]
        UI["React 18 + TypeScript SPA\n(Vite 6 + Tailwind CSS)"]
        Swagger["OpenAPI / Swagger UI\n(http://127.0.0.1:8000/docs)"]
    end

    subgraph APILayer["FastAPI Application"]
        Router["API Gateway / Routers\n(/auth, /centres, /bookings, /payments)"]
        RateLimiter["SlowAPI Rate Limiter\n(10 req/min on Auth)"]
        AuthMiddleware["JWT Bearer Authentication\n& IDOR Authorization"]
        ServiceLayer["Domain Services\n(BookingStateMachine, IdempotencyEngine)"]
    end

    subgraph StorageLayer["Data & Persistence"]
        DB[("PostgreSQL 16\n(asyncpg + SQLAlchemy 2.0 Async)")]
        RedisCache[("Redis In-Memory\n(Catalog Cache & Limiter Store)")]
    end

    subgraph AsyncLayer["Asynchronous Workers"]
        RedisQueue[("Redis Queue Broker\n(redis://127.0.0.1:6379/1)")]
        CeleryWorker["Celery Background Worker\n(Payment Retries & Receipts)"]
    end

    UI -->|REST / JSON Requests| Router
    Swagger -->|Interactive Testing| Router

    Router --> RateLimiter
    RateLimiter --> RedisCache
    Router --> AuthMiddleware
    AuthMiddleware --> ServiceLayer

    ServiceLayer -->|Async Queries| DB
    ServiceLayer -->|Cached Queries & TTL| RedisCache
    ServiceLayer -->|Enqueue Background Tasks| RedisQueue
    RedisQueue -->|Consume Tasks| CeleryWorker
    CeleryWorker -->|Async State Mutation| DB
```

---

## Application Flow

The diagram below details the complete lifecycle from account registration to appointment confirmation and idempotent webhook handling:

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Practitioner
    participant UI as React Frontend
    participant API as FastAPI Backend
    participant Redis as Redis Cache
    participant DB as PostgreSQL 16
    participant Celery as Celery Worker

    Note over User, DB: 1. Authentication
    User->>UI: Enter email, password (min 8 chars), full name
    UI->>API: POST /auth/signup
    API->>DB: Check unique email & store bcrypt hash
    API-->>UI: 201 Created (User Profile)
    User->>UI: Sign in with credentials
    UI->>API: POST /auth/login
    API-->>UI: 200 OK (access_token: JWT, user)

    Note over User, DB: 2. Catalog & Scheduling
    User->>UI: Browse Diagnostic Centres
    UI->>API: GET /centres/?page=1&page_size=20
    API->>Redis: Check cache (centres:page:1:size:20)
    alt Cache Miss
        API->>DB: Query centres table
        API->>Redis: Store in cache (TTL 60s)
    end
    API-->>UI: 200 OK (Centres list + pagination)

    User->>UI: Select Lab, Test & Future Appointment Slot
    UI->>API: POST /bookings/ (centre_id, test_id, appointment_datetime)
    API->>DB: Verify future datetime & query test price snapshot
    API->>DB: Insert booking record (status: PENDING, amount: test.price)
    API-->>UI: 201 Created (Booking details)

    Note over User, Celery: 3. Simulated Payment & Webhook
    User->>UI: Trigger Simulated Payment (Outcome: SUCCESS)
    UI->>API: POST /payments/ (booking_id, simulated_status)
    API->>DB: Verify booking is PENDING & copy booking.amount
    API->>DB: Insert payment record (status: PENDING, provider_reference)
    API->>Celery: Enqueue process_payment_webhook task
    API-->>UI: 200 OK (Payment initiated)

    Note over Celery, DB: 4. Idempotent Webhook Processing
    Celery->>API: POST /payments/webhook/ (event_id, booking_id, status: SUCCESS)
    API->>DB: Query webhook_events for event_id
    alt First-Time Delivery
        API->>DB: INSERT into webhook_events (event_id, payload)
        API->>DB: UPDATE bookings SET status = 'CONFIRMED'
        API-->>Celery: 200 OK {"status": "processed"}
    else Duplicate Replay Delivery
        API-->>Celery: 200 OK {"status": "already_processed"} (No state change)
    end

    UI->>API: GET /bookings/{id}
    API-->>UI: 200 OK (status: CONFIRMED)
```

---

## Tech Stack

### Backend Technologies
- **Python 3.12+** (Tested on Python 3.13): Modern type hints, pattern matching, and native async runtime.
- **FastAPI 0.115+**: High-performance ASGI framework with Pydantic v2 schema validation.
- **SQLAlchemy 2.0 (Async)**: Modern async ORM using `select()` syntax and connection pooling.
- **asyncpg 0.31+**: High-speed native asynchronous PostgreSQL database driver.
- **PostgreSQL 16**: Relational database with unique constraints, foreign keys, and indexes.
- **Alembic 1.20+**: Version-controlled database schema migrations.
- **Redis 8.1+**: In-memory cache for API catalog responses and backend counter for rate limiting.
- **Celery 5.4+**: Distributed asynchronous worker handling webhook processing and retry pipelines.
- **Pytest 9.1+ & pytest-asyncio**: Async test execution framework with HTTPX ASGI client.

### Frontend Technologies
- **React 18 + TypeScript 5.6**: Type-safe SPA architecture.
- **Vite 6**: Fast development build tool and optimized production bundler.
- **Tailwind CSS 3.4**: Clean, restrained healthcare design system with slate palettes and teal accents.
- **React Router v6**: Client-side routing with nested layout wrappers and `ProtectedRoute` guards.
- **Axios 1.7+**: Centralized API client with automatic JWT token attachment and 401 unauthenticated redirect interceptors.
- **Lucide React**: Modern iconography.

---

## Project Structure

```text
.
├── alembic/                         # Database migration scripts
│   ├── env.py                       # Alembic async migration environment
│   ├── script.py.mako               # Migration template
│   └── versions/                    # Version-controlled schema migrations
│       └── db983a6c2580_initial_schema.py
├── app/                             # Core backend application
│   ├── api/                         # FastAPI REST route controllers
│   │   ├── auth.py                  # POST /auth/signup, POST /auth/login
│   │   ├── centres.py               # GET/POST /centres, GET /centres/{id}, /tests
│   │   ├── bookings.py              # POST /bookings, GET /bookings, /cancel
│   │   └── payments.py              # POST /payments, POST /payments/webhook
│   ├── core/                        # Infrastructure and cross-cutting concerns
│   │   ├── celery.py                # Celery worker initialization
│   │   ├── config.py                # Pydantic Settings (.env configuration)
│   │   ├── database.py              # Async SQLAlchemy engine and sessionmaker
│   │   ├── logging.py               # Structured JSON logging formatter
│   │   ├── rate_limit.py            # Slowapi Redis rate limiter setup
│   │   ├── redis.py                 # Redis connection client and cache helpers
│   │   └── security.py              # Bcrypt hashing and PyJWT token utilities
│   ├── models/                      # SQLAlchemy relational models
│   │   ├── user.py                  # users table
│   │   ├── centre.py                # diagnostic_centres table
│   │   ├── test.py                  # diagnostic_tests table
│   │   ├── booking.py               # bookings table (BookingStatus enum)
│   │   ├── payment.py               # payments table (PaymentStatus enum)
│   │   └── webhook.py               # webhook_events table (Idempotency log)
│   ├── schemas/                     # Pydantic v2 validation and response schemas
│   │   ├── auth.py                  # SignupRequest, LoginRequest, TokenResponse
│   │   ├── centre.py                # CentreCreate, CentreResponse
│   │   ├── test.py                  # TestCreate, TestResponse
│   │   ├── booking.py               # BookingCreate, BookingResponse
│   │   ├── payment.py               # PaymentCreate, PaymentResponse
│   │   └── pagination.py            # PaginatedResponse generic model
│   ├── services/                    # Domain logic & state machine validation
│   │   ├── auth_service.py          # User registration & verification
│   │   ├── centre_service.py        # Lab & test management with Redis caching
│   │   ├── booking_service.py       # Pricing snapshot, date checks, IDOR verification
│   │   └── payment_service.py       # Payment initiation & idempotent webhook engine
│   ├── tasks/                       # Celery asynchronous worker tasks
│   │   └── payment_tasks.py         # process_payment_webhook, send_receipt
│   └── main.py                      # FastAPI app entry point, CORS, exception handlers
├── docs/                            # Documentation assets
│   └── demo/                        # Demo media
│       ├── EVE_Healthcare_Backend_Demo.mp4       # Full 1080p demo video (5m 56s)
│       ├── EVE_Healthcare_Backend_Demo_Short.mp4 # Concise 1080p demo video (2m 45s)
│       └── demo-thumbnail.png                    # Demo preview poster image
├── frontend/                        # React demonstration dashboard
│   ├── src/
│   │   ├── api/                     # Axios API clients (auth, centres, bookings, payments)
│   │   ├── components/              # Navbar, Sidebar, ProtectedRoute, StatusBadge, etc.
│   │   ├── context/                 # AuthContext (JWT session management)
│   │   ├── pages/                   # Login, Signup, Dashboard, Centres, Booking, Payments
│   │   ├── types/                   # TypeScript interfaces matching backend models
│   │   ├── App.tsx                  # App routes and layout configuration
│   │   ├── main.tsx                 # DOM entry point
│   │   └── index.css                # Tailwind directives
│   ├── .env.example                 # Template frontend config (VITE_API_BASE_URL)
│   ├── package.json                 # Dependencies
│   └── vite.config.ts               # Vite configuration
├── scripts/                         # Automation & verification tools
│   ├── generate_demo_videos.py      # Video generation script using FFmpeg and Pillow
│   └── verify_e2e.py                # 17-step end-to-end integration test script
├── tests/                           # Pytest automated test suite (35 tests)
│   ├── conftest.py                  # Async fixtures, test DB setup, auth tokens
│   ├── test_auth.py                 # Signup, login, password validation tests
│   ├── test_authorization.py        # IDOR security and user isolation tests
│   ├── test_bookings.py             # State machine, pricing snapshot, scheduling tests
│   ├── test_celery.py               # Celery worker task tests
│   ├── test_centres.py              # Catalogue and positive price validation tests
│   ├── test_payments.py             # Payment simulation and duplicate guard tests
│   ├── test_rate_limit.py           # Slowapi Redis rate limiting tests
│   └── test_webhooks.py             # Idempotency and duplicate webhook replay tests
├── .env.example                     # Template backend environment config
├── .gitignore                       # Clean Git exclusion rules
├── alembic.ini                      # Alembic database configuration
├── pytest.ini                       # Pytest configuration
├── README.md                        # Primary project documentation
└── requirements.txt                 # Python production dependencies
```

---

## Backend Architecture

### 1. Dependency Injection Pattern
FastAPI's dependency injection system (`Depends`) manages request lifecycles cleanly:
- `get_db()`: Yields an async database session wrapped in an automatic context manager.
- `get_current_user()`: Validates the incoming Bearer JWT, decodes the user ID, queries the database, and injects the authenticated `User` model.
- `get_redis()`: Injects the active Redis client connection.

### 2. Service Layer Separation
Routers handle HTTP request parsing, response codes, and serialization. All business logic, database transactions, and state validation reside in dedicated service classes:
- [`BookingService`](app/services/booking_service.py): Manages appointment date validation, queries the test price snapshot from the database, enforces IDOR ownership checks, and validates state transitions.
- [`PaymentService`](app/services/payment_service.py): Derives payment amounts from booking records and executes atomic webhook idempotency queries.

### 3. Global Exception Handling
In [`app/main.py`](app/main.py), custom exception handlers intercept:
- `RequestValidationError`: Formats Pydantic validation errors into clean, readable JSON strings with `HTTP 422 Unprocessable Entity`.
- `HTTPException`: Standardizes error message payloads.
- `StarletteHTTPException`: Uniform status reporting across all HTTP anomalies.

---

## Authentication

Authentication is stateless and implemented using JWT:

1. **User Registration** (`POST /auth/signup`):
   - Accepts `email`, `password`, and `full_name`.
   - Validates that the password is at least 8 characters long.
   - Computes a bcrypt salted hash (`bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())`).
   - Inserts the user record into PostgreSQL.
2. **User Login** (`POST /auth/login`):
   - Compares the provided password against the stored bcrypt hash.
   - Generates an HS256-signed JWT containing:
     - `sub`: User ID (UUID)
     - `exp`: Expiration timestamp (60 minutes default)
     - `iat`: Issued-at timestamp
   - Returns `{ "access_token": "<JWT>", "token_type": "bearer", "user": { ... } }`.
3. **Rate Limiting**:
   - Both `/auth/login` and `/auth/signup` are limited to **10 requests per minute per IP** via Redis sliding-window counters, mitigating brute-force attacks.

---

## Diagnostic Centres & Tests

- **Centres** (`POST /centres/`, `GET /centres/`, `GET /centres/{id}`):
  - Centres represent physical or regional diagnostic laboratories.
  - Centre lookups are cached in Redis with a 60-second TTL.
  - Adding a new centre invalidates the catalog cache automatically.
- **Diagnostic Tests** (`POST /centres/{id}/tests`, `GET /centres/{id}/tests`, `GET /tests/{id}`):
  - Each test belongs to a specific diagnostic centre via a foreign key (`centre_id`).
  - Enforces positive price validation: `price > Decimal("0")`. Attempts to create tests with zero or negative prices return `HTTP 422`.
  - Monetary values are stored as `NUMERIC(10, 2)` to eliminate floating-point imprecision.

---

## Booking System & State Machine

### Deterministic State Transitions

```mermaid
stateDiagram-v2
    [*] --> PENDING: POST /bookings/
    PENDING --> CONFIRMED: Webhook SUCCESS / Payment SUCCESS
    PENDING --> FAILED: Webhook FAILED / Payment FAILED
    PENDING --> CANCELLED: POST /bookings/{id}/cancel
    CONFIRMED --> [*]
    FAILED --> PENDING: Payment Retry
    CANCELLED --> [*]
```

### State Machine Rules
1. **Creation**:
   - Default status: `PENDING`.
   - Pricing is **strictly server-derived**: The backend queries `diagnostic_tests.price` and writes it to `bookings.amount`. The client cannot manipulate the amount.
   - Future appointment validation: `appointment_datetime` must be strictly in the future.
2. **Cancellation** (`POST /bookings/{id}/cancel`):
   - Permitted **only** when status is `PENDING`.
   - Attempting to cancel a `CONFIRMED`, `FAILED`, or already `CANCELLED` booking returns `HTTP 400 Bad Request`.
3. **Settlement**:
   - Only `PENDING` bookings can be settled. Attempting to initiate payment on an already `CONFIRMED` booking returns `HTTP 400 Bad Request`.

---

## Payment Flow & Simulation

Payment processing is simulated as required by the assignment. No real external banking gateway is connected.

1. **Initiate Payment** (`POST /payments/`):
   - Accepts `{ "booking_id": "<UUID>", "simulated_status": "SUCCESS" | "FAILED" }`.
   - Backend derives payment amount strictly from `booking.amount`.
   - Verifies the booking belongs to the authenticated user (IDOR protection).
   - Generates a unique provider reference: `pay_sim_<hex>`.
   - Inserts a record into the `payments` table.
   - Dispatches `process_payment_webhook` via Celery (or synchronous execution fallback).
2. **Provider Reference**:
   - The provider reference is unique and indexed in PostgreSQL, serving as a transaction audit trail.

---

## Webhook Idempotency

External gateways routinely retry webhooks when network timeouts occur. Without idempotency, duplicate webhooks could trigger duplicate transactions or corrupt booking states.

```mermaid
flowchart TD
    Webhook[Incoming POST /payments/webhook/\nPayload: event_id, booking_id, status] --> Check{Query webhook_events\nfor event_id}
    
    Check -->|Record Not Found| FirstDelivery[1st Delivery Confirmed]
    FirstDelivery --> InsertEvent[Insert event into webhook_events]
    InsertEvent --> MutateState[Update booking status to CONFIRMED/FAILED]
    MutateState --> Respond200[Return HTTP 200 OK\nstatus: processed]
    
    Check -->|Record Exists| DuplicateDelivery[Duplicate Replay Detected]
    DuplicateDelivery --> SkipMutation[Bypass State Machine & DB Mutation]
    SkipMutation --> RespondIdempotent[Return HTTP 200 OK\nstatus: already_processed]
```

### Technical Implementation
1. **Schema Constraint**: The `webhook_events` table enforces a `UNIQUE` constraint and index on `event_id`:
   ```sql
   CREATE TABLE webhook_events (
       id UUID PRIMARY KEY,
       event_id VARCHAR(255) NOT NULL UNIQUE,
       provider_reference VARCHAR(255),
       status VARCHAR(20) NOT NULL,
       payload JSONB NOT NULL,
       processed_at TIMESTAMPTZ DEFAULT NOW()
   );
   ```
2. **First Delivery**:
   - Event record does not exist.
   - The service inserts the event and transitions the booking status to `CONFIRMED` or `FAILED`.
   - Returns `HTTP 200 OK` with `{"status": "processed", "event_id": "..."}`.
3. **Duplicate Delivery (Replay)**:
   - Event record already exists.
   - The service catches the record existence, **bypasses booking state modification**, and immediately returns `HTTP 200 OK` with `{"status": "already_processed", "event_id": "..."}`.
   - No duplicate state mutations or receipts occur.

---

## Redis & Celery Infrastructure

### Redis Integration
1. **Catalog Caching**:
   - Centre and test catalogue endpoints (`/centres/`, `/centres/{id}/tests`) query Redis before hitting PostgreSQL.
   - Default cache TTL: 60 seconds (`CACHE_TTL_SECONDS=60`).
   - Mutations (`POST /centres/`, `POST /centres/{id}/tests`) automatically invalidate related cache keys.
2. **Sliding-Window Rate Limiting**:
   - Implemented via `slowapi` with Redis storage (`redis://127.0.0.1:6379/0`).
   - Protects `/auth/login` and `/auth/signup` at **10 requests per minute**. Excess requests return `HTTP 429 Too Many Requests`.

### Celery Background Worker
- **Task Queue**: Celery connects to Redis broker `redis://127.0.0.1:6379/1` and results backend `redis://127.0.0.1:6379/2`.
- **Registered Tasks**:
  - `app.tasks.payment_tasks.process_payment_webhook`: Decouples webhook ingestion from state mutation, supporting exponential backoff retries on transient errors.
  - `app.tasks.payment_tasks.send_booking_receipt`: Simulates asynchronous receipt dispatch.
- **Worker Concurrency**: Runs with `--pool=solo` on Windows environments for stable native execution.

---

## Database Design

PostgreSQL 16 relational schema managed with version-controlled **Alembic** migrations. All primary keys use `UUIDv4` to prevent sequential ID guessing.

```text
┌───────────────────────────────────────┐
│                 users                 │
├───────────────────────────────────────┤
│ id: UUID (PK)                         │
│ email: VARCHAR(255) (UNIQUE, INDEX)   │
│ hashed_password: VARCHAR(255)         │
│ full_name: VARCHAR(255)               │
│ is_active: BOOLEAN (DEFAULT TRUE)     │
│ created_at, updated_at: TIMESTAMPTZ   │
└──────────────────┬────────────────────┘
                   │ 1
                   │
                   │ *
┌──────────────────┴────────────────────┐       ┌───────────────────────────────────────┐
│               bookings                │       │          diagnostic_centres           │
├───────────────────────────────────────┤       ├───────────────────────────────────────┤
│ id: UUID (PK)                         │       │ id: UUID (PK)                         │
│ user_id: UUID (FK -> users.id)        │       │ name: VARCHAR(255) (INDEX)            │
│ centre_id: UUID (FK -> centres.id)    │◀──────│ location: VARCHAR(255)                │
│ test_id: UUID (FK -> tests.id)        │◀──┐   │ created_at, updated_at: TIMESTAMPTZ   │
│ appointment_datetime: TIMESTAMPTZ     │   │   └──────────────────┬────────────────────┘
│ amount: NUMERIC(10,2) (Price Snapshot)│   │                      │ 1
│ status: VARCHAR(20) (INDEX)           │   │                      │
│ created_at, updated_at: TIMESTAMPTZ   │   │                      │ *
└──────────────────┬────────────────────┘   │   ┌──────────────────┴────────────────────┐
                   │ 1                      │   │           diagnostic_tests            │
                   │                        │   ├───────────────────────────────────────┤
                   │ 1                      └───│ id: UUID (PK)                         │
┌──────────────────┴────────────────────┐       │ centre_id: UUID (FK -> centres.id)    │
│               payments                │       │ name: VARCHAR(255) (INDEX)            │
├───────────────────────────────────────┤       │ description: TEXT                     │
│ id: UUID (PK)                         │       │ price: NUMERIC(10,2) (> 0)            │
│ booking_id: UUID (FK -> bookings.id)  │       │ created_at, updated_at: TIMESTAMPTZ   │
│ amount: NUMERIC(10,2)                 │       └───────────────────────────────────────┘
│ status: VARCHAR(20) (INDEX)           │
│ provider_reference: VARCHAR (UNIQUE)  │       ┌───────────────────────────────────────┐
│ created_at, updated_at: TIMESTAMPTZ   │       │            webhook_events             │
└───────────────────────────────────────┘       ├───────────────────────────────────────┤
                                                │ id: UUID (PK)                         │
                                                │ event_id: VARCHAR(255) (UNIQUE, INDEX)│
                                                │ provider_reference: VARCHAR(255)      │
                                                │ status: VARCHAR(20) (INDEX)           │
                                                │ payload: JSONB                        │
                                                │ processed_at: TIMESTAMPTZ             │
                                                └───────────────────────────────────────┘
```

---

## API Reference

The interactive Swagger UI is available locally at **`http://127.0.0.1:8000/docs`**.

| Area | Method | Endpoint | Description | Auth Required |
|---|---|---|---|---|
| **Health** | `GET` | `/health` | Service, PostgreSQL, and Redis health check | No |
| **Auth** | `POST` | `/auth/signup` | Register a new user account (min. 8 char password) | No (Rate Limited: 10/min) |
| **Auth** | `POST` | `/auth/login` | Authenticate credentials and receive Bearer JWT | No (Rate Limited: 10/min) |
| **Centres** | `POST` | `/centres/` | Register a new diagnostic centre | Yes (JWT) |
| **Centres** | `GET` | `/centres/` | List diagnostic centres (paginated: `page`, `page_size`) | No (Redis Cached) |
| **Centres** | `GET` | `/centres/{id}` | Get diagnostic centre details by UUID | No (Redis Cached) |
| **Tests** | `POST` | `/centres/{id}/tests` | Create a diagnostic test for a centre (`price > 0`) | Yes (JWT) |
| **Tests** | `GET` | `/centres/{id}/tests` | List tests offered by a centre (paginated) | No (Redis Cached) |
| **Tests** | `GET` | `/tests/{id}` | Retrieve diagnostic test details and pricing | No (Redis Cached) |
| **Bookings** | `POST` | `/bookings/` | Schedule test appointment (server price snapshot) | Yes (JWT) |
| **Bookings** | `GET` | `/bookings/` | List authenticated user's bookings (paginated) | Yes (JWT) |
| **Bookings** | `GET` | `/bookings/{id}` | Retrieve booking details (IDOR protected: 403) | Yes (JWT) |
| **Bookings** | `POST` | `/bookings/{id}/cancel` | Cancel pending booking (state machine enforced) | Yes (JWT) |
| **Payments** | `POST` | `/payments/` | Initiate simulated payment (amount derived from booking) | Yes (JWT) |
| **Webhooks** | `POST` | `/payments/webhook/` | Process payment webhook with atomic idempotency | No (Event ID Deduplication) |

---

## Testing

The project includes an automated test suite with **100% passing results**.

### 1. Automated Unit & Integration Tests (`pytest`)

```powershell
pytest -v
```

**Result: 35 passed in 24.61s**

```text
tests/test_auth.py::test_signup_success PASSED                           [  2%]
tests/test_auth.py::test_duplicate_signup PASSED                         [  5%]
tests/test_auth.py::test_login_success PASSED                            [  8%]
tests/test_auth.py::test_login_invalid_password PASSED                   [ 11%]
tests/test_auth.py::test_protected_route_without_token PASSED            [ 14%]
tests/test_auth.py::test_signup_malformed_request PASSED                 [ 17%]
tests/test_authorization.py::test_user_cannot_access_another_users_booking PASSED [ 20%]
tests/test_authorization.py::test_user_cannot_cancel_another_users_booking PASSED [ 22%]
tests/test_authorization.py::test_user_cannot_pay_for_another_users_booking PASSED [ 25%]
tests/test_authorization.py::test_user_booking_list_isolation PASSED     [ 28%]
tests/test_bookings.py::test_create_booking_success PASSED               [ 31%]
tests/test_bookings.py::test_create_booking_invalid_centre PASSED        [ 34%]
tests/test_bookings.py::test_create_booking_invalid_test PASSED          [ 37%]
tests/test_bookings.py::test_create_booking_test_belongs_to_different_centre PASSED [ 40%]
tests/test_bookings.py::test_cancel_booking_success PASSED               [ 42%]
tests/test_bookings.py::test_cancel_already_cancelled_booking_fails PASSED [ 45%]
tests/test_bookings.py::test_list_bookings_pagination PASSED             [ 48%]
tests/test_celery.py::test_send_payment_receipt_task PASSED              [ 51%]
tests/test_celery.py::test_process_webhook_async_task PASSED             [ 54%]
tests/test_centres.py::test_create_centre PASSED                         [ 57%]
tests/test_centres.py::test_list_centres_and_pagination PASSED           [ 60%]
tests/test_centres.py::test_get_centre_by_id PASSED                      [ 62%]
tests/test_centres.py::test_get_centre_invalid_id PASSED                 [ 65%]
tests/test_centres.py::test_create_test_and_list_by_centre PASSED        [ 68%]
tests/test_centres.py::test_create_test_for_invalid_centre PASSED        [ 71%]
tests/test_centres.py::test_create_test_with_negative_price PASSED       [ 74%]
tests/test_payments.py::test_successful_simulated_payment PASSED         [ 77%]
tests/test_payments.py::test_failed_simulated_payment PASSED             [ 80%]
tests/test_payments.py::test_duplicate_payment_fails PASSED              [ 82%]
tests/test_payments.py::test_payment_for_non_existent_booking PASSED     [ 85%]
tests/test_rate_limit.py::test_rate_limiting_enforcement PASSED          [ 88%]
tests/test_webhooks.py::test_webhook_successful_processing PASSED        [ 91%]
tests/test_webhooks.py::test_webhook_idempotency_duplicate_events PASSED [ 94%]
tests/test_webhooks.py::test_webhook_unknown_payment_reference PASSED    [ 97%]
tests/test_webhooks.py::test_concurrent_duplicate_webhooks PASSED        [100%]

============================= 35 passed in 24.61s =============================
```

### 2. End-to-End Live System Verification (`verify_e2e.py`)

```powershell
python scripts/verify_e2e.py
```

**Result: 17/17 verification steps passing on live server**:
- `[STEP 1 - 3]` User signup, login, JWT token issuance.
- `[STEP 4 - 5]` Diagnostic centre creation and test catalog registration.
- `[STEP 6]` Test booking creation with server-derived pricing snapshot.
- `[STEP 7]` Simulated payment execution with unique provider reference.
- `[STEP 8]` Booking confirmation via webhook event processing.
- `[STEP 9 - 10]` Replay of identical webhook events returning HTTP 200 idempotently (`already_processed`).
- `[STEP 11 - 12]` State machine verification blocking duplicate payments.
- `[STEP 13]` IDOR cross-user access blocked with HTTP 403 Forbidden.
- `[STEP 14]` Booking cancellation state transition.
- `[STEP 15]` Sliding window rate limiter triggered on request 9 (HTTP 429).

---

## Local Setup

### Prerequisites

- **Python 3.12+**
- **Node.js 18+**
- **PostgreSQL 16** (running on `localhost:5432`)
- **Redis / Memurai** (running on `127.0.0.1:6379`)

### 1. Database Setup
Create the PostgreSQL databases for development and testing:
```sql
CREATE DATABASE eve_healthcare;
CREATE DATABASE eve_healthcare_test;
```

### 2. Backend Setup

```powershell
# 1. Clone repository & navigate to project root
cd d:\Projects\Assesmentt

# 2. Create and activate Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
Copy-Item .env.example .env

# 5. Apply database migrations
alembic upgrade head

# 6. Start Celery background worker (in a dedicated terminal)
celery -A app.core.celery worker --pool=solo --loglevel=info

# 7. Start FastAPI application server (in a dedicated terminal)
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- API Base: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/health`

### 3. Frontend Setup

```powershell
# In a new terminal, navigate to frontend directory
cd frontend

# Install frontend dependencies
npm install

# Start Vite development server
npm run dev
```

- Web Application: `http://localhost:5173`

---

## Environment Variables

Configured in root `.env` based on [`.env.example`](.env.example):

| Variable | Description | Default / Example Value |
|---|---|---|
| `DATABASE_URL` | PostgreSQL asyncpg connection string | `postgresql+asyncpg://postgres:postgres@localhost:5432/eve_healthcare` |
| `TEST_DATABASE_URL` | Test database connection string | `postgresql+asyncpg://postgres:postgres@localhost:5432/eve_healthcare_test` |
| `JWT_SECRET_KEY` | Secret key used to sign HS256 JWT tokens | *Change in production (min 32 chars)* |
| `JWT_ALGORITHM` | Token signature cryptographic algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime before expiration | `60` |
| `REDIS_URL` | Redis URL for catalog caching & rate limiting | `redis://127.0.0.1:6379/0` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://127.0.0.1:6379/1` |
| `CELERY_RESULT_BACKEND` | Celery result backend URL | `redis://127.0.0.1:6379/2` |
| `RATE_LIMIT_PER_MINUTE` | General global rate limit | `60` |
| `RATE_LIMIT_AUTH_PER_MINUTE` | Rate limit on login and signup | `10` |
| `RATE_LIMIT_WEBHOOK_PER_MINUTE`| Rate limit on payment webhooks | `120` |
| `CACHE_TTL_SECONDS` | In-memory cache TTL for catalog queries | `60` |
| `ENVIRONMENT` | Environment mode (`development` / `production`)| `development` |

---

## Example API Flow

Below is a complete, reproducible sequence using PowerShell `Invoke-RestMethod` or `curl`:

### 1. Register a User
```bash
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"doctor@evehealthcare.com","password":"Password123!","full_name":"Dr. Samantha Rao"}'
```

### 2. Login & Receive JWT
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"doctor@evehealthcare.com","password":"Password123!"}'
# Response contains: {"access_token": "<TOKEN>", "token_type": "bearer", ...}
```

### 3. Create Diagnostic Centre & Test
```bash
# Create Centre
curl -X POST http://127.0.0.1:8000/centres/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Apex Diagnostic Lab","location":"Koramangala, Bengaluru"}'

# Create Test under Centre
curl -X POST http://127.0.0.1:8000/centres/<CENTRE_ID>/tests \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Lipid Profile Panel","description":"Full cholesterol and triglyceride screen","price":850.00}'
```

### 4. Create Booking
```bash
curl -X POST http://127.0.0.1:8000/bookings/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"diagnostic_centre_id":"<CENTRE_ID>","diagnostic_test_id":"<TEST_ID>","appointment_datetime":"2026-10-15T10:00:00Z"}'
# Status: PENDING, amount: 850.00 (derived by server)
```

### 5. Simulate Payment
```bash
curl -X POST http://127.0.0.1:8000/payments/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"booking_id":"<BOOKING_ID>","simulated_status":"SUCCESS"}'
```

### 6. Process Webhook & Verify Idempotency
```bash
# 1st Webhook Delivery -> Transitions booking to CONFIRMED
curl -X POST http://127.0.0.1:8000/payments/webhook/ \
  -H "Content-Type: application/json" \
  -d '{"event_id":"evt_demo_101","booking_id":"<BOOKING_ID>","status":"SUCCESS","provider_reference":"pay_sim_abc","timestamp":"2026-10-03T00:00:00Z"}'
# Response: {"status":"processed","event_id":"evt_demo_101"}

# 2nd Delivery (Same event_id) -> Idempotently acknowledged without side effects
curl -X POST http://127.0.0.1:8000/payments/webhook/ \
  -H "Content-Type: application/json" \
  -d '{"event_id":"evt_demo_101","booking_id":"<BOOKING_ID>","status":"SUCCESS","provider_reference":"pay_sim_abc","timestamp":"2026-10-03T00:00:00Z"}'
# Response: {"status":"already_processed","event_id":"evt_demo_101"}
```

---

## Design Decisions

| Decision | Rationale |
|---|---|
| **SQLAlchemy 2.0 Async + asyncpg** | Non-blocking database I/O allows FastAPI worker threads to handle thousands of concurrent requests without thread starvation. |
| **Server-Derived Pricing Snapshots** | When booking an appointment, the test price is queried from PostgreSQL and written directly to `bookings.amount`. The client cannot supply or manipulate payment amounts, and subsequent catalog price changes do not alter existing booking records. |
| **UUIDv4 Primary Keys** | Prevents sequential enumeration attacks, masking booking volume and patient counts from competitors. |
| **Database-Level Webhook Idempotency** | In-memory deduplication (e.g. Redis keys with TTL) risks data corruption if Redis evicts keys under memory pressure. Enforcing a `UNIQUE` constraint on `webhook_events.event_id` in PostgreSQL guarantees ACID compliance and safe retries indefinitely. |
| **Explicit Booking State Machine** | Eliminates undefined states. Bookings transition exclusively from `PENDING` to terminal states (`CONFIRMED`, `FAILED`, `CANCELLED`). Payments on non-pending bookings are rejected immediately. |
| **Decoupled Celery Worker** | Prevents slow third-party integrations or retries from blocking the synchronous HTTP response thread. |

---

## Assumptions

1. **Simulated Payment Environment**: As specified in the assignment prompt, payment processing is simulated in-house without requiring live merchant credentials from third-party payment gateways.
2. **Future Appointment Validation**: Healthcare procedures require clinical preparation. The backend enforces that appointment timestamps must be set in the future.
3. **User Isolation**: A booking belongs to a single patient account. Cross-user viewing, cancellation, or settlement attempts are rejected with `HTTP 403 Forbidden`.

---

## Security Considerations

- **Password Security**: Salted bcrypt password hashing with an adaptive work factor prevents rainbow table attacks.
- **JWT Protection**: Tokens are signed using HS256 with a 60-minute expiration window. Secrets are loaded strictly from environment variables and excluded from version control.
- **IDOR Prevention**: Every booking operation checks `booking.user_id == current_user.id` before returning details or executing transitions.
- **SQL Injection Prevention**: SQLAlchemy 2.0 uses parameterized query bindings for all database operations, eliminating SQL injection vectors.
- **Rate Limiting**: Sliding-window rate limiters mitigate credential-stuffing and denial-of-service attempts.

---

## Future Improvements

1. **Notification Queues**: Hooking Celery tasks to SMS/Email providers (Twilio/SendGrid) for automated appointment reminders.
2. **Multi-Factor Authentication (MFA)**: Adding TOTP-based two-factor authentication for healthcare staff.
3. **Database Read Replicas**: Adding read/write query splitting in SQLAlchemy for read-heavy diagnostic catalogue lookups under extreme traffic.
