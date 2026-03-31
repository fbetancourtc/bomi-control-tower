# Phase 1: Project Scaffold & Google Sheets Connection - Context

**Gathered:** 2026-03-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Set up a running FastAPI application that authenticates with Google Sheets API using the existing Service Account and reads raw data from the BOMI spreadsheet's 3 tabs (Actual, TIPOLOGIAS, historico). This is the foundation — all other phases depend on this working.

</domain>

<decisions>
## Implementation Decisions

### Credential Strategy
- **D-01:** Copy the Service Account JSON key file into this project at `secrets/service-account.json`
- **D-02:** Add `secrets/` to `.gitignore` — key file never committed to git
- **D-03:** Support both `GOOGLE_SERVICE_ACCOUNT_FILE` (local dev) and `GOOGLE_SA_KEY` (base64, cloud deployment)
- **D-04:** No longer depend on the Diageo project path for credentials

### Project Structure
- **D-05:** Use FastAPI standard layout: `routers/`, `services/`, `models/`, `templates/`
- **D-06:** Refactor current flat layout (app.py + sheets/) into this structure

### Env Configuration
- **D-07:** Add `LOG_LEVEL` env var to control logging verbosity (dev vs prod)
- **D-08:** Keep existing vars: `GOOGLE_SERVICE_ACCOUNT_FILE`, `BOMI_SHEET_ID`, `POLL_INTERVAL_SECONDS`

### Error Handling
- **D-09:** On startup: if Google Sheets API fails, crash and exit with descriptive error. Do not start the server without data.
- **D-10:** On runtime polling failure: serve stale (last-good) data silently, retry on next polling cycle. No visual warning banner.

### Claude's Discretion
- Config management approach (pydantic Settings vs plain dotenv) — Claude picks best practice for FastAPI

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Google Sheets Integration (source patterns)
- `/Users/fbetncourtc/Documents/finops/proceso-tarificacion-diageo/sheets/auth.py` — Service Account auth pattern to adapt
- `/Users/fbetncourtc/Documents/finops/proceso-tarificacion-diageo/sheets/reader.py` — Sheets API v4 reading pattern

### Project Configuration
- `.env` — Current env var configuration
- `.planning/PROJECT.md` — Project context and constraints
- `.planning/REQUIREMENTS.md` — SHEET-01 through SHEET-04 requirements for this phase

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `sheets/auth.py` — SA auth already working, supports both file and base64 methods
- `sheets/reader.py` — Header-based column resolution, reads all 3 tabs, dataclass models defined
- `app.py` — FastAPI lifespan pattern, background polling, route structure

### Established Patterns
- Google Sheets API v4 via `googleapiclient.discovery.build()`
- `_read_tab()` helper for safe tab reading with HttpError handling
- `_resolve_columns()` for header-based column mapping (40+ header variations handled)
- `_get_cell()` for sparse row safety
- Async background polling via `asyncio.to_thread()` + `asyncio.create_task()`

### Integration Points
- `.env` file loaded via `python-dotenv` at app startup
- Google SA credentials file at `secrets/service-account.json` (to be created)
- Sheet ID: `1nlwPV97FE3zouKL519lBGJJExuZkWZCehzflxw_xaNo`

</code_context>

<specifics>
## Specific Ideas

- Reuse auth pattern from Diageo project (proven in production on Render)
- Service Account email: `diageo-sheets-reader@liftit-ai-products-sign-in-fbc.iam.gserviceaccount.com`
- Spreadsheet already shared with the SA — connectivity verified in this session

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-project-scaffold-google-sheets-connection*
*Context gathered: 2026-03-31*
