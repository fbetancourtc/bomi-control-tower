---
phase: quick
plan: 260407-mrc
subsystem: sheets-reader, app-metrics, dashboard-ui
tags: [time-parsing, compliance, computed-metrics, delta-column]
dependency_graph:
  requires: [sheets/reader.py, app.py, templates/dashboard.html]
  provides: [_parse_time, computed_met_appointment, arrival_delta_minutes, computed-compliance-metrics]
  affects: [dashboard-kpi-cards, services-table, api-json]
tech_stack:
  added: []
  patterns: [computed-properties-on-dataclass, regex-time-parsing, jinja2-conditional-badges]
key_files:
  created: []
  modified:
    - sheets/reader.py
    - app.py
    - templates/dashboard.html
decisions:
  - "Kept manual compliance properties (met_appointment, is_completed) for backward compatibility"
  - "Used regex for time parsing to handle all three Colombian time formats in one function"
  - "Green/yellow/red badge thresholds: <=0 green, 1-15 yellow, >15 red"
  - "Relabeled existing compliance as 'Manual', new computed as 'Calculado'"
metrics:
  duration: "2 minutes"
  completed: "2026-04-07"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 3
---

# Quick Task 260407-mrc: Computed Time-Based Compliance Analysis Summary

**One-liner:** Automated appointment compliance via time parsing (hora_llegada vs cita_entrega) with color-coded delta column and dual compliance KPIs

## What Was Done

### Task 1: _parse_time helper and computed properties (03e103c)

Added a `_parse_time(raw: str) -> Optional[int]` module-level function to `sheets/reader.py` that converts all three time formats found in the BOMI spreadsheet to total minutes since midnight:

- `H:MM` (e.g., "5:11" -> 311, "20:00" -> 1200)
- `H:MM:SS` (e.g., "7:00:00" -> 420)
- `h:mm:ss a. m.` / `h:mm:ss p. m.` (Colombian Spanish AM/PM, e.g., "3:00:00 p. m." -> 900)

Returns `None` for empty strings, unparseable values, or "0:00" (unset cita).

Added three computed properties to the `Service` dataclass:
- `arrival_delta_minutes`: Integer minutes between hora_llegada and cita_entrega (negative = early, positive = late)
- `computed_met_appointment`: `True` if on-time/early, `False` if late, `None` if data missing
- `lead_time_delta_minutes`: Integer minutes comparing actual arrival vs lead time estimate

Existing manual-column properties (`met_appointment`, `is_completed`, `missed_appointment`, `is_pending`) left untouched for backward compatibility.

### Task 2: Computed metrics and dashboard delta column (b65f751)

**app.py changes:**
- Extended `_compute_metrics()` with `computed_met`, `computed_missed`, `computed_completed`, `computed_compliance_pct`, and `avg_delta_minutes`
- Extended `api_services()` JSON output with `arrival_delta_minutes`, `computed_met_appointment`, `lead_time_delta_minutes`

**templates/dashboard.html changes:**
- Restructured KPI card row from 6 fixed `col-md-2` to 7 flexible `col-6 col-lg` cards
- Added "Cumplimiento (Calculado)" KPI card with same color thresholds as manual
- Added "Delta Promedio" KPI card showing average minutes early/late
- Relabeled existing compliance card as "Cumplimiento (Manual)"
- Added "Delta" column to services table with color-coded badges: green (on-time/early), yellow (1-15 min late), red (>15 min late)
- Added "LT vs Real" column showing lead time vs actual arrival delta
- Updated client-side JS filter index for cumplió column (10 -> 12)

## Deviations from Plan

None -- plan executed exactly as written.

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| 1 | 03e103c | feat(quick-260407-mrc): add _parse_time helper and computed time properties to Service |
| 2 | b65f751 | feat(quick-260407-mrc): add computed compliance metrics and delta column to dashboard |

## Known Stubs

None -- all features are fully wired with live data.

## Self-Check: PASSED

- [x] sheets/reader.py exists and contains `_parse_time`
- [x] app.py exists and contains `computed_met`
- [x] templates/dashboard.html exists and contains `arrival_delta_minutes`
- [x] Commit 03e103c exists
- [x] Commit b65f751 exists
- [x] All verification tests pass
