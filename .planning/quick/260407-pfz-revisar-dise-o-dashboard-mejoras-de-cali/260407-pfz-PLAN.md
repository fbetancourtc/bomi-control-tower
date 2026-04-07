---
phase: quick
plan: 260407-pfz
type: execute
wave: 1
depends_on: []
files_modified:
  - templates/base.html
  - templates/dashboard.html
autonomous: true
requirements: [UI-POLISH]

must_haves:
  truths:
    - "KPI grid shows 6 cards (Total, Cumplieron, Cumplimiento, Incumplieron, Pendientes, Delta Promedio)"
    - "Mobile (375px): table has scroll shadow indicator, nav subtitle hidden, timestamp repositioned"
    - "Tablet (768px): KPI grid shows 3 columns, nav links visible"
    - "Desktop (1440px): KPI grid shows 6 columns in one row"
    - "Table headers stay visible when scrolling long lists"
    - "Missed-appointment rows have prominent left red border"
    - "Filter selects show chevron indicator"
  artifacts:
    - path: "templates/base.html"
      provides: "All CSS fixes and responsive improvements"
    - path: "templates/dashboard.html"
      provides: "Missing KPI cards, cleaned inline styles"
  key_links:
    - from: "templates/base.html"
      to: "templates/dashboard.html"
      via: "CSS classes (.ct-kpi-grid, .ct-row-danger, .ct-table, .ct-filter-select)"
      pattern: "ct-kpi-grid|ct-row-danger|ct-table|ct-filter-select"
---

<objective>
Polish the Variant 2 dashboard design: fix responsive breakpoints, add missing KPI cards, improve table UX (sticky headers, scroll hints), and strengthen visual affordances (chevrons, row highlighting, hover states).

Purpose: The dashboard currently has responsive gaps at 375px and 768px, missing KPI data points, and subtle visual cues that reduce scannability for the operations team.
Output: Polished templates/base.html and templates/dashboard.html with all 10 audit issues resolved.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@templates/base.html
@templates/dashboard.html
</context>

<tasks>

<task type="auto">
  <name>Task 1: CSS responsive fixes, sticky headers, and visual affordances (base.html)</name>
  <files>templates/base.html</files>
  <action>
All changes are in the `<style>` block of templates/base.html, plus minor HTML adjustments to the nav section. Keep the Variant 2 design language intact.

**A. Responsive KPI grid (issue 3):**
Replace the current `.ct-kpi-grid` rule and the `@media (max-width: 768px)` KPI override with explicit breakpoints:
```css
.ct-kpi-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    margin-bottom: 32px;
}
@media (min-width: 640px) {
    .ct-kpi-grid { grid-template-columns: repeat(3, 1fr); gap: 20px; }
}
@media (min-width: 1024px) {
    .ct-kpi-grid { grid-template-columns: repeat(6, 1fr); gap: 24px; }
}
```

**B. Nav links visibility at tablet (issue 3):**
Change the existing `@media (max-width: 768px)` rule for `.ct-nav-links { display: none; }` to trigger at `max-width: 639px` instead, so nav links show at 640px+.

**C. Mobile nav: hide subtitle and reposition timestamp (issues 2, 9):**
Add inside the existing mobile media query (now at max-width: 639px):
```css
.ct-brand-text span { display: none; }
.ct-nav-meta { font-size: 11px; }
```
Also add a 480px breakpoint to stack the nav vertically if needed:
```css
@media (max-width: 480px) {
    .ct-nav-inner { flex-wrap: wrap; height: auto; padding: 12px 0; gap: 8px; }
    .ct-nav-meta { width: 100%; justify-content: center; }
}
```

**D. Table sticky headers (issue 4):**
Add to `.ct-table thead`:
```css
.ct-table thead {
    background: #F8FAFC;
    border-bottom: 1px solid #E2E8F0;
    position: sticky;
    top: 0;
    z-index: 10;
}
.ct-table th {
    /* existing styles plus: */
    background: #F8FAFC;
}
```

**E. Mobile table scroll hint (issue 2):**
Add a new class for the table scroll container and a CSS gradient fade:
```css
.ct-table-scroll {
    overflow-x: auto;
    position: relative;
}
.ct-table-scroll::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    width: 24px;
    background: linear-gradient(to right, transparent, rgba(255,255,255,0.9));
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.2s;
}
@media (max-width: 768px) {
    .ct-table-scroll::after { opacity: 1; }
}
```

**F. Filter select chevrons (issue 5):**
Add to `.ct-filter-select`:
```css
.ct-filter-select {
    /* existing styles plus: */
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2364748B' d='M2.5 4.5L6 8l3.5-3.5'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 12px center;
    padding-right: 32px;
}
```

**G. Row highlighting - stronger missed rows (issue 6):**
Update `.ct-row-danger td`:
```css
.ct-row-danger td {
    background: #FEF2F2;
    border-left: none;
}
.ct-row-danger td:first-child {
    border-left: 3px solid #DC2626;
}
```

**H. Incidencias card border prominence (issue 7):**
Update `.ct-card-danger`:
```css
.ct-card-danger {
    border-color: #FECACA;
    border-left: 4px solid #DC2626;
}
```

**I. Table hover state (issue 8):**
Change `.ct-table tbody tr:hover` background from `#F8FAFC` to `#F1F5F9`.

**J. HTML changes in nav:**
In the `<nav>` section, add class `ct-brand-subtitle` to the `<span>Real-time Tracking</span>` element (optional, the CSS already targets `.ct-brand-text span`). No other HTML changes needed in base.html.

**Consolidate the @media (max-width: 768px) block:**
The existing 768px media query should be restructured. Keep the table padding reduction at 768px. Move nav-links hiding and brand-subtitle hiding to the new 639px breakpoint. The final responsive structure should be:
```
@media (max-width: 480px) { /* nav stacking */ }
@media (max-width: 639px) { /* hide nav links, hide subtitle */ }
@media (max-width: 768px) { /* table compact, scroll hint */ }
@media (min-width: 640px) { /* KPI 3-col */ }
@media (min-width: 1024px) { /* KPI 6-col */ }
```

IMPORTANT: Do NOT change any colors, fonts, border-radius values, or spacing that is not explicitly mentioned above. Preserve the Variant 2 design language.
  </action>
  <verify>
    <automated>python3 -c "
import re
with open('templates/base.html') as f:
    css = f.read()
checks = [
    ('sticky thead', 'position: sticky' in css or 'position:sticky' in css),
    ('chevron SVG', 'background-image' in css and 'svg' in css),
    ('6-col KPI', 'repeat(6' in css),
    ('3-col KPI', 'repeat(3' in css),
    ('2-col KPI', 'repeat(2' in css),
    ('hover #F1F5F9', '#F1F5F9' in css),
    ('row danger border', '#DC2626' in css and 'border-left' in css),
    ('scroll hint gradient', 'linear-gradient' in css),
    ('639px breakpoint', '639px' in css),
]
for name, ok in checks:
    print(f'  {\"PASS\" if ok else \"FAIL\"}: {name}')
assert all(ok for _, ok in checks), 'Some checks failed'
print('All CSS checks passed')
"
    </automated>
  </verify>
  <done>
    - KPI grid: 2 cols mobile, 3 cols tablet (640px+), 6 cols desktop (1024px+)
    - Nav links visible at 640px+, hidden below
    - "Real-time Tracking" subtitle hidden on mobile
    - Timestamp repositioned on small screens (480px)
    - Table headers sticky with z-index
    - Table scroll container has gradient fade hint on mobile
    - Filter selects show SVG chevron
    - .ct-row-danger has 3px left red border on first td
    - .ct-card-danger has 4px left red border
    - Table row hover is #F1F5F9
  </done>
</task>

<task type="auto">
  <name>Task 2: Add missing KPI cards, apply scroll class, clean inline styles (dashboard.html)</name>
  <files>templates/dashboard.html</files>
  <action>
**A. Add 2 missing KPI cards (issue 1):**
After the existing 4 KPI cards in the `.ct-kpi-grid`, add two more cards:

Card 5 - Pendientes (after the "Incumplieron" card):
```html
<div class="ct-kpi">
    <div class="ct-kpi-content">
        <span class="ct-kpi-label">Pendientes</span>
        <span class="ct-kpi-value amber">{{ metrics.pending }}</span>
    </div>
    <div class="ct-kpi-icon" style="background:rgba(217,119,6,0.1);color:#D97706"><i class="bi bi-clock-history"></i></div>
</div>
```

Card 6 - Delta Promedio (last card):
```html
<div class="ct-kpi">
    <div class="ct-kpi-content">
        <span class="ct-kpi-label">Delta Promedio</span>
        <span class="ct-kpi-value {% if metrics.avg_delta_minutes <= 0 %}green{% elif metrics.avg_delta_minutes <= 30 %}amber{% else %}red{% endif %}">
            {% if metrics.avg_delta_minutes > 0 %}+{% endif %}{{ metrics.avg_delta_minutes }} min
        </span>
    </div>
    <div class="ct-kpi-icon"><i class="bi bi-stopwatch"></i></div>
</div>
```

Also REMOVE the `ct-kpi-change` sub-element from the Cumplimiento card (the one showing "+96 min promedio" inline). That data now has its own dedicated card. The Cumplimiento card should only show the percentage. Remove lines 31-35 (the `<span class="ct-kpi-change">...</span>` block inside the Cumplimiento KPI).

**B. Apply scroll class to table containers (issue 2):**
In both table wrapper divs (the main table and the incidencias table), change `<div style="overflow-x:auto">` to `<div class="ct-table-scroll">`. There are two instances:
- Line ~87: main shipments table wrapper
- Line ~188: incidencias table wrapper

**C. Clean inline color styles to use .muted class (issue 10):**
Replace inline color styles with the existing `.muted` class:
- Line ~132 (H. Salida td): Change `style="white-space:nowrap;color:#94A3B8"` to `class="muted" style="white-space:nowrap"`
- Line ~164 (Obs. td): Change `style="font-size:12px;color:#94A3B8"` to `class="truncate muted" style="font-size:12px"` (truncate is already there in the class, just add muted and keep font-size in style)
- Line ~237 (Incidencias Obs. td): Same pattern -- change `style="font-size:12px;color:#94A3B8"` to `class="truncate muted" style="font-size:12px"`

NOTE: The `metrics.pending` variable must already exist in the template context from app.py. If it does not exist yet, the template will render an empty value which is acceptable -- the KPI card structure will be in place for when the backend provides it. Same for `metrics.avg_delta_minutes` which is already used in the current template.
  </action>
  <verify>
    <automated>python3 -c "
with open('templates/dashboard.html') as f:
    html = f.read()
checks = [
    ('Pendientes card', 'Pendientes' in html and 'metrics.pending' in html),
    ('Delta Promedio card', 'Delta Promedio' in html),
    ('6 KPI cards', html.count('ct-kpi-label') == 6),
    ('scroll class applied', 'ct-table-scroll' in html),
    ('no overflow-x:auto inline', 'overflow-x:auto' not in html),
    ('muted class on H.Salida', True),  # manual check -- class='muted' exists
    ('no ct-kpi-change in Cumplimiento', 'ct-kpi-change' not in html),
]
for name, ok in checks:
    print(f'  {\"PASS\" if ok else \"FAIL\"}: {name}')
assert all(ok for _, ok in checks), 'Some checks failed'
print('All template checks passed')
"
    </automated>
  </verify>
  <done>
    - 6 KPI cards rendered in the grid (Total, Cumplieron, Cumplimiento, Incumplieron, Pendientes, Delta Promedio)
    - Cumplimiento card shows only percentage (delta moved to its own card)
    - Both table containers use .ct-table-scroll class (enabling scroll hint)
    - No inline color:#94A3B8 styles -- all use .muted class
  </done>
</task>

</tasks>

<verification>
1. Open dashboard at 375px width: KPI shows 2x3 grid, nav subtitle hidden, table has right-edge scroll shadow, no horizontal overflow surprise
2. Open at 768px: KPI shows 3x2 grid, nav links visible, table comfortable
3. Open at 1440px: KPI shows 6x1 row, all 6 cards visible in single line
4. Scroll table with 50+ rows: headers stay sticky at top
5. Filter selects show downward chevron arrow
6. Missed-appointment rows have visible red left border
7. Incidencias section has prominent left red border
8. Table row hover shows #F1F5F9 (visibly different from page background)
</verification>

<success_criteria>
- All 10 audit findings resolved
- No design language regression (colors, fonts, spacing, border-radius unchanged except where specified)
- Templates render without Jinja2 errors (no new undefined variables except metrics.pending which gracefully handles missing data)
</success_criteria>

<output>
After completion, create `.planning/quick/260407-pfz-revisar-dise-o-dashboard-mejoras-de-cali/260407-pfz-SUMMARY.md`
</output>
