<!-- GSD:project-start source:PROJECT.md -->
## Project

**BOMI Control Tower**

A web-based Control Tower dashboard that reads delivery/appointment data from a Google Spreadsheet ("CONTROL CITAS BOMI") and provides real-time visibility into BOMI's logistics operations. Tracks service fulfillment, appointment compliance, and incidencias for the operations team, management, and BOMI's Supply Chain Manager (Orlando).

**Core Value:** Real-time visibility into whether deliveries are meeting their scheduled appointments — so operations can act before problems compound.

### Constraints

- **Tech stack**: Python + FastAPI + HTML/JS dashboard (same as Diageo tarificación project)
- **Deployment**: Render (same infra as Diageo, GOOGLE_SA_KEY base64 pattern)
- **Authentication**: Login required (specific mechanism TBD)
- **Google credentials**: Reuse existing Service Account from proceso-tarificacion-diageo
- **Data freshness**: Real-time reads from Google Sheets API (no local DB cache for v1)
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Recommended Stack
### Core Technologies
| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.11+ | Runtime | Matches Diageo project (pyproject.toml targets 3.11). Stable, widely deployed on Render. 3.12 is fine too but 3.11 is the safe bet for compatibility with google-api-python-client. |
| FastAPI | >=0.115.0 | Web framework | Already used in Diageo project. Async-native, perfect for SSE/polling endpoints. Jinja2 templating built-in. Direct code reuse from existing project. |
| Uvicorn | >=0.30.0 | ASGI server | Standard FastAPI server. Use `uvicorn[standard]` for watchfiles (dev reload) and httptools (performance). Same as Diageo project. |
| Jinja2 | >=3.1.4 | HTML templating | Server-side rendering for dashboard views. Already proven in Diageo's cotizador. Keeps the stack simple -- no JS build step needed. |
| HTMX | 2.0.x (CDN) | Frontend interactivity | Enables real-time dashboard updates via SSE or polling WITHOUT a JS framework. Partial page updates, no React/Vue complexity. Perfect for a data dashboard that needs periodic refresh. |
### Google Sheets Integration (REUSED from Diageo)
| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| google-api-python-client | >=2.100.0 | Sheets API v4 | Direct reuse of `sheets/auth.py` and `sheets/reader.py` from Diageo. Battle-tested Service Account auth with base64 GOOGLE_SA_KEY pattern for Render deployment. |
| google-auth | >=2.20.0 | Google credential management | Required by google-api-python-client. Handles Service Account JSON parsing, token refresh. |
| google-auth-oauthlib | >=1.0.0 | OAuth flow (dev only) | Only needed if adding OAuth user flow. Diageo project includes it; keep for consistency but not strictly required since BOMI uses Service Account auth only. |
### Authentication
| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| python-jose[cryptography] | >=3.3.0 | JWT token handling | Lightweight JWT encoding/decoding. Better than PyJWT for FastAPI because it includes JWS/JWE support out of the box. Used by FastAPI's own security examples. |
| passlib[bcrypt] | >=1.7.4 | Password hashing | Industry standard bcrypt hashing. FastAPI security docs recommend this exact library. |
| python-multipart | >=0.0.9 | Form data parsing | Required by FastAPI for form-based login (POST with username/password). Already used in Diageo project. |
### Frontend (No Build Step)
| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| HTMX | 2.0.x | Partial page updates, SSE | CDN-loaded, zero build tooling. `hx-get` for polling, `hx-ext="sse"` for server-sent events. The standard choice for Python server-rendered dashboards that need interactivity without SPA complexity. |
| Alpine.js | 3.x | Lightweight JS reactivity | CDN-loaded. For dropdown filters, toggle states, small UI interactions that HTMX doesn't cover. Pairs perfectly with HTMX -- they solve different problems. |
| Chart.js | 4.x | Data visualization | CDN-loaded. Appointment compliance trends, service distribution charts. Simpler API than D3.js, sufficient for KPI dashboards. |
### Development Tools
| Tool | Purpose | Notes |
|------|---------|-------|
| Ruff | Linting + formatting | Already configured in Diageo's pyproject.toml. Replaces flake8 + isort + black. Use same config (target-version = "py311", line-length = 120). |
| pytest | Testing | Same markers approach as Diageo. Focus on `smoke` and `integration` markers. |
| pre-commit | Git hooks | Enforces ruff + pip-audit on every commit. Same as Diageo. |
| pip-audit | Dependency security | Checks for known vulnerabilities. Already in Diageo's dev deps. |
| mypy | Type checking | Optional but recommended. Use same strict settings for domain/application layers. |
### Deployment
| Technology | Purpose | Notes |
|------------|---------|-------|
| Render | Hosting platform | Same as Diageo. Web Service type (not Worker). Free tier works for MVP. GOOGLE_SA_KEY as base64 env var. |
| Docker | Containerization | Same Dockerfile pattern as Diageo. Python 3.11-slim base image. |
| render.yaml | Blueprint | Infrastructure-as-code. Web service, no database needed for v1 (reads directly from Sheets). |
## Installation
# Core (requirements.txt)
# Google Sheets integration
# Authentication
# Dev dependencies
## Alternatives Considered
| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| HTMX (partial updates) | React/Next.js | Only if you need complex client-side state (drag-and-drop, real-time collaboration). Massive overkill for a read-only dashboard. Adds npm build step, doubles deployment complexity. |
| HTMX SSE extension | WebSockets (via FastAPI) | Only if you need bidirectional communication (chat, collaborative editing). SSE is simpler, works through proxies/CDNs, and is sufficient for server-to-client dashboard updates. |
| Jinja2 (server-rendered) | Streamlit / Dash | Only if you want zero HTML/CSS and accept their opinionated UI. Streamlit cannot do custom auth or custom layouts well. Dash is heavier than FastAPI for this use case. Not deployable on Render as easily. |
| Chart.js | Plotly.js / D3.js | Plotly: if you need interactive drill-downs (hover tooltips, zoom). D3.js: if you need highly custom visualizations. Chart.js is sufficient for bar/line/doughnut KPI charts. |
| python-jose | PyJWT | PyJWT works fine for basic JWT. python-jose has broader algorithm support and is what FastAPI tutorials use. Either is acceptable. |
| passlib[bcrypt] | argon2-cffi | Argon2 is technically more modern than bcrypt. But passlib+bcrypt is the established FastAPI ecosystem choice with more documentation and examples. |
| Hardcoded users (v1) | Full user DB (PostgreSQL) | For v1, 3-5 users with hashed passwords in env vars or a JSON config is fine. Add a DB when you need user management, audit logs, or >10 users. |
| Alpine.js | Vanilla JS | If you refuse any JS library. Alpine.js is 15KB and eliminates boilerplate for filter dropdowns and toggle states. Not worth going vanilla for this. |
| google-api-python-client | gspread | gspread is a simpler wrapper but adds a dependency. Diageo project already uses the official client directly. Stick with what's proven and reusable. |
## What NOT to Use
| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Streamlit | No custom auth, no custom layouts, cannot embed in existing FastAPI app, limited deployment options, not production-grade for multi-user dashboards | FastAPI + Jinja2 + HTMX |
| Dash (Plotly) | Opinionated layout system, heavyweight for a simple dashboard, fights against custom auth patterns, separate server process | FastAPI + Chart.js |
| React/Vue/Angular | Massive overkill for a read-only dashboard. Adds npm build step, doubles the codebase, requires API serialization layer. This is not an SPA. | HTMX + Alpine.js |
| SQLAlchemy / PostgreSQL (v1) | No database needed when Google Sheets IS the database. Adding a DB adds sync complexity, migration overhead, and a paid Render add-on. Defer to v2 if caching is needed. | Direct Sheets API reads |
| gspread | Additional wrapper dependency over the official Google API client. Diageo project already uses google-api-python-client directly with proven auth patterns. Adding gspread would mean two ways to talk to Sheets. | google-api-python-client (reuse from Diageo) |
| Flask | FastAPI is async-native, has built-in OpenAPI docs, better type validation, and is already the team's standard. Flask would be a downgrade. | FastAPI |
| Celery | No background task queue needed for v1. Sheets reads are fast (<1s). If you need scheduled cache refresh later, use FastAPI's `BackgroundTasks` or a simple `asyncio.create_task`. | FastAPI BackgroundTasks |
| NextAuth / Clerk / Auth0 | External auth services are overkill for 3-5 internal users. Adds external dependency, costs money at scale, and requires JS frontend integration. | Simple JWT with hardcoded users |
## Stack Patterns by Variant
- Use HTMX SSE extension (`hx-ext="sse"`) with FastAPI's `StreamingResponse`
- Server polls Sheets API every N seconds, pushes diffs to connected clients
- Caution: Google Sheets API has rate limits (60 requests/minute/user for reads)
- Use HTMX polling (`hx-trigger="every 30s"`) on dashboard components
- Simpler implementation, no SSE infrastructure needed
- Each client triggers its own Sheets API read (fine for <10 concurrent users)
- Add a server-side cache (in-memory dict with TTL, or Redis)
- Single background task polls Sheets API every 30s, updates cache
- All dashboard requests read from cache, not Sheets directly
- This avoids hitting Google API rate limits
- Add PostgreSQL on Render (same pattern as Diageo)
- Use psycopg2-binary (already in Diageo's requirements)
- Background task syncs Sheets -> DB periodically
- Dashboard reads from DB, Sheets becomes source-of-truth sync
## Version Compatibility
| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| FastAPI >=0.115.0 | Pydantic v2 (>=2.0) | FastAPI 0.100+ requires Pydantic v2. Do not install Pydantic v1. |
| FastAPI >=0.115.0 | Uvicorn >=0.30.0 | Standard pairing. Use `uvicorn[standard]` for best performance. |
| google-api-python-client >=2.100.0 | google-auth >=2.20.0 | Must be installed together. google-auth handles credential refresh. |
| python-jose >=3.3.0 | cryptography >=41.0.0 | The `[cryptography]` extra pulls in the correct version. |
| passlib >=1.7.4 | bcrypt >=4.0.0 | passlib 1.7.4 works with bcrypt 4.x. Avoid bcrypt 3.x (deprecated C backend). |
| Python 3.11 | All packages above | 3.11 is the baseline. 3.12 also works but 3.11 matches Diageo exactly. |
| HTMX 2.0.x | SSE extension | SSE extension is built into HTMX 2.x (no separate download needed). |
## Code Reuse from Diageo Project
| Source File | Reuse Strategy | Adaptation Needed |
|-------------|----------------|-------------------|
| `sheets/auth.py` | Copy directly | Trim scopes to `spreadsheets.readonly` and `drive.readonly`. Remove Gmail service. Remove OAuth flow (SA-only for BOMI). |
| `sheets/reader.py` | Copy pattern, rewrite content | Keep `_read_sheet_tab()` and `_get_cell()` helpers. Replace Diageo-specific column mappings with BOMI's 15 columns (FECHA, HORA DE CARGUE, etc.). |
| `app.py` | Copy structure | Keep lifespan pattern, Jinja2 setup, `format_cop()` filter. Replace cotizador routes with dashboard routes. Add auth middleware. |
| `pyproject.toml` | Copy and simplify | Keep ruff config, pytest config, mypy config. Remove Diageo-specific overrides. |
| `render.yaml` | Copy and adapt | Change to `type: web` (not worker). Remove database. Add CONTROL_CITAS_SHEET_ID env var. |
| `Dockerfile` | Copy directly | Minimal changes -- same Python 3.11-slim base, same pip install pattern. |
## Authentication Architecture (Recommended Approach)
- FastAPI dependency that reads JWT from cookie
- Returns 401 -> redirect to /login if missing/expired
- No Bearer tokens, no localStorage -- cookies are simpler for server-rendered apps
- Environment variable: DASHBOARD_USERS='[{"username":"orlando","password_hash":"$2b$12..."},...]'
- Or a users.json file on the server
- 3-5 users max, no self-registration
## Sources
- Diageo project `requirements.txt` -- verified existing dependency versions and patterns (HIGH confidence)
- Diageo project `sheets/auth.py` -- verified Google Service Account auth pattern (HIGH confidence)
- Diageo project `app.py` -- verified FastAPI + Jinja2 + lifespan pattern (HIGH confidence)
- Diageo project `pyproject.toml` -- verified ruff/mypy/pytest configuration (HIGH confidence)
- Diageo project `render.yaml` -- verified Render deployment pattern (HIGH confidence)
- FastAPI documentation patterns (training data, May 2025) -- MEDIUM confidence on exact latest version numbers
- HTMX documentation (training data, May 2025) -- MEDIUM confidence; HTMX 2.0 was stable by mid-2025
- Chart.js, Alpine.js versions (training data) -- MEDIUM confidence on exact latest versions
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->

## Skill routing

When the user's request matches an available skill, ALWAYS invoke it using the Skill
tool as your FIRST action. Do NOT answer directly, do NOT use other tools first.
The skill has specialized workflows that produce better results than ad-hoc answers.

Key routing rules:
- Product ideas, "is this worth building", brainstorming → invoke office-hours
- Bugs, errors, "why is this broken", 500 errors → invoke investigate
- Ship, deploy, push, create PR → invoke ship
- QA, test the site, find bugs → invoke qa
- Code review, check my diff → invoke review
- Update docs after shipping → invoke document-release
- Weekly retro → invoke retro
- Design system, brand → invoke design-consultation
- Visual audit, design polish → invoke design-review
- Architecture review → invoke plan-eng-review
- Save progress, checkpoint, resume → invoke checkpoint
- Code quality, health check → invoke health
