# BOMI Control Tower

## What This Is

A web-based Control Tower dashboard that reads delivery/appointment data from a Google Spreadsheet ("CONTROL CITAS BOMI") and provides real-time visibility into BOMI's logistics operations. Tracks service fulfillment, appointment compliance, and incidencias for the operations team, management, and BOMI's Supply Chain Manager (Orlando).

## Core Value

Real-time visibility into whether deliveries are meeting their scheduled appointments — so operations can act before problems compound.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Connect to Google Spreadsheet and read delivery data in real-time
- [ ] Dashboard with live status: services in route, delivered, delayed
- [ ] Appointment compliance metrics (% CUMPLIÓ CITA = SI) with trends
- [ ] Filterable data table (by date, tipo de operación, punto de cargue, placa, asignación de servicio)
- [ ] Incidencias report: all services where CUMPLIÓ CITA = NO
- [ ] Multiple views: operational (day-to-day), executive (KPIs), client-facing
- [ ] Authentication — login required to access

### Out of Scope

- Mobile native app — web-first, responsive design instead
- Writing back to the spreadsheet — read-only consumption
- Email/push notifications for alerts — focus on dashboard first (per user direction)
- Integration with external TMS/ERP systems

## Context

- **Data source**: Google Spreadsheet `1nlwPV97FE3zouKL519lBGJJExuZkWZCehzflxw_xaNo` ("CONTROL CITAS BOMI")
- **3 tabs**: "Actual" (current operations, ~390 rows, 15 columns), "TIPOLOGIAS" (service type catalog), "historico" (historical data with driver info)
- **Key columns**: FECHA, HORA DE CARGUE, PUNTO CARGUE, CLIENTE, TIPO DE OPERACIÓN (DEDICADO/CONSOLIDADO/MEDTRONIC/ROCHE PHARMA), PLACA, ASIGNACIÓN DE SERVICIO (SOS URGENCIA VITAL/URGENCIA/CONSOLIDADO), PUNTO DE ENTREGA, CITA DE ENTREGA, HORA DE LLEGADA, CUMPLIÓ CITA (SI/NO), OBSERVACIONES
- **Spreadsheet updated in real-time** throughout the day by operations team
- **Google integration reused** from proyecto proceso-tarificacion-diageo (`/Users/fbetncourtc/Documents/finops/proceso-tarificacion-diageo/`)
  - `sheets/auth.py` — Service Account authentication (GOOGLE_SA_KEY or GOOGLE_SERVICE_ACCOUNT_FILE)
  - `sheets/reader.py` — Sheets API v4 reading pattern
  - Service Account: `diageo-sheets-reader@liftit-ai-products-sign-in-fbc.iam.gserviceaccount.com`
- **Users**: Operations team (dispatchers), management/directors, BOMI client (Orlando — Supply Chain Manager)
- **Current focus**: Build the dashboard first; alerts and advanced features deferred

## Constraints

- **Tech stack**: Python + FastAPI + HTML/JS dashboard (same as Diageo tarificación project)
- **Deployment**: Render (same infra as Diageo, GOOGLE_SA_KEY base64 pattern)
- **Authentication**: Login required (specific mechanism TBD)
- **Google credentials**: Reuse existing Service Account from proceso-tarificacion-diageo
- **Data freshness**: Real-time reads from Google Sheets API (no local DB cache for v1)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Reuse Service Account from Diageo project | Same GCP project, already has spreadsheets+drive scopes, avoid credential management overhead | — Pending |
| Python + FastAPI stack | Match existing Diageo project for code reuse (auth, adapters) and team familiarity | — Pending |
| Read-only dashboard (no write-back) | Spreadsheet is source of truth, managed by ops team directly | — Pending |
| Dashboard-first approach | User directed focus on dashboard before alerts/notifications | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-31 after initialization*
