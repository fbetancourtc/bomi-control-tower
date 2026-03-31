# Requirements: BOMI Control Tower

**Defined:** 2026-03-31
**Core Value:** Real-time visibility into whether deliveries are meeting their scheduled appointments

## v1 Requirements

### Google Sheets Integration

- [x] **SHEET-01**: System connects to Google Spreadsheet using existing Service Account credentials
- [x] **SHEET-02**: System reads all rows from "Actual" tab (current operations, ~390 rows, 15 columns)
- [x] **SHEET-03**: System reads "TIPOLOGIAS" tab to resolve service type definitions
- [x] **SHEET-04**: System reads "historico" tab for historical delivery data with driver info
- [x] **SHEET-05**: System uses header-based column resolution (not hardcoded indices) to handle column changes
- [x] **SHEET-06**: System caches spreadsheet data in memory with background polling every 30-60 seconds
- [ ] **SHEET-07**: System handles Google Sheets API rate limits gracefully (no crashes on quota exhaustion) — PARTIAL: errors caught but no quota-specific retry/backoff

### Dashboard — Live Status

- [x] **LIVE-01**: User sees count of total services for today
- [x] **LIVE-02**: User sees count of services delivered (CUMPLIO CITA populated)
- [x] **LIVE-03**: User sees count of services with appointment met (CUMPLIO CITA = SI)
- [x] **LIVE-04**: User sees count of services with appointment missed (CUMPLIO CITA = NO)
- [x] **LIVE-05**: User sees count of services pending (no CUMPLIO CITA value yet)
- [x] **LIVE-06**: Dashboard auto-refreshes data without manual page reload

### Dashboard — Filterable Table

- [ ] **TABLE-01**: User sees all services in a data table with all 15 columns — PARTIAL: 12/15 displayed (missing: Cliente, Hora Salida, Llegada Lead Time)
- [x] **TABLE-02**: User can filter by date (FECHA)
- [x] **TABLE-03**: User can filter by tipo de operacion (DEDICADO, CONSOLIDADO, MEDTRONIC, ROCHE PHARMA, etc.)
- [x] **TABLE-04**: User can filter by punto de cargue
- [x] **TABLE-05**: User can filter by placa (vehicle plate)
- [x] **TABLE-06**: User can filter by asignacion de servicio (SOS URGENCIA VITAL, URGENCIA, CONSOLIDADO)
- [x] **TABLE-07**: User can filter by cumplio cita (SI/NO/pending)
- [x] **TABLE-08**: Filters combine (AND logic) for precise querying

### Dashboard — Compliance Metrics

- [x] **KPI-01**: User sees overall appointment compliance percentage (CUMPLIO CITA = SI / total completed)
- [x] **KPI-02**: User sees compliance breakdown by tipo de operacion
- [x] **KPI-03**: User sees compliance breakdown by asignacion de servicio
- [x] **KPI-04**: User sees compliance breakdown by punto de cargue
- [ ] **KPI-05**: User sees compliance trend over time (using historico data) — MISSING: historico read but not used for trend chart

### Dashboard — Incidencias Report

- [x] **INC-01**: User sees a dedicated list of all services where CUMPLIO CITA = NO
- [x] **INC-02**: Each incidencia shows: fecha, punto cargue, tipo operacion, placa, punto entrega, cita entrega, observaciones
- [ ] **INC-03**: User can filter incidencias by date range — MISSING: no date range filter on incidencias
- [ ] **INC-04**: User can filter incidencias by tipo de operacion — PARTIAL: works in operational view via general filters, missing in client view

### Views

- [x] **VIEW-01**: Operational view — data table + live status counters for dispatchers/coordinators
- [x] **VIEW-02**: Executive view — KPI charts + compliance trends + summary metrics for management
- [x] **VIEW-03**: Client view — compliance report for Orlando (BOMI Supply Chain Manager) with incidencias

## v2 Requirements

### Authentication

- **AUTH-01**: User must log in with username/password to access the dashboard
- **AUTH-02**: Different users see different views based on their role (ops/executive/client)

### Alerts

- **ALERT-01**: System highlights services at risk of missing their appointment
- **ALERT-02**: Email/notification when a service misses its appointment

### Export

- **EXPORT-01**: User can export filtered data to CSV/Excel
- **EXPORT-02**: User can generate PDF report of incidencias

### Deployment

- **DEPLOY-01**: Application deployed to Render with GOOGLE_SA_KEY base64 pattern
- **DEPLOY-02**: Application accessible via public URL with authentication

## Out of Scope

| Feature | Reason |
|---------|--------|
| Write-back to spreadsheet | Spreadsheet is source of truth, managed by ops team directly |
| GPS/real-time vehicle tracking | Not available in data source, high complexity |
| Route optimization | Different product category entirely |
| Mobile native app | Web responsive design covers mobile use cases |
| ML/predictive analytics | Overengineered for current needs |
| Integration with TMS/ERP | No current need, adds complexity |
| Database storage | ~390 rows fits in memory, no DB needed for v1 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SHEET-01 | Phase 1 | Complete |
| SHEET-02 | Phase 1 | Complete |
| SHEET-03 | Phase 1 | Complete |
| SHEET-04 | Phase 1 | Complete |
| SHEET-05 | Phase 2 | Complete |
| SHEET-06 | Phase 2 | Complete |
| SHEET-07 | Phase 2 | Partial |
| LIVE-01 | Phase 4 | Complete |
| LIVE-02 | Phase 4 | Complete |
| LIVE-03 | Phase 4 | Complete |
| LIVE-04 | Phase 4 | Complete |
| LIVE-05 | Phase 4 | Complete |
| LIVE-06 | Phase 4 | Complete |
| TABLE-01 | Phase 5 | Partial |
| TABLE-02 | Phase 5 | Complete |
| TABLE-03 | Phase 5 | Complete |
| TABLE-04 | Phase 5 | Complete |
| TABLE-05 | Phase 5 | Complete |
| TABLE-06 | Phase 5 | Complete |
| TABLE-07 | Phase 5 | Complete |
| TABLE-08 | Phase 5 | Complete |
| KPI-01 | Phase 6 | Complete |
| KPI-02 | Phase 6 | Complete |
| KPI-03 | Phase 6 | Complete |
| KPI-04 | Phase 6 | Complete |
| KPI-05 | Phase 7 | Pending |
| INC-01 | Phase 8 | Complete |
| INC-02 | Phase 8 | Complete |
| INC-03 | Phase 8 | Pending |
| INC-04 | Phase 8 | Partial |
| VIEW-01 | Phase 9 | Complete |
| VIEW-02 | Phase 10 | Complete |
| VIEW-03 | Phase 11 | Complete |

**Coverage:**
- v1 requirements: 33 total
- Complete: 27
- Partial: 3 (SHEET-07, TABLE-01, INC-04)
- Pending: 3 (KPI-05, INC-03, INC-04)

---
*Requirements defined: 2026-03-31*
*Last updated: 2026-03-31 after code audit reconciliation*
