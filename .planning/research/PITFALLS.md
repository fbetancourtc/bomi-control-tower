# Domain Pitfalls

**Domain:** Healthcare logistics control tower dashboard with Google Sheets integration
**Project:** BOMI Control Tower
**Researched:** 2026-03-31
**Confidence:** HIGH (based on reference project production patterns + Google Sheets API documented behavior)

## Critical Pitfalls

Mistakes that cause rewrites, outages, or fundamental trust failures.

---

### Pitfall 1: Google Sheets API Rate Limit Exhaustion Under Polling

**What goes wrong:** The dashboard polls Google Sheets API on every page load or at a fixed interval (e.g., every 5-10 seconds). With multiple concurrent users (operations team + management + BOMI client), the app hammers the API. Google Sheets API v4 has a quota of **300 requests per minute per project** (for read operations) and **60 requests per minute per user per project**. A naive polling design with 5 users refreshing every 10 seconds = 30 req/min per user, blowing through per-user limits fast. When quotas are hit, the API returns `429 Too Many Requests` and the dashboard goes dark for all users simultaneously.

**Why it happens:** Developers treat Google Sheets like a database and implement request-per-client polling. The Diageo reference project does one-shot batch reads (read once, compute, respond), not sustained polling -- so the pattern doesn't transfer directly.

**Consequences:**
- Dashboard becomes unavailable during peak operations hours (exactly when it's most needed)
- Service Account quota exhaustion affects ALL apps sharing the same GCP project (including the Diageo tarificacion project)
- Ops team loses trust in dashboard reliability and reverts to manual spreadsheet checking

**Warning signs:**
- `HttpError 429` in logs
- Intermittent "data unavailable" states in the dashboard
- Diageo project starts failing API calls at the same time

**Prevention:**
1. Implement a **server-side cache layer** with a single polling loop: one background task reads the sheet every 30-60 seconds and caches results in memory. All HTTP requests serve from cache.
2. Use `If-Modified-Since` semantics at the app level: track a hash/version of the data and only re-fetch when stale.
3. Add exponential backoff with jitter on 429 responses.
4. Monitor quota usage via GCP Console and set up alerts at 70% utilization.

**Phase:** Phase 1 (Core Infrastructure) -- must be baked into the data layer from day one, not retrofitted.

---

### Pitfall 2: Sparse Row / Ragged Array Crashes

**What goes wrong:** Google Sheets API v4 returns rows as arrays **truncated at the last non-empty cell**. A row with data in columns A-L but empty columns M-O returns only 12 elements, not 15. Code that accesses `row[14]` (column O, OBSERVACIONES) crashes with `IndexError`. The BOMI spreadsheet has OBSERVACIONES as the last column -- it will frequently be empty, making every row a potential crash.

**Why it happens:** Developers assume the API returns fixed-width rows matching the header count. The Diageo reference project already solved this with `_get_cell(row, idx)` that returns `None` for out-of-bounds indices (see `reader.py:105-115`), proving this is a real production issue they encountered.

**Consequences:**
- Dashboard crashes on rows where operators haven't filled optional fields
- Silent data truncation if errors are caught but not handled properly
- Incomplete dashboard views that mislead operations decisions

**Warning signs:**
- `IndexError` or `KeyError` exceptions in data parsing
- Dashboard shows fewer rows than the spreadsheet contains
- Data discrepancies between dashboard and spreadsheet

**Prevention:**
1. Copy the `_get_cell(row, idx)` safe accessor pattern from the Diageo project.
2. Define a column index constant map (like Diageo's `COLUMN_MAP` in `config.py`) rather than hardcoded integers.
3. Add a startup validation that reads the header row and asserts expected columns exist at expected indices.
4. Log warnings (not errors) for rows shorter than expected, with row number for debugging.

**Phase:** Phase 1 (Data Adapter) -- this is foundational data parsing that everything else depends on.

---

### Pitfall 3: Column Index Drift When Spreadsheet Structure Changes

**What goes wrong:** Operations team adds, removes, or reorders columns in the Google Spreadsheet. The dashboard's hardcoded column indices silently read wrong data. CUMPLIÓ CITA was at index 10, but someone inserted a column before it and now index 10 is HORA DE LLEGADA. The dashboard reports compliance metrics using arrival times as SI/NO values.

**Why it happens:** The spreadsheet is managed by the ops team as a living document. There's no schema contract between the spreadsheet and the dashboard. The Diageo project's `reader.py` has a comment: `"CRITICAL: Column indices must be IDENTICAL to engine/loader.py and sheets/config.py"` -- revealing this is a known coordination problem.

**Consequences:**
- **Silent corruption**: Dashboard shows plausible-looking but completely wrong KPIs
- BOMI client (Orlando) makes decisions based on incorrect compliance percentages
- Trust destruction that is hard to recover from because users won't know when it started

**Warning signs:**
- Sudden shifts in KPI values without operational changes
- Column values containing unexpected data types (numbers where strings expected, or vice versa)
- Users reporting "the numbers don't match what I see in the sheet"

**Prevention:**
1. **Header-based column resolution**: On each data fetch, read the header row first and resolve column indices by matching header names (FECHA, CUMPLIÓ CITA, etc.) rather than hardcoding indices.
2. Add a validation check: if expected headers are missing or in unexpected positions, log an alert and gracefully degrade (show "schema mismatch" warning, not stale data).
3. Store the expected header schema as a configuration constant and compare on every fetch cycle.
4. Document with the ops team: "these column names must not be renamed" (a lightweight contract).

**Phase:** Phase 1 (Data Adapter) -- must be the default parsing strategy, not a hardcoded index approach.

---

### Pitfall 4: Treating Google Sheets as a Real-Time Database

**What goes wrong:** The project spec says "real-time reads from Google Sheets API (no local DB cache for v1)." This leads to building an architecture where every dashboard interaction triggers a Sheets API call. The fundamental problem: Google Sheets is a **collaboration tool**, not a database. It has no query language, no indexing, no transactions, no change notifications (the push notifications API is limited and unreliable). Trying to build real-time dashboards on top of it creates a fragile, slow, unscalable system.

**Why it happens:** The spreadsheet already exists and is the team's workflow. The path of least resistance is to read directly from it. "No local DB cache for v1" is a reasonable MVP constraint, but "no cache at all" is a critical misinterpretation.

**Consequences:**
- Response times of 1-3 seconds per API call (Google Sheets is not optimized for low-latency reads)
- Dashboard feels sluggish, especially for the data table view with filtering
- Cannot do any server-side computation, aggregation, or historical trend analysis efficiently
- No ability to detect "what changed since last check" for operational alerts later

**Warning signs:**
- Dashboard page loads taking >2 seconds consistently
- Users complaining about sluggishness
- Inability to add features like "show me compliance trend over last 7 days" without hitting API limits

**Prevention:**
1. Even for v1, implement an **in-memory cache** (Python dict or simple data class) refreshed by a background task every 30-60 seconds. This is NOT "a database" -- it's a read cache.
2. Design the data layer with a `DataProvider` interface so a future database backend can be swapped in without changing dashboard code.
3. Accept that "real-time" means "near-real-time with 30-60 second freshness" and communicate this clearly in the UI (show "Last updated: 2 min ago").
4. Plan for Phase 2+ to add a lightweight persistence layer (SQLite or PostgreSQL) for historical data and trend analysis.

**Phase:** Phase 1 (Architecture) -- the caching layer must exist from the start. Designing without it means rewriting the data access pattern later.

---

### Pitfall 5: Service Account Permission Scope Creep / Shared Credential Risk

**What goes wrong:** The project reuses the Diageo service account (`diageo-sheets-reader@liftit-ai-products-sign-in-fbc.iam.gserviceaccount.com`). This SA has broad scopes: `spreadsheets`, `drive`, `gmail.readonly`, `gmail.send`. The BOMI dashboard only needs `spreadsheets.readonly`. If the BOMI dashboard code has a vulnerability, an attacker could use these credentials to read/write any spreadsheet the SA has access to, browse Drive files, or send emails via Gmail.

**Why it happens:** Reusing credentials is expedient. Creating a new service account feels like overhead. The Diageo SA "already works."

**Consequences:**
- Security incident in BOMI dashboard exposes Diageo financial data
- Healthcare logistics data (BOMI) potentially exposed through overly broad permissions
- Compliance risk: healthcare supply chain data should have minimal-privilege access
- If the SA gets revoked due to a BOMI issue, the Diageo production system goes down too

**Warning signs:**
- Audit log showing BOMI dashboard accessing non-BOMI resources
- Security review flagging shared credentials across projects
- Any BOMI-related credential leak in logs or error messages

**Prevention:**
1. Create a **dedicated service account** for BOMI with only `spreadsheets.readonly` scope.
2. Share the specific BOMI spreadsheet with this new SA (not a broad Drive permission).
3. Use a separate `GOOGLE_SA_KEY` environment variable (e.g., `BOMI_GOOGLE_SA_KEY`) so credential rotation is independent.
4. If reusing the Diageo SA for v1 (pragmatic choice), document this as tech debt with a deadline to create dedicated credentials before the client-facing view goes live.

**Phase:** Phase 1 (Setup) -- create dedicated credentials before any code touches production. If deferred for MVP speed, must be resolved before Phase 2 (Client-Facing Views).

---

## Moderate Pitfalls

---

### Pitfall 6: Date/Time Parsing Chaos from Spreadsheet Locale

**What goes wrong:** Google Sheets stores dates as serial numbers internally but returns them as formatted strings via the API. The format depends on the spreadsheet's locale setting. A Colombian-locale spreadsheet might return `"31/03/2026"` (dd/mm/yyyy), while the API's `UNFORMATTED_VALUE` mode returns the serial number `46113`. Code using `datetime.strptime(val, "%Y-%m-%d")` fails on the formatted string, and code using the serial number needs conversion logic. HORA DE CARGUE and CITA DE ENTREGA columns compound this: times might come as `"14:30"`, `"2:30 PM"`, `"0.604166..."` (fraction of day), or `"14:30:00"`.

**Why it happens:** Developers test with sample data that happens to be in one format, then the production spreadsheet uses a different locale or the operator enters time in an unexpected format.

**Consequences:**
- Date filters don't work (filtering by "today" misses today's records)
- Time comparisons for appointment compliance (HORA DE LLEGADA vs CITA DE ENTREGA) produce wrong results
- Sorting by date produces nonsensical ordering

**Warning signs:**
- Date filters returning no results for dates that clearly have data
- Compliance calculations showing impossible percentages (>100% or negative)
- Dates appearing as numbers (46113) or in wrong format in the dashboard

**Prevention:**
1. Use `valueRenderOption: UNFORMATTED_VALUE` in the Sheets API call to get raw numbers, then convert consistently.
2. Alternatively, use `FORMATTED_VALUE` but build a robust parser that handles multiple date/time formats (`dateutil.parser.parse` is more forgiving than `strptime`).
3. Write explicit unit tests with date samples in multiple formats: `"31/03/2026"`, `"2026-03-31"`, `"03/31/2026"`, `46113`, `"14:30"`, `"2:30 PM"`.
4. Display "Last updated" timestamps in the UI to make date handling issues visible.

**Phase:** Phase 1 (Data Adapter) -- date parsing must be tested thoroughly before any date-based filtering or compliance calculation.

---

### Pitfall 7: Compliance Metric Miscalculation at Edge Cases

**What goes wrong:** The core KPI is `% CUMPLIÓ CITA = SI`. Seems simple: count SI / total. But edge cases corrupt the metric:
- Rows where CUMPLIÓ CITA is empty (delivery in progress) -- should these be excluded from the denominator?
- Rows where CUMPLIÓ CITA has unexpected values: `"si"`, `"Si"`, `"SÍ"` (with accent), `"S"`, whitespace padding
- Rows for SOS URGENCIA VITAL services where appointment compliance has different expectations
- Filtering by date range: does "today" mean the FECHA column date or the actual delivery date?
- Historical vs. current: the "Actual" tab has ~390 rows but may contain rows from yesterday still being updated

**Why it happens:** The ops team enters data manually with inevitable inconsistencies. The metric definition seems obvious but has undocumented business rules about exclusions, weighting, and time boundaries.

**Consequences:**
- Dashboard shows 85% compliance; Orlando's manual count shows 78%
- Trust in the dashboard evaporates
- Arguments about "what the real number is" instead of acting on operational insights

**Warning signs:**
- Compliance percentage doesn't match manual spot-checks
- Percentage changes dramatically with small data changes
- Stakeholders questioning dashboard numbers

**Prevention:**
1. Normalize CUMPLIÓ CITA values aggressively: `str(val).strip().upper()` and compare against `"SI"` and `"NO"` only. Log unexpected values.
2. Define and document the denominator rule: "In-progress deliveries (empty CUMPLIÓ CITA) are excluded from compliance percentage."
3. Show the breakdown in the UI: "42 SI / 51 total evaluated (8 in progress)" -- not just the percentage.
4. Validate against Orlando's manual calculations during initial deployment. Ask: "Is this number correct?" before going live.
5. Segment compliance by ASIGNACIÓN DE SERVICIO (SOS URGENCIA VITAL vs URGENCIA vs CONSOLIDADO) since these have different expectations.

**Phase:** Phase 2 (KPI/Metrics) -- but the normalization rules should be established in Phase 1 data parsing.

---

### Pitfall 8: Multi-Audience Dashboard Becoming a Franken-Dashboard

**What goes wrong:** Three audiences (operations, management, BOMI client) have different needs. Instead of building focused views, the team creates one dashboard with toggles, tabs, and filters that tries to serve everyone. It becomes cluttered, confusing, and satisfies nobody. The operations team needs real-time granular data; management wants KPI summaries; the BOMI client needs a clean, professional compliance report.

**Why it happens:** "Just add a tab" is faster than designing separate views. Requirements from all three audiences get mixed into a single UI. No one explicitly defines what each audience should NOT see.

**Consequences:**
- Operations team drowns in KPI charts when they need the raw data table
- Management can't find the executive summary amid operational detail
- BOMI client sees internal operational data that should be abstracted
- UI becomes a maintenance nightmare with complex conditional rendering

**Warning signs:**
- Dashboard has >6 navigation items or tabs
- Different stakeholders requesting conflicting layout changes
- "Can you hide X for Y but show it for Z?" requests proliferating

**Prevention:**
1. Design three distinct views from the start with clear purposes:
   - **Operational view**: Data table with filters, real-time status, incidencias list
   - **Executive view**: KPI cards, compliance trends, summary metrics
   - **Client view**: Clean compliance report, service fulfillment summary (no internal details like PLACA or driver info)
2. Each view has its own route (`/ops`, `/executive`, `/client`) and independent layout.
3. Define explicitly what each view does NOT show (e.g., client view never shows vehicle plates or internal observations).
4. Build the operational view first (Phase 1), then executive (Phase 2), then client (Phase 3) -- each as a separate deliverable.

**Phase:** Phase 1 (UI Architecture) -- the routing and view separation must be established early, even if only one view is built initially.

---

### Pitfall 9: No Graceful Degradation When Google Sheets Is Unavailable

**What goes wrong:** Google Sheets API has occasional outages (documented in Google Workspace Status Dashboard). When the API is down, the dashboard shows an error page or empty state. Users have zero visibility into operations during an outage -- which may last 30 minutes to several hours.

**Why it happens:** The dashboard has no fallback data source. If the API call fails, there's nothing to show.

**Consequences:**
- Complete operational blindness during Google outages
- For SOS URGENCIA VITAL deliveries, this could mean life-critical medical supplies not being tracked
- Users lose trust and maintain a parallel manual tracking process, defeating the dashboard's purpose

**Warning signs:**
- `HttpError 503` or connection timeout errors in logs
- Dashboard showing completely empty state
- Users asking "is the dashboard down?" in chat

**Prevention:**
1. Cache the last successful data fetch in memory (or to a local file/SQLite as backup). When API fails, serve stale data with a prominent banner: "Data as of [timestamp] -- Google Sheets temporarily unavailable."
2. Display connection status clearly in the UI (green/yellow/red indicator).
3. Implement a health check endpoint (`/health`) that reports both app health and Google Sheets connectivity.
4. For the background polling loop: on failure, retry with backoff but never clear the cache. The worst case should be stale data, never no data.

**Phase:** Phase 1 (Core Infrastructure) -- graceful degradation is a day-one requirement, not a nice-to-have.

---

### Pitfall 10: Authentication Blocking MVP Delivery

**What goes wrong:** The requirement says "login required to access" but the mechanism is TBD. Teams spend weeks building a full auth system (user registration, password reset, session management, role-based access) before the dashboard can even display data. Or worse, they skip auth entirely for "later" and the client-facing URL leaks internally.

**Why it happens:** Authentication is a bottomless scope hole. It's also a requirement that seems binary: either you have it or you don't.

**Consequences:**
- MVP delivery delays by 1-3 weeks for auth implementation
- Or: dashboard deployed without auth, creating security/privacy exposure for healthcare logistics data
- Over-engineered RBAC when a simple shared password or basic auth would suffice for v1

**Warning signs:**
- Auth implementation taking more than 2 days
- Discussions about user roles, permissions matrices, OAuth providers for a 3-audience dashboard
- Dashboard data accessible without any authentication

**Prevention:**
1. For v1, use the simplest viable auth: environment-variable-based shared credentials with FastAPI's built-in HTTP Basic Auth or a simple session cookie with a hardcoded password. Three passwords: one for ops, one for management, one for BOMI client.
2. This takes <1 day to implement and gates access immediately.
3. Plan proper auth (individual accounts, SSO) for a later phase only if user management becomes a real need.
4. Never deploy without at least basic auth -- healthcare logistics data has privacy expectations.

**Phase:** Phase 1 (Authentication) -- implement simple auth early, upgrade later. Do not let this block core dashboard delivery.

---

## Minor Pitfalls

---

### Pitfall 11: Frontend Polling Creating Unnecessary API Load

**What goes wrong:** The frontend JavaScript polls the FastAPI backend every 5 seconds for updates. With 10 browser tabs open (common for operations teams), that's 120 requests/minute to the backend. Each backend request triggers a Sheets API call (if not cached), amplifying the load.

**Prevention:**
1. Frontend should poll the backend at 30-60 second intervals, matching the backend's cache refresh cycle.
2. Display a "Last refreshed" timestamp so users understand the data freshness.
3. Consider Server-Sent Events (SSE) for push-based updates instead of polling -- FastAPI supports this natively with `StreamingResponse`.
4. Never let frontend poll interval be shorter than backend cache refresh interval.

**Phase:** Phase 1 (Frontend) -- set appropriate polling intervals from the start.

---

### Pitfall 12: Ignoring the "historico" Tab and TIPOLOGIAS Catalog

**What goes wrong:** The spreadsheet has three tabs: "Actual", "TIPOLOGIAS", and "historico". The dashboard focuses only on "Actual" and ignores the catalog and historical data. Later, when users want trend analysis or service type breakdowns, the data model doesn't account for these relationships.

**Prevention:**
1. Read TIPOLOGIAS during startup as a reference/lookup table for service type categorization.
2. Design the data model to accept historical data, even if the historico tab isn't parsed in v1.
3. Don't hardcode service type labels -- pull them from TIPOLOGIAS so new types are automatically supported.

**Phase:** Phase 1 (Data Model) -- read TIPOLOGIAS as a reference. Phase 3+ for historico integration.

---

### Pitfall 13: Deploying on Render Free Tier with Sleep Behavior

**What goes wrong:** Render's free tier spins down services after 15 minutes of inactivity. The first request after spin-down takes 30-60 seconds to cold start (Python + pip install). For a "real-time" dashboard used throughout the workday, this creates a terrible experience every morning and after lunch breaks.

**Prevention:**
1. Use Render's paid tier (Starter at $7/month) for always-on behavior, or implement a keep-alive ping.
2. If using free tier, implement a lightweight `/ping` endpoint and set up an external uptime monitor (UptimeRobot, free tier) to hit it every 10 minutes.
3. Optimize Docker image / start time: use a slim base image, pre-install dependencies.

**Phase:** Phase 1 (Deployment) -- decide on tier before deploying. The cold start problem is immediately visible to users.

---

### Pitfall 14: Not Handling Spanish Text Encoding Correctly

**What goes wrong:** Column values contain Spanish characters with accents and special characters: URGENCIA, CUMPLIÓ, ASIGNACIÓN, city names like BOGOTÁ, MEDELLÍN. If encoding is not handled properly, string comparisons fail (`"CUMPLIÓ" != "CUMPLIO"`), filters miss records, and the UI displays garbled text.

**Prevention:**
1. Google Sheets API returns UTF-8 -- ensure all string processing preserves UTF-8 encoding.
2. For string comparisons, use Unicode normalization: `unicodedata.normalize("NFC", val)` before comparing.
3. Consider accent-insensitive matching for filters: normalize to ASCII for comparison but display original text.
4. Test explicitly with accented characters in both data parsing and UI rendering.

**Phase:** Phase 1 (Data Adapter) -- handle encoding from the first data read.

---

### Pitfall 15: Building Analytics Before Validating Data Quality

**What goes wrong:** The dashboard builds sophisticated KPI charts and trend analysis, but the underlying data has quality issues: duplicate rows, inconsistent date formats, empty required fields, typos in TIPO DE OPERACIÓN values ("DEDCADO" vs "DEDICADO"). The analytics look professional but produce misleading results.

**Prevention:**
1. Before building any analytics view, run a data quality audit: count nulls per column, unique values for categorical columns, date range validation.
2. Add a "Data Quality" section to the operational view showing: rows with missing dates, unrecognized service types, compliance fields with unexpected values.
3. Feed data quality findings back to the ops team so they can improve data entry practices.
4. Normalize categorical values at parse time (strip whitespace, uppercase, map known typos).

**Phase:** Phase 1 (Data Adapter) for normalization. Phase 2 for data quality visibility.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Data Adapter (Phase 1) | Sparse rows crashing parser (Pitfall 2) | Use safe cell accessor pattern from Diageo project |
| Data Adapter (Phase 1) | Column index drift (Pitfall 3) | Header-based column resolution, not hardcoded indices |
| Data Adapter (Phase 1) | Date/time format inconsistency (Pitfall 6) | Use `UNFORMATTED_VALUE` or robust multi-format parser |
| Core Infrastructure (Phase 1) | API rate limit exhaustion (Pitfall 1) | Server-side cache with single background polling loop |
| Core Infrastructure (Phase 1) | No degradation on API outage (Pitfall 9) | Serve stale cached data with freshness banner |
| Authentication (Phase 1) | Auth scope creep delaying MVP (Pitfall 10) | Simple HTTP Basic Auth, upgrade later |
| KPI/Metrics (Phase 2) | Compliance miscalculation (Pitfall 7) | Normalize SI/NO, define denominator rules, validate with Orlando |
| UI Architecture (Phase 1-2) | Franken-dashboard (Pitfall 8) | Three separate views with distinct routes from day one |
| Deployment (Phase 1) | Render cold starts (Pitfall 13) | Use paid tier or uptime monitor keep-alive |
| Credentials (Phase 1) | Shared SA risk (Pitfall 5) | Dedicated SA with readonly scope for BOMI |

## Sources

- **Diageo reference project** (`/Users/fbetncourtc/Documents/finops/proceso-tarificacion-diageo/sheets/`): Production-proven patterns for `_get_cell()` safe accessor, column mapping, currency parsing, sparse row handling. HIGH confidence -- this is real code handling real edge cases.
- **Google Sheets API v4 quotas**: 300 read requests/min/project, 60 read requests/min/user/project (documented at developers.google.com/sheets/api/limits). MEDIUM confidence -- based on training data, quota numbers should be verified against current documentation.
- **Google Sheets API data format behavior**: Sparse row truncation, `valueRenderOption` modes (`FORMATTED_VALUE`, `UNFORMATTED_VALUE`, `FORMULA`). HIGH confidence -- well-documented API behavior confirmed by Diageo project patterns.
- **Render deployment behavior**: Free tier sleep after inactivity, cold start times. MEDIUM confidence -- based on known Render behavior, verify current tier pricing.
