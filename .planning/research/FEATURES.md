# Feature Landscape

**Domain:** Logistics control tower / delivery tracking dashboard (healthcare logistics)
**Researched:** 2026-03-31
**Confidence:** MEDIUM (based on domain knowledge of logistics visibility platforms — FourKites, project44, Transporeon, Shippeo — and custom logistics dashboards; web verification unavailable)

## Table Stakes

Features users expect. Missing = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Real-time delivery status board** | Core promise of any control tower. Users need to see what's in transit, delivered, or delayed at a glance. | Med | Must show current-day operations with auto-refresh. Status categories: en ruta, entregado, demorado, pendiente. |
| **Appointment compliance rate (KPI)** | The central metric for BOMI — "CUMPLIO CITA SI/NO". Without this front-and-center, the dashboard has no purpose. | Low | Simple ratio: SI / (SI + NO). Display as percentage with color coding (green >90%, yellow 80-90%, red <80%). |
| **Filterable/sortable data table** | Operations teams live in tables. They need to filter by date, service type, loading point, vehicle plate, delivery point. | Med | Must support multi-column filtering and sorting. This IS the operational view. |
| **Date range selection** | Users need to look at today, yesterday, this week, custom ranges. Without it, the dashboard is frozen in time. | Low | Default to "today" for operations view. Allow custom range for reporting. |
| **Incidencias view (non-compliance list)** | Operations needs a focused list of failed appointments (CUMPLIO CITA = NO) to investigate and act on. | Low | Filter of the main table, but presented as its own view with OBSERVACIONES prominently displayed. |
| **Service type breakdown** | SOS URGENCIA VITAL, URGENCIA, CONSOLIDADO have very different SLAs. Mixing them hides performance problems. | Low | Show compliance rates per service type. SOS URGENCIA VITAL failures are more critical than CONSOLIDADO. |
| **Loading point breakdown** | Different loading points (CEDI Funza, CEDI Cota, etc.) have different operational dynamics. Users need to see which are performing. | Low | Group by PUNTO CARGUE, show count and compliance per point. |
| **Auto-refresh / live data** | The spreadsheet is updated throughout the day. Dashboard must reflect changes without manual reload. | Low | Polling every 60-120 seconds is sufficient. No WebSocket needed for spreadsheet-backed data. |
| **Login / access control** | Multiple user types (ops, management, client). Must restrict access. | Med | Simple auth is enough for v1. Role-based access is a differentiator, not table stakes. |
| **Responsive design** | Operations team may check on phones/tablets in warehouse. Client (Orlando) likely checks on laptop but may be mobile. | Med | Not a native app, but must be usable on mobile browsers. |

## Differentiators

Features that set the product apart. Not expected in a v1 internal tool, but deliver outsized value.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Trend analysis over time** | Move from "how did today go?" to "are we getting better or worse?" Weekly/monthly compliance trends reveal systemic issues vs one-off problems. | Med | Requires historical data (the "historico" tab exists). Line charts showing compliance % over weeks/months. |
| **Role-based views** | Operations sees the table and real-time status. Management sees KPIs and trends. Orlando (client) sees a clean compliance report without internal operational noise. | Med | Three view templates sharing the same data. Client view is the highest-value differentiator — it's what BOMI shows their customer. |
| **SLA tiering with weighted compliance** | Not all failures are equal. An SOS URGENCIA VITAL miss is catastrophically different from a CONSOLIDADO delay. Weighted compliance reflects actual service quality. | Low | Weight by service type criticality. Simple formula, high insight value. |
| **Delivery point heatmap / geographic view** | Map visualization showing delivery locations colored by compliance. Reveals geographic patterns (e.g., "we always miss Bogota Sur appointments"). | High | Requires geocoding delivery points. Valuable for route optimization conversations but complex to implement. |
| **Exception-based alerting indicators** | Color-coded rows/cards for services approaching their appointment window but not yet marked as arrived. "At risk" status before failure happens. | Med | Requires comparing CITA DE ENTREGA with current time. Only possible for today's in-progress deliveries. |
| **Vehicle utilization view** | Group by PLACA to see how many deliveries each vehicle handles, compliance per vehicle. Identifies consistently late vehicles/drivers. | Low | Simple group-by on existing data. Reveals driver/vehicle performance patterns. |
| **Exportable reports (PDF/Excel)** | Orlando (client) likely needs to share compliance data with his management chain. A downloadable report is high-value for the client relationship. | Med | PDF for executive summaries, Excel for detailed data. The client-facing report is the key export. |
| **Operation type comparison** | DEDICADO vs CONSOLIDADO vs MEDTRONIC vs ROCHE PHARMA have different operational characteristics. Comparing them reveals which operation types need attention. | Low | Bar charts comparing compliance rates across TIPO DE OPERACION. |
| **Configurable dashboard widgets** | Let users arrange which KPIs/charts appear on their landing page. | High | Nice but premature for a v1 internal tool. Consider for v2 if user base grows. |
| **Automated daily/weekly email digest** | Summary email with key metrics sent to management and client. Reduces need to log in daily. | Med | Explicitly deferred per user direction ("focus on dashboard first"). Flag for v2. |

## Anti-Features

Features to explicitly NOT build. Building these would waste time, add complexity, or misalign with the product's purpose.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Write-back to spreadsheet** | Explicitly out of scope. The spreadsheet is the source of truth, managed by ops team directly. Writing back creates data conflicts, requires conflict resolution logic, and adds massive complexity. | Read-only consumption. If feedback loops needed later, use a separate mechanism (e.g., comments in a side database). |
| **GPS / real-time vehicle tracking** | Requires GPS device integration, real-time streaming infrastructure, and map rendering. Far beyond scope of a spreadsheet-backed dashboard. This is what FourKites/project44 charge millions for. | Show delivery status from the spreadsheet data. If HORA DE LLEGADA is populated, it's arrived. That's enough. |
| **Route optimization / planning** | Route optimization is a separate product category (OptimoRoute, Routific). Adding it to a visibility dashboard creates scope creep and requires optimization algorithms. | Focus on visibility and compliance. Route insights come from analyzing delivery point patterns, not optimizing routes. |
| **TMS/ERP integration** | Explicitly out of scope. The data comes from Google Sheets. Adding SAP/Oracle integrations adds months of work and enterprise sales complexity. | Google Sheets API is the integration layer. If they migrate off sheets later, swap the data adapter. |
| **Chat / collaboration features** | Slack/Teams already exist. Building in-app chat duplicates what messaging tools do better and adds real-time infrastructure complexity. | Link to existing communication channels if needed. The OBSERVACIONES column already captures notes. |
| **Mobile native app** | Explicitly out of scope. Responsive web covers mobile use cases without App Store distribution, updates, and platform-specific development. | Build responsive web. Test on mobile browsers. Progressive Web App (PWA) wrapper only if users demand home screen access. |
| **Predictive analytics / ML forecasting** | Requires data science infrastructure, training data pipelines, and model maintenance. The current dataset (~390 rows) is too small for meaningful ML. | Trend lines and simple moving averages are sufficient for "are we improving?" The value is in visibility, not prediction. |
| **Multi-tenant architecture** | BOMI is the only client. Building multi-tenancy adds database isolation, tenant switching, and permission complexity for zero current value. | Single-tenant. If they acquire more clients, refactor then. The data adapter pattern makes this possible later. |
| **Notification system (push/email/SMS)** | Explicitly deferred per user direction. Adds background job infrastructure, notification preferences, and delivery guarantees. | Dashboard-first. Users check it proactively. Alerts are a v2 feature after the dashboard proves its value. |
| **Custom report builder** | Drag-and-drop report builders are an entire product (Metabase, Superset). Building one inside the control tower is scope explosion. | Provide 3-4 pre-built views (operational, executive, client, incidencias). Export to Excel for custom analysis. |

## Feature Dependencies

```
Login/Auth
  --> All views (every feature requires authentication)

Google Sheets data ingestion
  --> Real-time status board
  --> Data table with filters
  --> All KPI calculations
  --> All breakdown views

Real-time status board
  --> Exception alerting (needs current status + appointment time comparison)

Data table with filters
  --> Incidencias view (filtered subset of main table)
  --> Exportable reports (exports filtered data)

Date range selection
  --> Trend analysis (requires querying historical data)
  --> All views (scopes the data displayed)

Service type breakdown
  --> SLA tiering / weighted compliance (builds on per-type metrics)

Historical data access ("historico" tab)
  --> Trend analysis over time
  --> Vehicle utilization view (needs enough data points)
```

## MVP Recommendation

### Phase 1: Core Dashboard (Table Stakes)
Prioritize these to have a usable product:

1. **Google Sheets data ingestion** — without data, nothing works
2. **Login/Auth** — required for any deployment
3. **Real-time status board** — the landing page, the core promise
4. **Filterable data table** — the operational workhorse
5. **Appointment compliance KPI** — the headline number
6. **Date range selection** — scopes everything
7. **Incidencias view** — actionable list of failures
8. **Auto-refresh** — keeps data current without manual reload

### Phase 2: Breakdowns and Insights
Add analytical depth:

1. **Service type breakdown** — segment compliance by urgency level
2. **Loading point breakdown** — identify operational bottlenecks
3. **Operation type comparison** — DEDICADO vs CONSOLIDADO performance
4. **Vehicle utilization view** — driver/vehicle performance patterns

### Phase 3: Role-Based and Client-Facing
Differentiate the product:

1. **Role-based views** (operational, executive, client)
2. **Client-facing compliance report** (Orlando's view)
3. **Exportable reports** (PDF/Excel)
4. **SLA tiering with weighted compliance**

### Defer

- **Trend analysis**: Requires meaningful historical data accumulation. Build after 4-6 weeks of data collection.
- **Delivery point heatmap**: High complexity, requires geocoding. Valuable but not urgent.
- **Configurable dashboard widgets**: Premature optimization. Learn what users actually want first.
- **Email digest**: Explicitly deferred per user direction. Revisit when dashboard is validated.
- **Exception-based alerting indicators**: Requires real-time time comparison logic. Add after core dashboard is stable.

## Domain-Specific Considerations for Healthcare Logistics

Healthcare logistics (BOMI operates in pharma/medical supply chain) has specific feature expectations:

| Consideration | Impact on Features | Priority |
|---------------|-------------------|----------|
| **SOS URGENCIA VITAL = life-critical deliveries** | Failed urgent deliveries need immediate visual prominence. Red/critical styling. Consider a dedicated "urgent failures" counter on the main dashboard. | HIGH |
| **Client (Orlando) is Supply Chain Manager** | The client-facing view is not a nice-to-have — it's a business retention tool. If BOMI can't show Orlando clear compliance data, they risk the contract. | HIGH |
| **Regulatory traceability** | Healthcare logistics may require audit trails. The dashboard should timestamp when data was read, not just display current state. | MEDIUM |
| **Temperature-sensitive shipments** | Not in current data columns, but may emerge. The data model should be extensible for additional tracking dimensions. | LOW (future) |
| **Multiple delivery windows** | Healthcare facilities often have strict receiving windows. CITA DE ENTREGA captures this, but the compliance logic must handle time-based comparisons, not just date. | MEDIUM |

## Sources

- Domain knowledge from logistics visibility platforms: FourKites, project44, Transporeon, Shippeo (MEDIUM confidence — based on training data, not live verification)
- Project context from `.planning/PROJECT.md` (HIGH confidence — direct source)
- Healthcare logistics domain patterns from pharma distribution industry knowledge (MEDIUM confidence)
- Web search and web fetch were unavailable for live verification; all findings derive from training data and project context

**Note:** Web search tools were unavailable during this research session. Findings are based on extensive domain knowledge of logistics control tower platforms and healthcare supply chain operations. Confidence is MEDIUM overall — the feature landscape for logistics dashboards is well-established and unlikely to have shifted dramatically, but specific competitor feature sets should be verified if critical decisions depend on them.
