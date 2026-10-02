# EVE Healthcare — Frontend Application

A modern, production-grade frontend client for the **EVE Healthcare Diagnostic Management Platform**. Designed to showcase and interface with the FastAPI backend, demonstrating real end-to-end user workflows: authentication, diagnostic centre discovery, appointment scheduling, and payment simulation.

---

## 1. Project Overview

The EVE Healthcare frontend is an internal healthcare SaaS dashboard built to demonstrate:
- **Stateless JWT Authentication**: Secure signup and signin flows interfacing with FastAPI rate limiters.
- **Diagnostic Discovery**: Real-time browsing and filtering of accredited diagnostic centres and lab tests.
- **Appointment Scheduling**: Booking workflows where the backend strictly enforces future appointment validation and server-derived pricing.
- **Simulated Payment Gateway**: Visualizing asynchronous state transitions (`PENDING` → `CONFIRMED` or `FAILED`) backed by Celery and Redis.
- **Engineering Architecture Showcase**: Technical breakdown of backend systems (FastAPI, PostgreSQL, Redis, Celery, idempotent webhooks) for evaluation and interviews.

---

## 2. Tech Stack

- **Framework**: [React 18](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/)
- **Bundler & Tooling**: [Vite 6](https://vitejs.dev/)
- **Routing**: [React Router v6](https://reactrouter.com/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/) (healthcare palette: clean slate, crisp borders, teal accents)
- **HTTP Client**: [Axios](https://axios-http.com/) with request/response interceptors for Bearer auth and 401 handling
- **Icons**: [Lucide React](https://lucide.dev/)

---

## 3. Setup & Installation

Ensure Node.js (v18+) is installed on your system.

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install
```

---

## 4. Environment Variables

Create a `.env` file in the `frontend/` directory (or copy from `.env.example`):

```bash
# frontend/.env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

| Variable | Description | Default |
|---|---|---|
| `VITE_API_BASE_URL` | Base URL of the running FastAPI backend | `http://127.0.0.1:8000` |

---

## 5. Running Locally

### Development Mode

```bash
npm run dev
```
The application will launch at: **http://localhost:5173**

### Production Build

```bash
npm run build
npm run preview
```

---

## 6. Backend Dependency

This frontend is designed to consume the live EVE Healthcare FastAPI backend.

Ensure the backend services are running:
1. **PostgreSQL**: Running on port `5432` with database `eve_healthcare`.
2. **Redis**: Running on port `6379`.
3. **Celery Worker**:
   ```bash
   celery -A app.core.celery worker --pool=solo --loglevel=info
   ```
4. **FastAPI Application**:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

Backend URLs:
- **API Base**: `http://127.0.0.1:8000`
- **Swagger Documentation**: `http://127.0.0.1:8000/docs`
- **Health Check**: `http://127.0.0.1:8000/health`

---

## 7. Available Pages & Routes

| Path | Access | Description |
|---|---|---|
| `/login` | Public | User authentication with email and password |
| `/signup` | Public | New account registration (enforces backend 8+ char password) |
| `/dashboard` | Protected | Live summary telemetry, recent bookings, and quick action shortcuts |
| `/centres` | Protected | Diagnostic centres directory with search and pagination |
| `/centres/:id` | Protected | Centre profile showing accredited tests, descriptions, and pricing |
| `/book` | Protected | Test booking flow with date-time scheduling and backend price sync |
| `/bookings` | Protected | User appointments list with status filters (`PENDING`, `CONFIRMED`, `FAILED`, `CANCELLED`) |
| `/bookings/:id` | Protected | Detailed appointment view with visual lifecycle timeline and cancel action |
| `/payment-demo` | Protected | Simulated gateway interface for triggering payment webhooks |
| `/api-showcase` | Protected | Technical architecture breakdown, pipeline diagram, and endpoint catalog |

---

## 8. API Integration Layer

All backend interactions are organized under `src/api/`:
- **`client.ts`**: Central Axios instance with automated Bearer token attachment and centralized error extraction.
- **`auth.ts`**: `POST /auth/signup`, `POST /auth/login`.
- **`centres.ts`**: `GET /centres/`, `GET /centres/{id}`.
- **`tests.ts`**: `GET /centres/{id}/tests`, `GET /tests/{id}`.
- **`bookings.ts`**: `POST /bookings/`, `GET /bookings/`, `GET /bookings/{id}`, `POST /bookings/{id}/cancel`.
- **`payments.ts`**: `POST /payments/` (strictly excludes client-side amount override).

---

## 9. Authentication Flow

1. User submits credentials at `/login`.
2. Backend validates bcrypt hash and issues a signed JWT (`POST /auth/login`).
3. Frontend stores the token securely in `localStorage` and updates `AuthContext`.
4. `ProtectedRoute` allows access to dashboard and internal routes.
5. In the event of token expiry (401 response), the Axios interceptor clears stored session tokens and routes the user back to `/login`.

---

## 10. Payment Demo (`/payment-demo`)

The payment page provides an interactive demonstration of the backend's simulated payment processing:
- Select an unpaid appointment (`PENDING` or `FAILED`).
- Review the immutable amount derived by the backend.
- Choose a simulated gateway outcome:
  - **SUCCESS**: Triggers webhook dispatch and transitions state to `CONFIRMED`.
  - **FAILED**: Transitions state to `FAILED` and permits retry.
- Displays live provider reference and confirms real-time PostgreSQL record updates.

---

## 11. API Showcase (`/api-showcase`)

A dedicated section built for engineering interviewers and reviewers:
- **Visual Webhook Pipeline**: Illustrates the progression from payment request through Celery queue, idempotent event verification, and booking confirmation.
- **Architectural Pillars**: Highlights JWT security, async PostgreSQL with SQLAlchemy 2.0, Redis caching, Celery workers, slowapi rate limiting, and state machine validation.
- **Interactive Endpoint Catalog**: Complete listing of methods, paths, JWT requirements, and one-click path copying.
- **Direct Swagger Access**: One-click button linking to live interactive OpenAPI docs.

---

## 12. Screenshots Section

<!-- Screenshots placeholder -->
*Place product screenshots here for demonstration in portfolio or PR submissions.*
- `screenshots/dashboard.png` — Telemetry & Recent Bookings
- `screenshots/centres.png` — Diagnostic Centres Directory
- `screenshots/booking_flow.png` — Appointment Scheduling
- `screenshots/payment_demo.png` — Simulated Payment Gateway
- `screenshots/api_showcase.png` — Engineering Architecture Showcase
