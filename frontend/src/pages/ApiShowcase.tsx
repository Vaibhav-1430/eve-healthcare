import React, { useState } from 'react';
import {
  ExternalLink,
  Shield,
  Database,
  Cpu,
  Repeat,
  Gauge,
  Layers,
  CheckCircle2,
  Workflow,
  Copy,
  Check,
} from 'lucide-react';

interface EndpointItem {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
  description: string;
  auth: boolean;
  notes?: string;
}

export const ApiShowcase: React.FC = () => {
  const [copiedPath, setCopiedPath] = useState<string | null>(null);

  const handleCopy = (path: string) => {
    navigator.clipboard.writeText(path);
    setCopiedPath(path);
    setTimeout(() => setCopiedPath(null), 1500);
  };

  const architectureCards = [
    {
      title: 'JWT Authentication',
      icon: Shield,
      description:
        'Stateless Bearer tokens with HS256 algorithm and bcrypt password hashing. Secured endpoints extract current user dependency from authorization headers.',
      badge: 'Core Auth',
    },
    {
      title: 'PostgreSQL & Async SQLAlchemy',
      icon: Database,
      description:
        'SQLAlchemy 2.0 async engine with asyncpg. Enforces strict schema validations, unique constraints on bookings and centres, and managed via Alembic.',
      badge: 'Persistence',
    },
    {
      title: 'Redis Caching & Queue',
      icon: Layers,
      description:
        'Redis serves as an in-memory broker and cache. Caches centre/test lookups with TTL invalidation on writes and backs Celery background task queuing.',
      badge: 'In-Memory',
    },
    {
      title: 'Celery Background Tasks',
      icon: Cpu,
      description:
        'Asynchronous task processing for long-running jobs, webhooks, and retry pipelines decoupled from the core HTTP request/response lifecycle.',
      badge: 'Async Worker',
    },
    {
      title: 'Idempotent Webhooks',
      icon: Repeat,
      description:
        'Payment gateway callbacks feature database-level uniqueness on webhook event IDs and provider references. Duplicate webhooks return HTTP 200 without duplicate state transitions.',
      badge: 'Reliability',
    },
    {
      title: 'Rate Limiting',
      icon: Gauge,
      description:
        'FastAPI slowapi limiter protecting sensitive authentication endpoints (10 requests/minute per client IP) mitigating brute-force attacks.',
      badge: 'Security',
    },
    {
      title: 'Standardized Pagination',
      icon: Layers,
      description:
        'All listing endpoints support `page` and `page_size` query parameters, returning structured metadata: items, total records, page count, and page size.',
      badge: 'API Design',
    },
    {
      title: 'Strict State Machine',
      icon: Workflow,
      description:
        'Deterministic booking lifecycle: PENDING -> CONFIRMED (on payment success) or FAILED (on payment failure), or CANCELLED (if cancelled before confirmation). Disallows invalid state jumps.',
      badge: 'Domain Logic',
    },
  ];

  const apiSections: { title: string; endpoints: EndpointItem[] }[] = [
    {
      title: 'Authentication',
      endpoints: [
        {
          method: 'POST',
          path: '/auth/signup',
          description: 'Register a new user account with bcrypt password hashing.',
          auth: false,
          notes: 'Rate limited to 10 req/min. Validates email format and 8+ char password.',
        },
        {
          method: 'POST',
          path: '/auth/login',
          description: 'Authenticate user credentials and issue signed JWT access token.',
          auth: false,
          notes: 'Rate limited to 10 req/min. Returns user profile and Bearer token.',
        },
      ],
    },
    {
      title: 'Diagnostic Centres & Tests',
      endpoints: [
        {
          method: 'POST',
          path: '/centres/',
          description: 'Create a new diagnostic laboratory centre.',
          auth: true,
          notes: 'Enforces location and centre name requirements.',
        },
        {
          method: 'GET',
          path: '/centres/',
          description: 'List registered diagnostic centres with pagination and caching.',
          auth: false,
          notes: 'Supports page & page_size queries. Cached via Redis.',
        },
        {
          method: 'GET',
          path: '/centres/{id}',
          description: 'Retrieve diagnostic centre details by unique UUID.',
          auth: false,
        },
        {
          method: 'POST',
          path: '/centres/{id}/tests',
          description: 'Register a diagnostic test under a specific centre.',
          auth: true,
          notes: 'Requires decimal price and test name.',
        },
        {
          method: 'GET',
          path: '/centres/{id}/tests',
          description: 'List diagnostic tests offered by a specific centre.',
          auth: false,
          notes: 'Supports pagination. Returns live pricing.',
        },
        {
          method: 'GET',
          path: '/tests/{id}',
          description: 'Retrieve diagnostic test details and pricing.',
          auth: false,
        },
      ],
    },
    {
      title: 'Bookings',
      endpoints: [
        {
          method: 'POST',
          path: '/bookings/',
          description: 'Create a new appointment booking for a test at a centre.',
          auth: true,
          notes:
            'Derives booking amount strictly from test price in database. Validates future datetime.',
        },
        {
          method: 'GET',
          path: '/bookings/',
          description: 'Retrieve paginated bookings belonging to the authenticated user.',
          auth: true,
          notes: 'Scoped to current user token. Supports pagination.',
        },
        {
          method: 'GET',
          path: '/bookings/{id}',
          description: 'Retrieve single booking record by UUID.',
          auth: true,
          notes: 'Protected by authorization checks (IDOR protection).',
        },
        {
          method: 'POST',
          path: '/bookings/{id}/cancel',
          description: 'Cancel a pending appointment.',
          auth: true,
          notes: 'Validates state machine rules: only PENDING bookings can be cancelled.',
        },
      ],
    },
    {
      title: 'Payments & Simulation',
      endpoints: [
        {
          method: 'POST',
          path: '/payments/',
          description: 'Simulate an external payment gateway transaction.',
          auth: true,
          notes:
            'Amount is never client-supplied; backend derives amount directly from booking record.',
        },
      ],
    },
    {
      title: 'Webhooks & Asynchronous Processing',
      endpoints: [
        {
          method: 'POST',
          path: '/payments/webhook/',
          description: 'Process payment gateway event with idempotent deduplication.',
          auth: false,
          notes:
            'Atomic uniqueness on webhook events. Re-delivered webhooks return HTTP 200 without duplicate transitions.',
        },
      ],
    },
  ];

  const getMethodBadge = (method: string) => {
    switch (method) {
      case 'GET':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'POST':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'PUT':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'DELETE':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-teal-700 bg-teal-50 px-2 py-0.5 rounded border border-teal-200 uppercase">
              Engineering Architecture
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900">
            Backend API &amp; Architecture Showcase
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 max-w-2xl">
            A comprehensive architectural view of the EVE Healthcare backend system designed for
            technical interviews and engineering review.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <a
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2.5 text-xs sm:text-sm font-semibold text-white bg-teal-600 hover:bg-teal-700 rounded-lg shadow-sm transition-colors"
          >
            <span>Open Swagger Docs</span>
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>

      {/* Visual Workflow: Webhook & Idempotency Pipeline */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 shadow-sm space-y-4">
        <div>
          <h2 className="text-base font-bold text-slate-900">
            Webhook &amp; Idempotency Architecture
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            How payment events traverse the gateway simulation, Celery workers, and database state machine.
          </p>
        </div>

        <div className="p-6 rounded-xl bg-slate-50 border border-slate-200 overflow-x-auto">
          <div className="flex items-center justify-between min-w-[620px] text-xs">
            {/* Step 1 */}
            <div className="flex flex-col items-center text-center w-32">
              <div className="w-10 h-10 rounded-xl bg-teal-600 text-white flex items-center justify-center font-bold shadow-sm mb-2">
                1
              </div>
              <span className="font-semibold text-slate-900">Payment Simulation</span>
              <span className="text-[11px] text-slate-500 mt-0.5">POST /payments/</span>
            </div>

            <div className="h-0.5 flex-1 bg-teal-300 mx-2" />

            {/* Step 2 */}
            <div className="flex flex-col items-center text-center w-36">
              <div className="w-10 h-10 rounded-xl bg-teal-600 text-white flex items-center justify-center font-bold shadow-sm mb-2">
                2
              </div>
              <span className="font-semibold text-slate-900">Webhook Dispatch</span>
              <span className="text-[11px] text-slate-500 mt-0.5">Celery / Worker Queue</span>
            </div>

            <div className="h-0.5 flex-1 bg-teal-300 mx-2" />

            {/* Step 3 */}
            <div className="flex flex-col items-center text-center w-36">
              <div className="w-10 h-10 rounded-xl bg-teal-600 text-white flex items-center justify-center font-bold shadow-sm mb-2">
                3
              </div>
              <span className="font-semibold text-slate-900">Idempotency Check</span>
              <span className="text-[11px] text-slate-500 mt-0.5">PostgreSQL event_id check</span>
            </div>

            <div className="h-0.5 flex-1 bg-teal-300 mx-2" />

            {/* Step 4 */}
            <div className="flex flex-col items-center text-center w-36">
              <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold shadow-sm mb-2">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <span className="font-semibold text-slate-900">State Transition</span>
              <span className="text-[11px] text-slate-500 mt-0.5">PENDING → CONFIRMED</span>
            </div>
          </div>
        </div>
      </div>

      {/* Engineering Pillars Grid */}
      <div>
        <h2 className="text-base font-bold text-slate-900 mb-4">Core Engineering Pillars</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {architectureCards.map((card) => {
            const Icon = card.icon;
            return (
              <div
                key={card.title}
                className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className="w-9 h-9 rounded-lg bg-teal-50 border border-teal-100 flex items-center justify-center text-teal-700">
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="text-[10px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                      {card.badge}
                    </span>
                  </div>
                  <h3 className="text-sm font-semibold text-slate-900">{card.title}</h3>
                  <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
                    {card.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Live Endpoints Catalog */}
      <div className="space-y-6">
        <div>
          <h2 className="text-base font-bold text-slate-900">API Endpoints Catalog</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Real REST endpoints provided by the running FastAPI backend.
          </p>
        </div>

        {apiSections.map((section) => (
          <div
            key={section.title}
            className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden"
          >
            <div className="p-4 border-b border-slate-100 bg-slate-50/70 flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                {section.title}
              </h3>
              <span className="text-[11px] text-slate-400">
                {section.endpoints.length} endpoints
              </span>
            </div>

            <div className="divide-y divide-slate-100">
              {section.endpoints.map((ep) => (
                <div
                  key={ep.path + ep.method}
                  className="p-4 sm:px-6 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3 hover:bg-slate-50/50 transition-colors"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2.5 flex-wrap">
                      <span
                        className={`text-xs font-bold px-2 py-0.5 rounded border ${getMethodBadge(
                          ep.method
                        )}`}
                      >
                        {ep.method}
                      </span>
                      <span className="font-mono text-xs font-semibold text-slate-900">
                        {ep.path}
                      </span>
                      {ep.auth && (
                        <span className="text-[10px] font-medium text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">
                          JWT Required
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-600">{ep.description}</p>
                    {ep.notes && (
                      <p className="text-[11px] text-slate-400 italic">Note: {ep.notes}</p>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleCopy(ep.path)}
                      className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded hover:bg-slate-50 transition-colors"
                      title="Copy endpoint path"
                    >
                      {copiedPath === ep.path ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-600" />
                          <span className="text-emerald-600">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5 text-slate-400" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
