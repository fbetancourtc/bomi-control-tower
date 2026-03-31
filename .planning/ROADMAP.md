# Roadmap: BOMI Control Tower

## Overview

Build a local-running logistics Control Tower dashboard that reads delivery data from the BOMI Google Spreadsheet and provides real-time visibility into appointment compliance. The journey starts with connecting to the data source (reusing proven Diageo code), then builds the dashboard layer-by-layer: live status counters, filterable data table, compliance KPIs, incidencias reporting, and finally assembles these into three purpose-built views for dispatchers, management, and the BOMI client.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Project Scaffold & Google Sheets Connection** - FastAPI project structure with proven Sheets auth/reading from Diageo
- [ ] **Phase 2: Data Model & Caching Layer** - In-memory cache with background polling and header-based column mapping
- [ ] **Phase 3: API Endpoints & Data Serving** - FastAPI routes that serve spreadsheet data as JSON for dashboard consumption
- [ ] **Phase 4: Live Status Dashboard** - Real-time counters showing today's delivery status at a glance
- [ ] **Phase 5: Filterable Data Table** - Full data table with combined filters for precise querying
- [ ] **Phase 6: Compliance Metrics & KPIs** - Appointment compliance percentages with breakdowns by operation type, service, and location
- [ ] **Phase 7: Compliance Trends** - Historical compliance trend using historico data
- [ ] **Phase 8: Incidencias Report** - Dedicated missed-appointment view with filtering
- [ ] **Phase 9: Operational View** - Dispatcher-focused view combining live status + data table
- [ ] **Phase 10: Executive View** - Management-focused view with KPI charts and compliance trends
- [ ] **Phase 11: Client View** - BOMI-facing compliance report for Orlando with incidencias

## Phase Details

### Phase 1: Project Scaffold & Google Sheets Connection
**Goal**: A running FastAPI application that successfully authenticates with Google Sheets API and reads raw data from the BOMI spreadsheet
**Depends on**: Nothing (first phase)
**Requirements**: SHEET-01, SHEET-02, SHEET-03, SHEET-04
**Success Criteria** (what must be TRUE):
  1. FastAPI server starts locally and responds to a health-check request
  2. Application authenticates with Google Sheets API using the existing Service Account credentials
  3. Application reads and returns raw row data from the "Actual" tab
  4. Application reads and returns raw row data from "TIPOLOGIAS" and "historico" tabs
**Plans**: TBD

Plans:
- [ ] 01-01: TBD
- [ ] 01-02: TBD

### Phase 2: Data Model & Caching Layer
**Goal**: Spreadsheet data is parsed into structured models, cached in memory, and refreshed automatically via background polling
**Depends on**: Phase 1
**Requirements**: SHEET-05, SHEET-06, SHEET-07
**Success Criteria** (what must be TRUE):
  1. Columns are resolved by header name, not hardcoded index -- renaming a column header in the spreadsheet does not break the application
  2. Data refreshes automatically every 30-60 seconds without user action
  3. Application continues serving cached data when Google Sheets API returns a rate-limit error instead of crashing
**Plans**: TBD

Plans:
- [ ] 02-01: TBD
- [ ] 02-02: TBD

### Phase 3: API Endpoints & Data Serving
**Goal**: FastAPI routes expose structured delivery data as JSON, ready for frontend consumption
**Depends on**: Phase 2
**Requirements**: (infrastructure -- supports LIVE, TABLE, KPI, INC requirements)
**Success Criteria** (what must be TRUE):
  1. An API endpoint returns today's services from cached data as structured JSON
  2. An API endpoint returns historical data from the "historico" tab as structured JSON
  3. API responses include all 15 columns with correct field names
**Plans**: TBD

Plans:
- [ ] 03-01: TBD

### Phase 4: Live Status Dashboard
**Goal**: Users see at-a-glance delivery status counters that update automatically
**Depends on**: Phase 3
**Requirements**: LIVE-01, LIVE-02, LIVE-03, LIVE-04, LIVE-05, LIVE-06
**Success Criteria** (what must be TRUE):
  1. User sees a card/counter showing total services for today
  2. User sees separate counters for delivered, appointment met (SI), appointment missed (NO), and pending services
  3. Counters update automatically without the user refreshing the page
**Plans**: TBD
**UI hint**: yes

Plans:
- [ ] 04-01: TBD
- [ ] 04-02: TBD

### Phase 5: Filterable Data Table
**Goal**: Users can explore all service data in a table and narrow results using combined filters
**Depends on**: Phase 3
**Requirements**: TABLE-01, TABLE-02, TABLE-03, TABLE-04, TABLE-05, TABLE-06, TABLE-07, TABLE-08
**Success Criteria** (what must be TRUE):
  1. User sees all services displayed in a data table showing all 15 columns
  2. User can filter by date, tipo de operacion, punto de cargue, placa, asignacion de servicio, and cumplido cita
  3. Multiple filters combine with AND logic -- applying two filters narrows results to only rows matching both
  4. Filter options are populated from actual data values (not hardcoded lists)
**Plans**: TBD
**UI hint**: yes

Plans:
- [ ] 05-01: TBD
- [ ] 05-02: TBD

### Phase 6: Compliance Metrics & KPIs
**Goal**: Users see appointment compliance percentages broken down by operation type, service assignment, and loading point
**Depends on**: Phase 3
**Requirements**: KPI-01, KPI-02, KPI-03, KPI-04
**Success Criteria** (what must be TRUE):
  1. User sees the overall compliance percentage (CUMPLIO CITA = SI / total completed)
  2. User sees compliance broken down by tipo de operacion (DEDICADO, CONSOLIDADO, etc.)
  3. User sees compliance broken down by asignacion de servicio and by punto de cargue
**Plans**: TBD
**UI hint**: yes

Plans:
- [ ] 06-01: TBD
- [ ] 06-02: TBD

### Phase 7: Compliance Trends
**Goal**: Users see how appointment compliance has changed over time using historical data
**Depends on**: Phase 6
**Requirements**: KPI-05
**Success Criteria** (what must be TRUE):
  1. User sees a chart showing compliance percentage over time (daily or weekly)
  2. Trend data is sourced from the "historico" tab, not just today's data
**Plans**: TBD
**UI hint**: yes

Plans:
- [ ] 07-01: TBD

### Phase 8: Incidencias Report
**Goal**: Users can quickly see and filter all deliveries that missed their appointment
**Depends on**: Phase 3
**Requirements**: INC-01, INC-02, INC-03, INC-04
**Success Criteria** (what must be TRUE):
  1. User sees a dedicated list showing only services where CUMPLIO CITA = NO
  2. Each incidencia displays fecha, punto cargue, tipo operacion, placa, punto entrega, cita entrega, and observaciones
  3. User can filter incidencias by date range and by tipo de operacion
**Plans**: TBD
**UI hint**: yes

Plans:
- [ ] 08-01: TBD
- [ ] 08-02: TBD

### Phase 9: Operational View
**Goal**: Dispatchers and coordinators have a single view optimized for their daily workflow
**Depends on**: Phase 4, Phase 5
**Requirements**: VIEW-01
**Success Criteria** (what must be TRUE):
  1. User can access an operational view that combines live status counters and the filterable data table on one screen
  2. The view is designed for quick scanning -- status counters are prominent at the top, table fills the remaining space
**Plans**: TBD
**UI hint**: yes

Plans:
- [ ] 09-01: TBD

### Phase 10: Executive View
**Goal**: Management sees a KPI-focused dashboard with charts and compliance trends for strategic decisions
**Depends on**: Phase 6, Phase 7
**Requirements**: VIEW-02
**Success Criteria** (what must be TRUE):
  1. User can access an executive view showing KPI charts and compliance breakdown visualizations
  2. The view includes the compliance trend chart showing performance over time
  3. Summary metrics (total services, overall compliance %, incidencia count) are visible at the top
**Plans**: TBD
**UI hint**: yes

Plans:
- [ ] 10-01: TBD

### Phase 11: Client View
**Goal**: Orlando (BOMI Supply Chain Manager) has a compliance report view with incidencias detail
**Depends on**: Phase 6, Phase 8
**Requirements**: VIEW-03
**Success Criteria** (what must be TRUE):
  1. User can access a client view showing compliance metrics and the incidencias list together
  2. The view is presentation-ready -- suitable for sharing in a meeting with BOMI stakeholders
  3. Compliance data and incidencia details are clearly separated and easy to read
**Plans**: TBD
**UI hint**: yes

Plans:
- [ ] 11-01: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11
Note: Phases 4, 5, 6, 8 can run in parallel after Phase 3. Phases 9, 10, 11 assemble earlier components.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Project Scaffold & Google Sheets Connection | 0/2 | Not started | - |
| 2. Data Model & Caching Layer | 0/2 | Not started | - |
| 3. API Endpoints & Data Serving | 0/1 | Not started | - |
| 4. Live Status Dashboard | 0/2 | Not started | - |
| 5. Filterable Data Table | 0/2 | Not started | - |
| 6. Compliance Metrics & KPIs | 0/2 | Not started | - |
| 7. Compliance Trends | 0/1 | Not started | - |
| 8. Incidencias Report | 0/2 | Not started | - |
| 9. Operational View | 0/1 | Not started | - |
| 10. Executive View | 0/1 | Not started | - |
| 11. Client View | 0/1 | Not started | - |
