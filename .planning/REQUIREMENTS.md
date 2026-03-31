# Requirements: BOMI Control Tower

**Defined:** 2026-03-31
**Core Value:** Real-time visibility into whether deliveries are meeting their scheduled appointments

## v1 Requirements

### Google Sheets Integration

- [ ] **SHEET-01**: System connects to Google Spreadsheet using existing Service Account credentials
- [ ] **SHEET-02**: System reads all rows from "Actual" tab (current operations, ~390 rows, 15 columns)
- [ ] **SHEET-03**: System reads "TIPOLOGIAS" tab to resolve service type definitions
- [ ] **SHEET-04**: System reads "historico" tab for historical delivery data with driver info
- [ ] **SHEET-05**: System uses header-based column resolution (not hardcoded indices) to handle column changes
- [ ] **SHEET-06**: System caches spreadsheet data in memory with background polling every 30-60 seconds
- [ ] **SHEET-07**: System handles Google Sheets API rate limits gracefully (no crashes on quota exhaustion)

### Dashboard — Live Status

- [ ] **LIVE-01**: User sees count of total services for today
- [ ] **LIVE-02**: User sees count of services delivered (CUMPLIO CITA populated)
- [ ] **LIVE-03**: User sees count of services with appointment met (CUMPLIO CITA = SI)
- [ ] **LIVE-04**: User sees count of services with appointment missed (CUMPLIO CITA = NO)
- [ ] **LIVE-05**: User sees count of services pending (no CUMPLIO CITA value yet)
- [ ] **LIVE-06**: Dashboard auto-refreshes data without manual page reload

### Dashboard — Filterable Table

- [ ] **TABLE-01**: User sees all services in a data table with all 15 columns
- [ ] **TABLE-02**: User can filter by date (FECHA)
- [ ] **TABLE-03**: User can filter by tipo de operacion (DEDICADO, CONSOLIDADO, MEDTRONIC, ROCHE PHARMA, etc.)
- [ ] **TABLE-04**: User can filter by punto de cargue
- [ ] **TABLE-05**: User can filter by placa (vehicle plate)
- [ ] **TABLE-06**: User can filter by asignacion de servicio (SOS URGENCIA VITAL, URGENCIA, CONSOLIDADO)
- [ ] **TABLE-07**: User can filter by cumplio cita (SI/NO/pending)
- [ ] **TABLE-08**: Filters combine (AND logic) for precise querying

### Dashboard — Compliance Metrics

- [ ] **KPI-01**: User sees overall appointment compliance percentage (CUMPLIO CITA = SI / total completed)
- [ ] **KPI-02**: User sees compliance breakdown by tipo de operacion
- [ ] **KPI-03**: User sees compliance breakdown by asignacion de servicio
- [ ] **KPI-04**: User sees compliance breakdown by punto de cargue
- [ ] **KPI-05**: User sees compliance trend over time (using historico data)

### Dashboard — Incidencias Report

- [ ] **INC-01**: User sees a dedicated list of all services where CUMPLIO CITA = NO
- [ ] **INC-02**: Each incidencia shows: fecha, punto cargue, tipo operacion, placa, punto entrega, cita entrega, observaciones
- [ ] **INC-03**: User can filter incidencias by date range
- [ ] **INC-04**: User can filter incidencias by tipo de operacion

### Views

- [ ] **VIEW-01**: Operational view — data table + live status counters for dispatchers/coordinators
- [ ] **VIEW-02**: Executive view — KPI charts + compliance trends + summary metrics for management
- [ ] **VIEW-03**: Client view — compliance report for Orlando (BOMI Supply Chain Manager) with incidencias

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
| SHEET-01 | Phase 1 | Pending |
| SHEET-02 | Phase 1 | Pending |
| SHEET-03 | Phase 1 | Pending |
| SHEET-04 | Phase 1 | Pending |
| SHEET-05 | Phase 2 | Pending |
| SHEET-06 | Phase 2 | Pending |
| SHEET-07 | Phase 2 | Pending |
| LIVE-01 | Phase 4 | Pending |
| LIVE-02 | Phase 4 | Pending |
| LIVE-03 | Phase 4 | Pending |
| LIVE-04 | Phase 4 | Pending |
| LIVE-05 | Phase 4 | Pending |
| LIVE-06 | Phase 4 | Pending |
| TABLE-01 | Phase 5 | Pending |
| TABLE-02 | Phase 5 | Pending |
| TABLE-03 | Phase 5 | Pending |
| TABLE-04 | Phase 5 | Pending |
| TABLE-05 | Phase 5 | Pending |
| TABLE-06 | Phase 5 | Pending |
| TABLE-07 | Phase 5 | Pending |
| TABLE-08 | Phase 5 | Pending |
| KPI-01 | Phase 6 | Pending |
| KPI-02 | Phase 6 | Pending |
| KPI-03 | Phase 6 | Pending |
| KPI-04 | Phase 6 | Pending |
| KPI-05 | Phase 7 | Pending |
| INC-01 | Phase 8 | Pending |
| INC-02 | Phase 8 | Pending |
| INC-03 | Phase 8 | Pending |
| INC-04 | Phase 8 | Pending |
| VIEW-01 | Phase 9 | Pending |
| VIEW-02 | Phase 10 | Pending |
| VIEW-03 | Phase 11 | Pending |

**Coverage:**
- v1 requirements: 33 total
- Mapped to phases: 33
- Unmapped: 0

---
*Requirements defined: 2026-03-31*
*Last updated: 2026-03-31 after roadmap phase mapping*
