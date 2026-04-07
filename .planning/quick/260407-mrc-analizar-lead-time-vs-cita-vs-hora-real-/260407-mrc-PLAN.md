---
phase: quick
plan: 260407-mrc
type: execute
wave: 1
depends_on: []
files_modified:
  - sheets/reader.py
  - app.py
  - templates/dashboard.html
autonomous: true
requirements: []
must_haves:
  truths:
    - "Each service shows computed arrival delta (minutes early/late) based on hora_llegada vs cita_entrega"
    - "Compliance metrics use computed time comparison, not manual CUMPLIO CITA column"
    - "Dashboard table shows color-coded delta column: green for early/on-time, red for late"
    - "Pending services (no hora_llegada) display as pending without a delta"
  artifacts:
    - path: "sheets/reader.py"
      provides: "_parse_time() helper, computed properties on Service"
      contains: "_parse_time"
    - path: "app.py"
      provides: "computed compliance metrics in _compute_metrics()"
      contains: "computed_met"
    - path: "templates/dashboard.html"
      provides: "Delta column with color-coded early/late indicators"
      contains: "arrival_delta"
  key_links:
    - from: "sheets/reader.py"
      to: "app.py"
      via: "Service.computed_met_appointment, Service.arrival_delta_minutes"
      pattern: "computed_met_appointment|arrival_delta_minutes"
    - from: "app.py"
      to: "templates/dashboard.html"
      via: "metrics context dict with computed_ keys"
      pattern: "computed_met|computed_compliance"
---

<objective>
Add computed time-based appointment compliance analysis to the BOMI Control Tower.

Purpose: The current dashboard reads the manual "CUMPLIO CITA" column from the spreadsheet. This is error-prone and depends on operators filling it in. By computing compliance from actual time data (hora_llegada vs cita_entrega), we get automated, reliable compliance tracking plus a delta showing exactly how early or late each delivery was.

Output: Updated reader with time parsing, computed properties on Service, updated metrics in app.py, and a new delta column in the dashboard table.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@sheets/reader.py
@app.py
@templates/dashboard.html
</context>

<interfaces>
<!-- Existing Service dataclass fields relevant to this work -->
From sheets/reader.py:
```python
@dataclass
class Service:
    llegada_lead_time: str = ""   # "H:MM" format (e.g., "5:11", "20:00")
    cita_entrega: str = ""        # "H:MM" format (e.g., "8:00", "15:00")
    hora_llegada: str = ""        # "H:MM:SS" or "h:mm:ss a. m./p. m." format
    cumplio_cita: str = ""        # Manual "SI"/"NO"/""

    # Existing properties (keep for backward compat):
    def is_completed(self) -> bool  # cumplio_cita in SI/NO
    def met_appointment(self) -> bool  # cumplio_cita == SI
    def missed_appointment(self) -> bool  # cumplio_cita == NO
    def is_pending(self) -> bool  # not is_completed
```

From app.py:
```python
def _compute_metrics(services) -> dict:
    # Returns: total, completed, met, missed, pending, compliance_pct,
    #          by_tipo_op, by_asignacion, by_punto_cargue

def _filter_services(services, fecha, tipo_op, punto_cargue, placa, asignacion, cumplio):
    # Returns filtered list of Service
```
</interfaces>

<tasks>

<task type="auto">
  <name>Task 1: Add _parse_time helper and computed properties to Service</name>
  <files>sheets/reader.py</files>
  <action>
    1. Add a module-level `_parse_time(raw: str) -> Optional[int]` function that converts time strings to total minutes since midnight. Must handle these formats found in the spreadsheet:
       - "H:MM" (e.g., "5:11" -> 311, "8:00" -> 480, "20:00" -> 1200)
       - "H:MM:SS" (e.g., "7:00:00" -> 420, "11:31:00" -> 691)
       - "h:mm:ss a. m." / "h:mm:ss p. m." (Colombian Spanish AM/PM format — "3:00:00 p. m." -> 900, "12:30:00 p. m." -> 750)
       - Return None for empty strings, unparseable values, or "0:00" (which appears when cita is not set)
       - Use regex to parse: `r'(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(a\.\s*m\.|p\.\s*m\.)?'` (case-insensitive)
       - For "p. m." add 720 minutes (12 hours) UNLESS hour is 12. For "a. m." if hour is 12, treat as 0.

    2. Add three computed properties to the `Service` dataclass:

       ```python
       @property
       def arrival_delta_minutes(self) -> Optional[int]:
           """Minutes between hora_llegada and cita_entrega. Negative = early, positive = late."""
           arrival = _parse_time(self.hora_llegada)
           appointment = _parse_time(self.cita_entrega)
           if arrival is None or appointment is None:
               return None
           return arrival - appointment

       @property
       def computed_met_appointment(self) -> Optional[bool]:
           """True if arrived on/before cita. None if data missing."""
           delta = self.arrival_delta_minutes
           if delta is None:
               return None
           return delta <= 0

       @property
       def lead_time_delta_minutes(self) -> Optional[int]:
           """Minutes between hora_llegada and llegada_lead_time. Negative = faster than estimate."""
           arrival = _parse_time(self.hora_llegada)
           estimated = _parse_time(self.llegada_lead_time)
           if arrival is None or estimated is None:
               return None
           return arrival - estimated
       ```

    3. Do NOT modify existing `met_appointment`, `missed_appointment`, `is_completed`, `is_pending` properties. They remain for backward compatibility with the manual column.
  </action>
  <verify>
    <automated>cd /Users/fbetncourtc/Documents/FlexOS/bomi-control-tower && python3 -c "
from sheets.reader import _parse_time, Service
# Test _parse_time
assert _parse_time('8:00') == 480, f'8:00 failed: {_parse_time(\"8:00\")}'
assert _parse_time('5:11') == 311, f'5:11 failed: {_parse_time(\"5:11\")}'
assert _parse_time('20:00') == 1200, f'20:00 failed: {_parse_time(\"20:00\")}'
assert _parse_time('7:00:00') == 420, f'7:00:00 failed: {_parse_time(\"7:00:00\")}'
assert _parse_time('11:31:00') == 691, f'11:31:00 failed: {_parse_time(\"11:31:00\")}'
assert _parse_time('3:00:00 p. m.') == 900, f'3pm failed: {_parse_time(\"3:00:00 p. m.\")}'
assert _parse_time('') is None
assert _parse_time('0:00') is None
# Test computed properties
s = Service(hora_llegada='7:00:00', cita_entrega='8:00')
assert s.arrival_delta_minutes == -60, f'delta failed: {s.arrival_delta_minutes}'
assert s.computed_met_appointment == True
s2 = Service(hora_llegada='7:00:00', cita_entrega='6:00')
assert s2.arrival_delta_minutes == 60
assert s2.computed_met_appointment == False
s3 = Service(hora_llegada='', cita_entrega='8:00')
assert s3.arrival_delta_minutes is None
assert s3.computed_met_appointment is None
print('All _parse_time and computed property tests passed')
"</automated>
  </verify>
  <done>
    - `_parse_time()` handles all three time formats from the spreadsheet
    - `Service.arrival_delta_minutes` returns integer minutes (negative=early, positive=late)
    - `Service.computed_met_appointment` returns True/False/None
    - `Service.lead_time_delta_minutes` returns integer minutes comparing actual vs estimated
    - Existing manual-column properties unchanged
  </done>
</task>

<task type="auto">
  <name>Task 2: Add computed metrics to app.py and update dashboard table</name>
  <files>app.py, templates/dashboard.html</files>
  <action>
    **app.py changes:**

    1. Update `_compute_metrics()` to add computed compliance metrics alongside manual ones:
       ```python
       # After existing manual metrics calculation, add:
       computed_completed = [s for s in services if s.computed_met_appointment is not None]
       computed_met = [s for s in services if s.computed_met_appointment is True]
       computed_missed = [s for s in services if s.computed_met_appointment is False]
       computed_compliance_pct = (len(computed_met) / len(computed_completed) * 100) if computed_completed else 0

       # Average delta for completed services
       deltas = [s.arrival_delta_minutes for s in services if s.arrival_delta_minutes is not None]
       avg_delta = round(sum(deltas) / len(deltas), 1) if deltas else 0
       ```

    2. Add these keys to the returned dict:
       - `computed_met`: len(computed_met)
       - `computed_missed`: len(computed_missed)
       - `computed_completed`: len(computed_completed)
       - `computed_compliance_pct`: round(computed_compliance_pct, 1)
       - `avg_delta_minutes`: avg_delta

    3. Update `api_services()` to include computed fields in JSON output:
       - Add `"arrival_delta_minutes": s.arrival_delta_minutes`
       - Add `"computed_met_appointment": s.computed_met_appointment`
       - Add `"lead_time_delta_minutes": s.lead_time_delta_minutes`

    **templates/dashboard.html changes:**

    1. In the KPI stat cards row, add a new card after the existing "Cumplimiento" card (or replace — keep the existing manual one but relabel it "Cumplimiento (Manual)"):
       ```html
       <div class="col-md-2">
           <div class="card stat-card h-100">
               <div class="card-body text-center">
                   <div class="compliance-big {% if metrics.computed_compliance_pct >= 90 %}compliance-good{% elif metrics.computed_compliance_pct >= 70 %}compliance-warning{% else %}compliance-bad{% endif %}">
                       {{ metrics.computed_compliance_pct }}%
                   </div>
                   <div class="stat-label">Cumplimiento (Calculado)</div>
               </div>
           </div>
       </div>
       ```
       Restructure the row to accommodate 7 cards — change columns from `col-md-2` to a flexible layout (e.g., wrap naturally or use smaller column widths like a mix of `col-6 col-md` classes).

    2. Add a "Delta" column to the Services table between "Hora Llegada" and "Cumplio":
       - Header: `<th>Delta</th>`
       - Cell content:
         ```html
         <td class="text-nowrap">
             {% if s.arrival_delta_minutes is not none %}
                 {% if s.arrival_delta_minutes <= 0 %}
                     <span class="badge bg-success">{{ s.arrival_delta_minutes }} min</span>
                 {% elif s.arrival_delta_minutes <= 15 %}
                     <span class="badge bg-warning text-dark">+{{ s.arrival_delta_minutes }} min</span>
                 {% else %}
                     <span class="badge bg-danger">+{{ s.arrival_delta_minutes }} min</span>
                 {% endif %}
             {% else %}
                 <span class="text-muted">--</span>
             {% endif %}
         </td>
         ```
       - Green badge for on-time/early (delta <= 0)
       - Yellow badge for slightly late (1-15 min)
       - Red badge for late (>15 min)

    3. Add a "Lead Time vs Real" column after "Delta" (optional, keep table clean):
       - Only show if `s.lead_time_delta_minutes is not none`
       - Format: `+X min` or `-X min` in a smaller muted badge

    4. Update the client-side JS filter at the bottom of the template to account for the new column indices (the cumplió cell index shifts from 10 to 12 due to the 2 new columns).
  </action>
  <verify>
    <automated>cd /Users/fbetncourtc/Documents/FlexOS/bomi-control-tower && python3 -c "
from sheets.reader import Service
from app import _compute_metrics

# Create test services
services = [
    Service(hora_llegada='7:00:00', cita_entrega='8:00', cumplio_cita='SI'),   # early by 60min
    Service(hora_llegada='7:00:00', cita_entrega='6:00', cumplio_cita='NO'),   # late by 60min
    Service(hora_llegada='', cita_entrega='15:00', cumplio_cita=''),           # pending
]
m = _compute_metrics(services)
assert 'computed_met' in m, 'missing computed_met'
assert 'computed_missed' in m, 'missing computed_missed'
assert 'computed_compliance_pct' in m, 'missing computed_compliance_pct'
assert 'avg_delta_minutes' in m, 'missing avg_delta_minutes'
assert m['computed_met'] == 1, f'computed_met should be 1, got {m[\"computed_met\"]}'
assert m['computed_missed'] == 1, f'computed_missed should be 1, got {m[\"computed_missed\"]}'
assert m['computed_compliance_pct'] == 50.0, f'compliance should be 50, got {m[\"computed_compliance_pct\"]}'
assert m['avg_delta_minutes'] == 0, f'avg delta should be 0, got {m[\"avg_delta_minutes\"]}'
print('All computed metrics tests passed')
" && python3 -c "
# Verify template has delta column
with open('templates/dashboard.html') as f:
    html = f.read()
assert 'arrival_delta_minutes' in html, 'Template missing arrival_delta_minutes'
assert 'computed_compliance_pct' in html, 'Template missing computed_compliance_pct'
print('Template verification passed')
"</automated>
  </verify>
  <done>
    - `_compute_metrics()` returns computed_met, computed_missed, computed_compliance_pct, avg_delta_minutes
    - API JSON response includes arrival_delta_minutes and computed_met_appointment per service
    - Dashboard shows "Cumplimiento (Calculado)" KPI card with color-coding
    - Services table has a Delta column with green/yellow/red badges
    - Pending services show "--" in the delta column
    - Client-side JS filter indices updated to match new column layout
  </done>
</task>

</tasks>

<verification>
1. `python3 -c "from sheets.reader import _parse_time; assert _parse_time('8:00') == 480; print('OK')"` -- time parsing works
2. `python3 -c "from app import _compute_metrics; print('OK')"` -- metrics import works
3. Start the server (`python3 -m uvicorn app:app --reload`) and verify:
   - Dashboard shows a "Cumplimiento (Calculado)" card
   - Services table has a "Delta" column with colored badges
   - Early arrivals show green negative values
   - Late arrivals show red positive values
   - Pending services show "--"
4. `curl -s http://localhost:8000/api/services | python3 -m json.tool | head -30` -- JSON includes arrival_delta_minutes
</verification>

<success_criteria>
- Time parsing handles all three formats from the spreadsheet (H:MM, H:MM:SS, H:MM:SS a. m./p. m.)
- Computed compliance metrics are independent of the manual CUMPLIO CITA column
- Delta column provides at-a-glance visual for early/late arrivals
- All existing dashboard functionality (filters, incidencias, manual compliance) unchanged
- No runtime errors when time data is missing or malformed
</success_criteria>

<output>
After completion, create `.planning/quick/260407-mrc-analizar-lead-time-vs-cita-vs-hora-real-/260407-mrc-SUMMARY.md`
</output>
