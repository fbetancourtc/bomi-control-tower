"""Read BOMI Control Citas spreadsheet with header-based column resolution."""

import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from googleapiclient.errors import HttpError

from .auth import get_sheets_service

logger = logging.getLogger(__name__)

SHEET_ID = os.environ.get("BOMI_SHEET_ID", "")

_TIME_RE = re.compile(
    r"(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(a\.\s*m\.|p\.\s*m\.)?",
    re.IGNORECASE,
)

# Matches "DD/MM/YYYY HH:MM" or "DD/MM/YYYY HH:MM:SS"
_DATETIME_RE = re.compile(
    r"(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?",
)


def _parse_time(raw: str) -> Optional[int]:
    """Convert a time string to total minutes since midnight.

    Handles formats found in the BOMI spreadsheet:
      - "H:MM"          (e.g. "5:11" -> 311, "20:00" -> 1200)
      - "H:MM:SS"       (e.g. "7:00:00" -> 420)
      - "h:mm:ss a. m." / "h:mm:ss p. m." (Colombian AM/PM)

    Returns None for empty, unparseable, or "0:00" (unset cita).
    """
    if not raw or not raw.strip():
        return None

    m = _TIME_RE.match(raw.strip())
    if not m:
        return None

    hour = int(m.group(1))
    minute = int(m.group(2))

    ampm = m.group(4)
    if ampm:
        ampm_lower = ampm.lower().replace(" ", "")
        if "p" in ampm_lower and hour != 12:
            hour += 12
        elif "a" in ampm_lower and hour == 12:
            hour = 0

    total = hour * 60 + minute
    return total


def _parse_datetime(raw: str) -> Optional[datetime]:
    """Parse a datetime string 'DD/MM/YYYY HH:MM' or 'DD/MM/YYYY HH:MM:SS'.

    Returns None for empty or unparseable values.
    """
    if not raw or not raw.strip():
        return None

    m = _DATETIME_RE.match(raw.strip())
    if not m:
        return None

    day = int(m.group(1))
    month = int(m.group(2))
    year = int(m.group(3))
    hour = int(m.group(4))
    minute = int(m.group(5))
    second = int(m.group(6)) if m.group(6) else 0

    try:
        return datetime(year, month, day, hour, minute, second)
    except ValueError:
        return None


def _build_datetime(date_str: str, time_str: str) -> Optional[datetime]:
    """Combine a date 'DD/MM/YYYY' and time 'H:MM' or 'H:MM:SS' into a datetime.

    Returns None if either is empty/unparseable.
    """
    if not date_str or not date_str.strip() or not time_str or not time_str.strip():
        return None

    minutes = _parse_time(time_str)
    if minutes is None:
        return None

    parts = date_str.strip().split("/")
    if len(parts) != 3:
        return None

    try:
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
        hour = minutes // 60
        minute = minutes % 60
        return datetime(year, month, day, hour, minute)
    except (ValueError, IndexError):
        return None


@dataclass
class Service:
    """A single delivery/service row from the spreadsheet."""
    fecha: str = ""
    hora_cargue: str = ""
    punto_cargue: str = ""
    cliente: str = ""
    tipo_operacion: str = ""
    placa: str = ""
    tipo_vh: str = ""
    recurencia_vh: str = ""
    asignacion_servicio: str = ""
    punto_entrega: str = ""
    hora_salida: str = ""
    llegada_lead_time: str = ""
    fecha_entrega: str = ""
    cita_entrega: str = ""
    hora_llegada: str = ""
    cumplio_cita: str = ""
    observaciones: str = ""
    detalle_observaciones: str = ""

    @property
    def _arrival_dt(self) -> Optional[datetime]:
        """Parse hora_llegada as a full datetime (DD/MM/YYYY HH:MM) or time-only."""
        # Try datetime format first (new format with date)
        dt = _parse_datetime(self.hora_llegada)
        if dt is not None:
            return dt
        # Fallback: time-only → combine with fecha_entrega
        return _build_datetime(self.fecha_entrega, self.hora_llegada)

    @property
    def _appointment_dt(self) -> Optional[datetime]:
        """Parse cita_entrega combined with fecha_entrega as a full datetime.

        Returns None if cita_entrega is '0:00' (means unset in the spreadsheet).
        """
        if self.cita_entrega.strip() in ("0:00", "0:00:00", ""):
            return None
        return _build_datetime(self.fecha_entrega, self.cita_entrega)

    @property
    def arrival_delta_minutes(self) -> Optional[int]:
        """Minutes between hora_llegada and cita_entrega. Negative = early, positive = late."""
        arrival = self._arrival_dt
        appointment = self._appointment_dt
        if arrival is None or appointment is None:
            return None
        delta = arrival - appointment
        return int(delta.total_seconds() // 60)

    @property
    def is_completed(self) -> bool:
        """True if we have both hora_llegada and cita_entrega to compare."""
        return self.arrival_delta_minutes is not None

    @property
    def met_appointment(self) -> bool:
        """True if arrived on/before cita (hora_llegada <= cita_entrega)."""
        delta = self.arrival_delta_minutes
        return delta is not None and delta <= 0

    @property
    def missed_appointment(self) -> bool:
        """True if arrived after cita (hora_llegada > cita_entrega)."""
        delta = self.arrival_delta_minutes
        return delta is not None and delta > 0

    @property
    def is_pending(self) -> bool:
        """True if hora_llegada is missing (vehicle hasn't arrived yet)."""
        return not self.is_completed

    @property
    def lead_time_delta_minutes(self) -> Optional[int]:
        """Minutes between hora_llegada and llegada_lead_time. Negative = faster than estimate."""
        arrival = self._arrival_dt
        estimated = _build_datetime(self.fecha_entrega, self.llegada_lead_time)
        if arrival is None or estimated is None:
            return None
        delta = arrival - estimated
        return int(delta.total_seconds() // 60)


@dataclass
class HistoricoService:
    """A row from the historico tab."""
    fecha: str = ""
    id_liftit: str = ""
    hora_cargue: str = ""
    punto_cargue: str = ""
    tipo_vh: str = ""
    conductor: str = ""
    placa: str = ""
    celular: str = ""
    cedula: str = ""
    asignacion_servicio: str = ""
    punto_entrega: str = ""
    cita_entrega: str = ""

    @property
    def is_completed(self) -> bool:
        return False  # historico doesn't have cumplio_cita in headers we saw

    @property
    def met_appointment(self) -> bool:
        return False

    @property
    def missed_appointment(self) -> bool:
        return False


@dataclass
class Tipologia:
    """A service type from the TIPOLOGIAS tab."""
    tipo: str = ""
    concepto: str = ""


@dataclass
class SpreadsheetData:
    """All data from the BOMI spreadsheet."""
    services: list[Service] = field(default_factory=list)
    historico: list[HistoricoService] = field(default_factory=list)
    tipologias: list[Tipologia] = field(default_factory=list)
    last_updated: Optional[datetime] = None
    error: Optional[str] = None


# Header-to-field mapping for Actual tab
ACTUAL_HEADER_MAP = {
    "FECHA": "fecha",
    "HORA DE CARGUE": "hora_cargue",
    "PUNTO CARGUE": "punto_cargue",
    "CLIENTE  USP BOMI ": "cliente",
    "CLIENTE USP BOMI": "cliente",
    "CLIENTE  UPS BOMI ": "cliente",
    "CLIENTE UPS BOMI": "cliente",
    "TIPO DE OPERACIÓN": "tipo_operacion",
    "TIPO DE OPERACION": "tipo_operacion",
    "PLACA": "placa",
    "ASIGNACION DE SERVICIO": "asignacion_servicio",
    "ASIGNACIÓN DE SERVICIO": "asignacion_servicio",
    "PUNTO DE ENTREGA": "punto_entrega",
    "HORA DE SALIDA": "hora_salida",
    "LLEGADA SEGUN LEAD TIME": "llegada_lead_time",
    "LLEGADA SEGÚN LEAD TIME": "llegada_lead_time",
    "FECHA DE ENTREGA": "fecha_entrega",
    "CITA DE ENTREGA": "cita_entrega",
    "HORA DE LLEGADA AL PUNTO DE ENTREGA": "hora_llegada",
    "CUMPLIO CITA": "cumplio_cita",
    "CUMPLIÓ CITA": "cumplio_cita",
    "CUMPLIÓ CITA ": "cumplio_cita",
    "CUMPLIO CITA ": "cumplio_cita",
    "OBSERVACIONES": "observaciones",
    "TIPO VH": "tipo_vh",
    "RECURENCIA VH": "recurencia_vh",
    "DETALLE DE OBSERVACIONES": "detalle_observaciones",
}

HISTORICO_HEADER_MAP = {
    "FECHA": "fecha",
    "ID LIFTIT": "id_liftit",
    "HORA DE CARGUE": "hora_cargue",
    "PUNTO DE CARGUE": "punto_cargue",
    "PUNTO CARGUE": "punto_cargue",
    "TIPO VH": "tipo_vh",
    "CONDUCTOR": "conductor",
    "PLACA": "placa",
    "CELULAR": "celular",
    "CEDULA": "cedula",
    "CÉDULA": "cedula",
    "ASIGNACION DE SERVICIO": "asignacion_servicio",
    "ASIGNACIÓN DE SERVICIO": "asignacion_servicio",
    "PUNTO DE ENTREGA": "punto_entrega",
    "CITA DE ENTREGA": "cita_entrega",
}


def _resolve_columns(header_row: list[str], header_map: dict[str, str]) -> dict[int, str]:
    """Map column indices to field names using header names."""
    col_map = {}
    for i, header in enumerate(header_row):
        cleaned = header.strip()
        if cleaned in header_map:
            col_map[i] = header_map[cleaned]
        elif cleaned.upper() in {k.upper(): k for k in header_map}:
            for key, val in header_map.items():
                if key.upper() == cleaned.upper():
                    col_map[i] = val
                    break
    return col_map


def _get_cell(row: list, idx: int) -> str:
    """Safely get a cell value, handling sparse rows."""
    if idx < len(row):
        val = row[idx]
        return str(val).strip() if val is not None else ""
    return ""


def _read_tab(service, tab_name: str) -> list[list]:
    """Read all values from a tab."""
    try:
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=SHEET_ID, range=tab_name)
            .execute()
        )
        return result.get("values", [])
    except HttpError as e:
        logger.error("Failed to read tab %s: %s", tab_name, e)
        return []


def read_all(service=None) -> SpreadsheetData:
    """Read all tabs from the BOMI spreadsheet."""
    if service is None:
        service = get_sheets_service()

    data = SpreadsheetData()

    try:
        # --- SEGUIMIENTO tab ---
        actual_rows = _read_tab(service, "SEGUIMIENTO")
        if actual_rows:
            col_map = _resolve_columns(actual_rows[0], ACTUAL_HEADER_MAP)
            for row in actual_rows[1:]:
                if not any(_get_cell(row, i) for i in range(min(3, len(row)))):
                    continue  # skip empty rows
                kwargs = {}
                for idx, field_name in col_map.items():
                    kwargs[field_name] = _get_cell(row, idx)
                data.services.append(Service(**kwargs))

        # --- TIPOLOGIAS tab ---
        tipo_rows = _read_tab(service, "TIPOLOGIAS")
        for row in tipo_rows:
            if len(row) >= 3 and row[1] and row[1].strip():
                data.tipologias.append(
                    Tipologia(tipo=str(row[1]).strip(), concepto=str(row[2]).strip() if len(row) > 2 else "")
                )

        # Note: no "historico" tab exists in current spreadsheet.
        # Tabs available: SEGUIMIENTO, LEAD TIME, TIPOLOGIAS.

        data.last_updated = datetime.now()

    except Exception as e:
        logger.exception("Error reading spreadsheet")
        data.error = str(e)

    return data


def _col_letter(idx: int) -> str:
    """Convert 0-based column index to spreadsheet letter (0=A, 25=Z, 26=AA, etc.)."""
    result = ""
    while idx >= 0:
        result = chr(ord("A") + idx % 26) + result
        idx = idx // 26 - 1
    return result


def migrate_llegada_to_datetime(service=None) -> dict:
    """Migrate column O (HORA DE LLEGADA) from time-only to date+time format.

    Combines FECHA DE ENTREGA (M) + HORA DE LLEGADA (O) → writes
    'DD/MM/YYYY HH:MM' back to column O. Skips rows that already
    have the datetime format or are empty.

    Returns dict with counts: migrated, skipped, already_ok, errors.
    """
    if service is None:
        service = get_sheets_service()

    result = {"migrated": 0, "skipped": 0, "already_ok": 0, "errors": 0}

    try:
        rows = _read_tab(service, "SEGUIMIENTO")
        if not rows:
            return result

        headers = rows[0]
        col_map = _resolve_columns(headers, ACTUAL_HEADER_MAP)

        fecha_ent_col = llegada_col = None
        for idx, field_name in col_map.items():
            if field_name == "fecha_entrega":
                fecha_ent_col = idx
            elif field_name == "hora_llegada":
                llegada_col = idx

        if fecha_ent_col is None or llegada_col is None:
            logger.error("Could not find fecha_entrega or hora_llegada columns")
            return result

        llegada_letter = _col_letter(llegada_col)
        updates = []

        for row_idx, row in enumerate(rows[1:], start=2):
            if not any(_get_cell(row, i) for i in range(min(3, len(row)))):
                continue

            llegada_val = _get_cell(row, llegada_col)
            fecha_ent_val = _get_cell(row, fecha_ent_col)

            if not llegada_val:
                result["skipped"] += 1
                continue

            # Already has datetime format?
            if _parse_datetime(llegada_val) is not None:
                result["already_ok"] += 1
                continue

            # Build datetime from fecha_entrega + hora_llegada
            dt = _build_datetime(fecha_ent_val, llegada_val)
            if dt is None:
                result["skipped"] += 1
                continue

            new_val = dt.strftime("%d/%m/%Y %H:%M")
            updates.append({
                "range": f"SEGUIMIENTO!{llegada_letter}{row_idx}",
                "values": [[new_val]],
            })
            result["migrated"] += 1

        if updates:
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=SHEET_ID,
                body={"valueInputOption": "RAW", "data": updates},
            ).execute()
            logger.info("Migrated %d llegada cells to datetime format", len(updates))

    except Exception as e:
        logger.exception("Failed to migrate llegada column")
        result["errors"] = 1

    return result


def write_computed_compliance(service=None) -> dict:
    """Write computed CUMPLIO CITA values to column P of SEGUIMIENTO tab.

    Uses full datetime comparison (hora_llegada with date vs cita on fecha_entrega).

    Returns dict with counts: updated, skipped, errors.
    """
    if service is None:
        service = get_sheets_service()

    result = {"updated": 0, "skipped": 0, "errors": 0}

    try:
        rows = _read_tab(service, "SEGUIMIENTO")
        if not rows:
            return result

        headers = rows[0]
        col_map = _resolve_columns(headers, ACTUAL_HEADER_MAP)

        cita_col = llegada_col = cumplio_col = fecha_ent_col = None
        for idx, field_name in col_map.items():
            if field_name == "cita_entrega":
                cita_col = idx
            elif field_name == "hora_llegada":
                llegada_col = idx
            elif field_name == "cumplio_cita":
                cumplio_col = idx
            elif field_name == "fecha_entrega":
                fecha_ent_col = idx

        if cumplio_col is None or cita_col is None or llegada_col is None or fecha_ent_col is None:
            logger.error("Could not find required columns")
            return result

        col_letter = _col_letter(cumplio_col)
        updates = []

        for row_idx, row in enumerate(rows[1:], start=2):
            if not any(_get_cell(row, i) for i in range(min(3, len(row)))):
                continue

            llegada_val = _get_cell(row, llegada_col)
            cita_val = _get_cell(row, cita_col)
            fecha_ent_val = _get_cell(row, fecha_ent_col)

            # Parse arrival: try datetime format first, then combine with fecha_entrega
            arrival_dt = _parse_datetime(llegada_val)
            if arrival_dt is None:
                arrival_dt = _build_datetime(fecha_ent_val, llegada_val)

            # Parse appointment: fecha_entrega + cita (skip unset "0:00" citas)
            if cita_val.strip() in ("0:00", "0:00:00", ""):
                appointment_dt = None
            else:
                appointment_dt = _build_datetime(fecha_ent_val, cita_val)

            if arrival_dt is None:
                updates.append({"range": f"SEGUIMIENTO!{col_letter}{row_idx}", "values": [["PENDIENTE"]]})
                result["skipped"] += 1
                continue

            if appointment_dt is None:
                updates.append({"range": f"SEGUIMIENTO!{col_letter}{row_idx}", "values": [["PENDIENTE"]]})
                result["skipped"] += 1
                continue

            delta = arrival_dt - appointment_dt
            delta_minutes = int(delta.total_seconds() // 60)
            computed_value = "SI" if delta_minutes <= 0 else "NO"
            updates.append({"range": f"SEGUIMIENTO!{col_letter}{row_idx}", "values": [[computed_value]]})
            result["updated"] += 1

        if updates:
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=SHEET_ID,
                body={"valueInputOption": "RAW", "data": updates},
            ).execute()
            logger.info("Wrote %d compliance values to column %s", len(updates), col_letter)

    except Exception as e:
        logger.exception("Failed to write compliance values")
        result["errors"] = 1

    return result
