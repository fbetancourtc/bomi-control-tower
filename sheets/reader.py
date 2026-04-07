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

    # "0:00" means cita is not set in the spreadsheet
    if total == 0:
        return None

    return total


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
    def is_completed(self) -> bool:
        return self.cumplio_cita.strip().upper() in ("SI", "SÍ", "NO")

    @property
    def met_appointment(self) -> bool:
        return self.cumplio_cita.strip().upper() in ("SI", "SÍ")

    @property
    def missed_appointment(self) -> bool:
        return self.cumplio_cita.strip().upper() == "NO"

    @property
    def is_pending(self) -> bool:
        return not self.is_completed

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
