# Research Summary: BOMI Control Tower

**Domain:** Real-time logistics dashboard (delivery appointment tracking)
**Researched:** 2026-03-31
**Overall confidence:** MEDIUM

## Executive Summary

The BOMI Control Tower is a read-only logistics dashboard that reads delivery appointment data from a Google Spreadsheet and displays real-time KPIs, filterable tables, and compliance metrics for an operations team of 3-5 users. The architecture is deliberately simple: Python + FastAPI serves server-rendered HTML with HTMX for partial page updates, reading directly from Google Sheets API with no intermediate database.

The most important stack decision is choosing HTMX over a JavaScript SPA framework. This project is fundamentally a data display tool -- it reads from a spreadsheet, computes metrics, and renders tables and charts. There is no complex client-side state, no drag-and-drop, no collaborative editing. HTMX with server-side Jinja2 templating eliminates the need for a Node.js build pipeline, API serialization, and frontend state management. The entire application stays in Python, which matches the team's existing skillset and the Diageo project's proven patterns.

The Google Sheets integration is the strongest piece of this stack. The existing Diageo project has battle-tested code for Service Account authentication (with base64 key for Render deployment), Sheets API v4 reading patterns, and error handling. This code can be copied and adapted with minimal changes -- the main work is mapping BOMI's 15 column structure instead of Diageo's.

Authentication is the one genuinely new piece. The Diageo project has no auth. For 3-5 internal users, the recommendation is cookie-based JWT sessions with hardcoded bcrypt-hashed passwords stored in environment variables. This avoids the overhead of a database, OAuth provider, or user management UI.

## Key Findings

**Stack:** Python 3.11 + FastAPI + Jinja2 + HTMX + Chart.js. No database, no JS build step, no SPA framework. Google Sheets auth reused from Diageo.

**Architecture:** Monolithic FastAPI app with three view layers (operational, executive, client-facing), a Google Sheets reader service, and cookie-based JWT authentication middleware.

**Critical pitfall:** Google Sheets API rate limits (60 reads/minute/user). If >10 concurrent users hit the dashboard simultaneously with 30-second polling, you will exhaust the quota. Mitigate with server-side caching from the start.

## Implications for Roadmap

Based on research, suggested phase structure:

1. **Foundation & Auth** - Set up FastAPI project structure, copy/adapt Diageo's Sheets auth, implement login system
   - Addresses: Authentication, Google Sheets connection
   - Avoids: Building on an unproven foundation; validates Sheets connectivity early

2. **Core Dashboard (Operational View)** - Filterable data table with live status, the primary view dispatchers need daily
   - Addresses: Live status table, filters (date, tipo operacion, placa, etc.)
   - Avoids: Over-engineering multiple views before one works well

3. **Metrics & Compliance** - Appointment compliance KPIs, incidencias report, trends
   - Addresses: % CUMPLIO CITA metrics, incidencias where CUMPLIO CITA = NO
   - Avoids: Premature optimization; metrics layer builds on proven data reading

4. **Executive & Client Views** - KPI dashboards with charts, client-facing view for Orlando
   - Addresses: Multiple views (operational, executive, client-facing)
   - Avoids: Scope creep; the operational view must work first

5. **Deployment & Polish** - Render deployment, responsive design, performance tuning
   - Addresses: Production deployment, mobile responsiveness
   - Avoids: Deploying before core functionality is validated

**Phase ordering rationale:**
- Auth first because every endpoint depends on it and it cannot be retrofitted easily
- Operational view before executive/client views because it validates the data model and Sheets reading patterns
- Metrics after the data table because metrics are computed from the same data -- once reading works, aggregation is straightforward
- Deployment last because Render deployment is a proven pattern from Diageo (low risk, mechanical work)

**Research flags for phases:**
- Phase 1: May need deeper research on HTMX SSE vs polling tradeoffs (depends on desired data freshness)
- Phase 3: Standard aggregation patterns, unlikely to need research
- Phase 5: Render deployment is well-documented from Diageo, no research needed

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Core technologies proven via Diageo project. Version numbers are conservative minimums from training data (May 2025), not verified against live PyPI. |
| Features | HIGH | Requirements clearly defined in PROJECT.md. Feature landscape is well-understood for logistics dashboards. |
| Architecture | HIGH | Simple monolithic pattern. No novel architectural decisions. Follows established FastAPI + Jinja2 patterns from Diageo. |
| Pitfalls | HIGH | Google Sheets API rate limits, auth patterns, and deployment gotchas are well-documented concerns. |

## Gaps to Address

- Exact latest versions of FastAPI, HTMX, Chart.js should be verified at project setup time (`pip install --upgrade`)
- Google Sheets API rate limit specifics should be verified against current quota documentation (the 60 req/min figure is from training data)
- Whether HTMX SSE or simple polling is better for the target user count (3-10 users) -- recommend starting with polling and adding SSE only if needed
- Specific BOMI spreadsheet column mapping (15 columns documented in PROJECT.md) needs validation against actual sheet structure during Phase 1

---
*Research summary for: BOMI Control Tower*
*Researched: 2026-03-31*
