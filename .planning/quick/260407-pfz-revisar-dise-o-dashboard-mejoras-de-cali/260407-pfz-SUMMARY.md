---
phase: quick
plan: 260407-pfz
subsystem: frontend/dashboard
tags: [css, responsive, kpi, ux-polish]
dependency_graph:
  requires: []
  provides: [responsive-kpi-grid, sticky-headers, scroll-hints, row-highlighting]
  affects: [templates/base.html, templates/dashboard.html]
tech_stack:
  added: []
  patterns: [ct-table-scroll, responsive-grid-breakpoints, css-only-chevrons]
key_files:
  created: []
  modified:
    - templates/base.html
    - templates/dashboard.html
decisions:
  - "Nav links visibility breakpoint at 639px (not 768px) to show nav on tablets"
  - "Subtitle hidden via CSS on brand-text span (no extra class needed)"
  - "Scroll hint uses CSS ::after pseudo-element with gradient fade"
metrics:
  duration: "3 minutes"
  completed: "2026-04-07"
  tasks_completed: 2
  tasks_total: 2
---

# Quick Task 260407-pfz: Dashboard Design Polish Summary

Responsive CSS fixes, missing KPI cards, sticky headers, and visual affordance improvements for Variant 2 dashboard.

## One-liner

Responsive KPI grid (2/3/6 col breakpoints), sticky table headers, scroll hints, chevron selects, and 2 new KPI cards (Pendientes + Delta Promedio).

## Changes Made

### Task 1: CSS responsive fixes, sticky headers, and visual affordances (base.html)

**Commit:** `28f68d9`

- **Responsive KPI grid**: Replaced `auto-fit` with explicit breakpoints: 2-col at mobile, 3-col at 640px+, 6-col at 1024px+
- **Nav links**: Visibility breakpoint moved from 768px to 639px so tablets show nav links
- **Mobile nav**: Subtitle hidden below 639px, timestamp repositioned with 480px vertical stacking
- **Sticky headers**: `position: sticky; top: 0; z-index: 10` on thead with matching `background` on th
- **Scroll hint**: New `.ct-table-scroll` class with CSS `::after` gradient fade, visible on mobile (768px)
- **Filter chevrons**: SVG data URI background-image on `.ct-filter-select` with padding-right for clearance
- **Row highlighting**: `.ct-row-danger td:first-child` gets 3px solid #DC2626 left border
- **Incidencias card**: `.ct-card-danger` gets 4px solid #DC2626 left border
- **Hover state**: Table row hover changed from #F8FAFC to #F1F5F9 for visible contrast

### Task 2: Add missing KPI cards, apply scroll class, clean inline styles (dashboard.html)

**Commit:** `f78c76b`

- **Pendientes KPI card**: New card with `metrics.pending`, amber color, clock-history icon
- **Delta Promedio KPI card**: New card with `metrics.avg_delta_minutes`, conditional coloring (green/amber/red)
- **Cumplimiento card cleaned**: Removed inline `ct-kpi-change` sub-element (delta now in its own card)
- **Scroll class applied**: Both table containers changed from `style="overflow-x:auto"` to `class="ct-table-scroll"`
- **Inline styles cleaned**: Three instances of `color:#94A3B8` replaced with `.muted` CSS class

## Audit Issues Resolved

| # | Issue | Resolution |
|---|-------|-----------|
| 1 | Missing KPI cards (Pendientes, Delta Promedio) | Added 2 new cards to ct-kpi-grid |
| 2 | Mobile table scroll hint missing | ct-table-scroll class with gradient ::after |
| 3 | KPI grid responsive gaps at 375px/768px | Explicit 2/3/6 column breakpoints |
| 4 | Table headers not sticky | position:sticky on thead |
| 5 | Filter selects lack chevron indicator | SVG data URI background-image |
| 6 | Missed-appointment rows lack visual prominence | 3px red left border on first td |
| 7 | Incidencias card border not prominent | 4px red left border |
| 8 | Table hover state barely visible | Changed from #F8FAFC to #F1F5F9 |
| 9 | Mobile timestamp positioning | 480px breakpoint for nav vertical stacking |
| 10 | Inline color styles instead of classes | Replaced with .muted class |

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None. All KPI variables (`metrics.pending`, `metrics.avg_delta_minutes`) are already provided by the backend (`app.py`).

## Self-Check: PASSED
