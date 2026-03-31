# Architecture Research

**Domain:** Real-time logistics dashboard (Google Sheets data source)
**Researched:** 2026-03-31
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     BROWSER (Client)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Dashboard │  │ Filters  │  │  Charts  │  │  Tables  │     │
│  │  Layout   │  │  Panel   │  │  (KPIs)  │  │  (Data)  │     │
│  └────┬──────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       └──────────────┴──────────────┴──────────────┘          │
│                          │ fetch / SSE                        │
├──────────────────────────┼──────────────────────────────────┤
│                    FASTAPI SERVER                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │   Auth   │  │   API    │  │   SSE    │  │  Static  │     │
│  │Middleware│  │ Endpoints│  │ /stream  │  │  Files   │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┘     │
│       │              │             │                          │
│  ┌────┴──────────────┴─────────────┴──────────────────┐      │
│  │              Data Service Layer                     │      │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │      │
│  │  │  Sheets    │  │   Data     │  │    KPI     │    │      │
│  │  │  Reader    │  │ Transformer│  │ Calculator │    │      │
│  │  └─────┬──────┘  └────────────┘  └────────────┘    │      │
│  └────────┼───────────────────────────────────────────┘      │
│           │                                                   │
├───────────┼──────────────────────────────────────────────────┤
│           │         IN-MEMORY CACHE                           │
│  ┌────────┴──────────────────────────────────────────┐       │
│  │  Cached sheet data + TTL (30-60s refresh cycle)   │       │
│  └───────────────────────────────────────────────────┘       │
│           │                                                   │
├───────────┼──────────────────────────────────────────────────┤
│           ▼        EXTERNAL SERVICE                           │
│  ┌───────────────────────────────────────────────────┐       │
│  │  Google Sheets API v4 (Service Account auth)      │       │
│  │  Spreadsheet: CONTROL CITAS BOMI                  │       │
│  │  Tabs: Actual | TIPOLOGIAS | historico            │       │
│  └───────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Auth Middleware | Gate all routes behind login | FastAPI `Depends()` with session cookies or JWT |
| API Endpoints | Serve dashboard HTML + JSON data | FastAPI routes returning Jinja2 templates or JSON |
| SSE Stream | Push data updates to connected browsers | FastAPI `StreamingResponse` with `text/event-stream` |
| Sheets Reader | Read raw data from Google Sheets API v4 | Reuse `sheets/auth.py` + `sheets/reader.py` from Diageo |
| Data Transformer | Parse raw rows into typed domain objects | Python dataclasses/Pydantic models for delivery records |
| KPI Calculator | Compute metrics from delivery data | Pure functions: compliance %, counts by status, trends |
| In-Memory Cache | Avoid hitting Sheets API on every request | Dict with TTL; background refresh via `asyncio.create_task` |
| Static Files | Serve CSS, JS, images | FastAPI `StaticFiles` mount |

## Recommended Project Structure

```
bomi-control-tower/
├── app.py                  # FastAPI app, lifespan, route registration
├── main.py                 # Uvicorn entry: `uvicorn app:app`
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment blueprint
├── Dockerfile              # Container for Render
├── .env.example            # Template for required env vars
│
├── sheets/                 # Google Sheets integration (reused from Diageo)
│   ├── __init__.py
│   ├── auth.py             # Service Account authentication (copy from Diageo)
│   ├── reader.py           # Read CONTROL CITAS BOMI tabs
│   └── config.py           # Sheet ID, tab names, column mappings
│
├── domain/                 # Business logic (no framework dependencies)
│   ├── __init__.py
│   ├── models.py           # DeliveryRecord, ServiceType, ComplianceStatus
│   ├── kpis.py             # KPI calculation: compliance %, on-time trends
│   └── filters.py          # Filter/query logic for date, tipo, placa, etc.
│
├── services/               # Application services (orchestrate domain + infra)
│   ├── __init__.py
│   ├── cache.py            # In-memory cache with TTL + background refresh
│   └── data_service.py     # Fetch → transform → cache pipeline
│
├── auth/                   # Authentication
│   ├── __init__.py
│   ├── middleware.py        # Auth dependency for FastAPI routes
│   └── users.py            # User store (env-based or simple JSON for v1)
│
├── routes/                 # FastAPI route handlers
│   ├── __init__.py
│   ├── dashboard.py        # Main dashboard views (operational, executive, client)
│   ├── api.py              # JSON API endpoints for AJAX data fetching
│   ├── stream.py           # SSE endpoint for real-time push
│   └── login.py            # Login/logout routes
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Shared layout (nav, auth status, CSS/JS includes)
│   ├── login.html          # Login form
│   ├── dashboard.html      # Main operational dashboard
│   ├── executive.html      # Executive KPI view
│   └── client.html         # Client-facing view (for Orlando/BOMI)
│
└── static/                 # Frontend assets
    ├── css/
    │   └── dashboard.css   # Dashboard styles
    ├── js/
    │   ├── dashboard.js    # Client-side rendering, filters, SSE listener
    │   └── charts.js       # Chart rendering (Chart.js or similar)
    └── img/
```

### Structure Rationale

- **sheets/:** Direct copy-adapt from Diageo project. Proven pattern. Isolated so it only knows about Google APIs, not the dashboard.
- **domain/:** Pure business logic. No FastAPI, no Google, no HTML. Models and KPI calculations that can be unit-tested in isolation.
- **services/:** Orchestration layer. Coordinates sheets reading, caching, and transformation. The "how often do we refresh" and "how do we cache" decisions live here.
- **routes/:** Thin HTTP handlers. Call services, pass data to templates. No business logic in route handlers.
- **auth/:** Separate because auth is a cross-cutting concern. Started simple (env-based users), can be swapped for OAuth/SSO later without touching other code.
- **templates/ + static/:** Standard Jinja2 pattern matching the Diageo project. No SPA framework needed for this scale.

## Architectural Patterns

### Pattern 1: Background Cache Refresh (Core Pattern)

**What:** A background asyncio task periodically fetches fresh data from Google Sheets and stores it in an in-memory cache. All HTTP requests read from cache, never directly from Sheets API.

**When to use:** Always. This is the central pattern for the entire system. Google Sheets API has rate limits (~60 requests/minute/user for reads). Without caching, 10 concurrent dashboard users would exhaust the quota instantly.

**Trade-offs:**
- Pro: Fast responses (sub-millisecond cache reads), API quota protection, decouples request latency from Sheets API latency
- Con: Data is stale by up to the refresh interval (30-60 seconds), slightly more complex startup

**Example:**
```python
# services/cache.py
import asyncio
import time
from typing import Optional
from domain.models import DashboardData

class SheetCache:
    def __init__(self, refresh_interval_seconds: int = 30):
        self._data: Optional[DashboardData] = None
        self._last_refresh: float = 0
        self._interval = refresh_interval_seconds
        self._lock = asyncio.Lock()

    @property
    def data(self) -> Optional[DashboardData]:
        return self._data

    async def start_background_refresh(self, fetch_fn):
        """Run as asyncio task in FastAPI lifespan."""
        while True:
            try:
                # Run blocking Sheets API call in thread pool
                raw = await asyncio.to_thread(fetch_fn)
                async with self._lock:
                    self._data = raw
                    self._last_refresh = time.time()
            except Exception as exc:
                # Log but don't crash — serve stale data
                import logging
                logging.getLogger(__name__).error("Cache refresh failed: %s", exc)
            await asyncio.sleep(self._interval)
```

### Pattern 2: Server-Sent Events for Live Updates

**What:** An SSE endpoint streams data change events to connected browsers. The browser's `EventSource` API reconnects automatically on disconnect. Simpler than WebSockets for one-directional data push.

**When to use:** When the dashboard needs to update without manual page refresh. The cache refresh loop detects changes and pushes them via SSE.

**Trade-offs:**
- Pro: Native browser support (EventSource API), automatic reconnection, simpler than WebSockets, HTTP/2 compatible
- Con: Unidirectional (server-to-client only, which is exactly what we need), keeps connections open (manageable at <50 concurrent users)

**Example:**
```python
# routes/stream.py
import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/api/stream")
async def event_stream(request):
    async def generate():
        last_hash = None
        while True:
            data = cache.data
            current_hash = hash(str(data))
            if current_hash != last_hash:
                yield f"data: {json.dumps(data.to_summary_dict())}\n\n"
                last_hash = current_hash
            await asyncio.sleep(5)  # Check every 5 seconds

    return StreamingResponse(generate(), media_type="text/event-stream")
```

### Pattern 3: Server-Side Rendering with Progressive Enhancement

**What:** Jinja2 renders the initial page with data baked in. JavaScript then takes over for filtering, sorting, and SSE-driven updates. No SPA framework.

**When to use:** When the application is primarily a data display with filters. Avoids the complexity of React/Vue build tooling for a project this size.

**Trade-offs:**
- Pro: Fast initial load (no JS bundle to parse), SEO-friendly (not relevant here but a bonus), matches Diageo project patterns, simpler deployment
- Con: More page reloads for view switching (mitigated by AJAX), less rich interactivity than a SPA

## Data Flow

### Primary Data Flow (Read Path)

```
Google Spreadsheet (CONTROL CITAS BOMI)
    │
    │  Google Sheets API v4 (values.get)
    │  Triggered by: background asyncio task every 30-60s
    ▼
Sheets Reader (sheets/reader.py)
    │  Returns: list[list[str]] (raw rows)
    ▼
Data Transformer (domain/models.py)
    │  Parses raw rows → DeliveryRecord dataclasses
    │  Handles: date parsing, status enum mapping, null safety
    ▼
KPI Calculator (domain/kpis.py)
    │  Computes: compliance %, status counts, trends
    ▼
In-Memory Cache (services/cache.py)
    │  Stores: transformed data + computed KPIs
    │  TTL: 30-60 seconds
    ▼
API / Template Route (routes/)
    │  Reads from cache (sub-ms)
    │  Applies user filters (date, tipo, placa)
    ▼
Browser (Dashboard)
    │  Initial: full HTML from Jinja2
    │  Updates: SSE stream or AJAX polling
    ▼
User sees real-time delivery status
```

### Authentication Flow

```
User visits any route
    │
    ▼
Auth Middleware (Depends)
    ├── Has valid session cookie? → YES → Pass through to route
    └── No session? → Redirect to /login
                          │
                          ▼
                     Login Form (POST)
                          │
                          ▼
                     Verify credentials
                     (env-based or JSON file for v1)
                          │
                          ├── Valid → Set session cookie → Redirect to dashboard
                          └── Invalid → Show error
```

### Three Dashboard Views (Same Data, Different Projections)

```
Cached DashboardData
    │
    ├─── /dashboard (Operational View)
    │    Filters: date, tipo operacion, punto cargue, placa, asignacion
    │    Shows: live table of all deliveries, status colors, search
    │    Audience: Dispatchers, operations team
    │
    ├─── /executive (Executive View)
    │    Shows: KPI cards (compliance %, on-time trend), aggregate charts
    │    Audience: Management, directors
    │
    └─── /client (Client View)
    │    Shows: Filtered to BOMI's deliveries, compliance metrics
    │    Audience: Orlando (BOMI Supply Chain Manager)
    │
    All three read from the SAME cache — no separate data fetching.
```

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 1-10 users | Current architecture is fine. Single Render instance, in-memory cache, no DB needed. |
| 10-50 users | Still fine. SSE connections are lightweight. Monitor Sheets API quota. Consider increasing cache TTL to 60s. |
| 50+ users | Add Redis cache (shared across instances). Move SSE to WebSockets via a pub/sub broker. But this scale is unlikely for an internal ops tool. |

### Scaling Priorities

1. **First bottleneck — Google Sheets API quota:** At ~60 reads/min, aggressive cache refresh can hit limits. The background refresh pattern ensures we make exactly 1 request per refresh interval regardless of user count. A 30s interval = 2 requests/minute. Safe.
2. **Second bottleneck — SSE connections:** Each connected browser holds an open HTTP connection. At 50 users, that's 50 open connections. Uvicorn with asyncio handles this trivially. Only becomes a concern at 500+ simultaneous connections, which will never happen for this use case.

## Anti-Patterns

### Anti-Pattern 1: Direct Sheets API Calls from Route Handlers

**What people do:** Call `sheets.reader.read_actual()` inside every HTTP request handler.
**Why it's wrong:** Google Sheets API has rate limits and 200-500ms latency per call. Under load, requests queue up, users see slow pages, and the API quota exhausts. N users = N API calls per page load.
**Do this instead:** Background cache refresh. All routes read from in-memory cache. 1 API call per refresh interval, regardless of user count.

### Anti-Pattern 2: Storing All Logic in Route Handlers

**What people do:** Put data transformation, KPI calculations, and filtering logic directly in FastAPI route functions.
**Why it's wrong:** Untestable (requires HTTP context), unmaintainable (routes become 200+ lines), logic is duplicated across views.
**Do this instead:** Domain layer (`domain/`) for business logic, services layer (`services/`) for orchestration. Routes are thin — fetch from service, pass to template.

### Anti-Pattern 3: Using WebSockets When SSE Suffices

**What people do:** Implement full WebSocket support for a dashboard that only pushes data server-to-client.
**Why it's wrong:** WebSockets are bidirectional and more complex: need connection management, heartbeat, reconnection logic, and they don't work through some proxies/CDNs. Dashboard data flow is purely server-to-client.
**Do this instead:** SSE via `EventSource`. Native browser API, automatic reconnection, works through all HTTP proxies, simpler server code.

### Anti-Pattern 4: Adding a Database for "Performance"

**What people do:** Add PostgreSQL or SQLite to cache Sheets data "for performance."
**Why it's wrong:** For ~390 rows, an in-memory Python dict is faster than any database. Adding a DB introduces schema management, migrations, sync complexity, and another failure point — all to store data that already lives in Google Sheets and fits in <1MB of RAM.
**Do this instead:** In-memory cache with periodic refresh. The data set (~390 rows x 15 columns) is tiny. If the app restarts, the cache rebuilds in <2 seconds from Sheets API.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Google Sheets API v4 | Service Account auth, `values.get` for batch reads | Reuse `sheets/auth.py` from Diageo. Share same Service Account. Must grant spreadsheet access to the SA email. |
| Render (hosting) | Docker container, web service type (not worker) | Unlike Diageo (which is a worker), this needs HTTP port exposed. `render.yaml` with `type: web`. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| sheets/ to domain/ | Function calls returning raw data | Sheets module returns `list[list[str]]`, domain transforms to typed models. No Sheets types leak into domain. |
| domain/ to routes/ | Via services layer | Routes never import from sheets/ directly. Always go through `services/data_service.py`. |
| routes/ to templates/ | Jinja2 template context dicts | Routes pass Python dicts/dataclasses to templates. Templates never call services. |
| Browser to Server | HTTP (HTML pages) + SSE (live updates) + AJAX (filtered data) | Initial page load is full HTML. Subsequent updates via `/api/stream` (SSE) or `/api/data` (JSON). |

## Build Order (Dependencies Between Components)

The following order respects component dependencies — each phase can only be built after its prerequisites exist:

```
Phase 1: sheets/ (auth + reader)
    │     No dependencies. Reuse from Diageo. Can test standalone.
    │     Deliverable: `python -c "from sheets.reader import read_actual; print(read_actual())"`
    ▼
Phase 2: domain/ (models + KPIs)
    │     Depends on: sheets/ (needs to know what data looks like)
    │     Deliverable: Typed DeliveryRecord objects, KPI calculations, unit tests
    ▼
Phase 3: services/ (cache + data_service)
    │     Depends on: sheets/ + domain/
    │     Deliverable: Background refresh loop, cached data accessible via service
    ▼
Phase 4: routes/ + templates/ (dashboard views)
    │     Depends on: services/ (reads cached data)
    │     Deliverable: Working dashboard with all three views, filters, tables
    ▼
Phase 5: auth/ (authentication)
    │     Depends on: routes/ (wraps existing routes with auth middleware)
    │     Deliverable: Login page, protected routes, session management
    ▼
Phase 6: SSE streaming (real-time updates)
    │     Depends on: services/ cache + working dashboard
    │     Deliverable: Dashboard auto-updates without page refresh
    ▼
Phase 7: Deployment (Render)
          Depends on: all above
          Deliverable: Live URL, GOOGLE_SA_KEY configured, health check
```

**Why this order:**
- Sheets reader first because everything depends on data access. If Sheets API integration fails, nothing else matters.
- Domain models second because KPI calculations and data types must be defined before the UI can render them.
- Cache service third because the dashboard must read from cache, not directly from Sheets.
- Dashboard views fourth because they're the core deliverable and can be tested with cached data.
- Auth fifth (not first) because auth is easier to add as middleware around working routes than to build login before there's anything to protect. Develop locally without auth friction, add auth before deployment.
- SSE sixth because it's a progressive enhancement — the dashboard works without it (manual refresh).
- Deployment last because it depends on everything being functional.

## Sources

- Google Sheets API v4 values.get documentation (HIGH confidence — used extensively in Diageo project)
- Diageo proyecto proceso-tarificacion-diageo source code: `sheets/auth.py`, `sheets/reader.py`, `app.py`, `render.yaml` (HIGH confidence — proven production patterns)
- FastAPI official documentation: lifespan events, StreamingResponse, Depends middleware (HIGH confidence — established framework patterns)
- SSE / EventSource browser API specification (HIGH confidence — W3C standard, widely supported)

---
*Architecture research for: BOMI Control Tower logistics dashboard*
*Researched: 2026-03-31*
