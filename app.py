"""BOMI Control Tower — FastAPI application."""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader

load_dotenv()

from sheets.reader import SpreadsheetData, read_all  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- In-memory cache ---
_cache: SpreadsheetData = SpreadsheetData()
_poll_interval = int(os.environ.get("POLL_INTERVAL_SECONDS", "45"))


async def _poll_sheets():
    """Background task: refresh spreadsheet data on interval."""
    global _cache
    while True:
        try:
            logger.info("Refreshing spreadsheet data...")
            data = await asyncio.to_thread(read_all)
            if data.error is None:
                _cache = data
                logger.info(
                    "Data refreshed: %d services, %d historico, %d tipologias",
                    len(data.services),
                    len(data.historico),
                    len(data.tipologias),
                )
            else:
                logger.error("Refresh error: %s (serving stale data)", data.error)
                if _cache.last_updated is None:
                    _cache = data
        except Exception:
            logger.exception("Poll failed")
        await asyncio.sleep(_poll_interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background polling on startup."""
    global _cache
    logger.info("Initial data load...")
    _cache = await asyncio.to_thread(read_all)
    logger.info("Loaded %d services", len(_cache.services))
    task = asyncio.create_task(_poll_sheets())
    yield
    task.cancel()


app = FastAPI(title="BOMI Control Tower", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
_jinja_env = Environment(loader=FileSystemLoader("templates"), autoescape=True)


def _render(template_name: str, **context) -> HTMLResponse:
    """Render a Jinja2 template to an HTMLResponse."""
    tmpl = _jinja_env.get_template(template_name)
    return HTMLResponse(tmpl.render(**context))


def _compute_metrics(services):
    """Compute dashboard metrics from services list."""
    total = len(services)
    completed = [s for s in services if s.is_completed]
    met = [s for s in services if s.met_appointment]
    missed = [s for s in services if s.missed_appointment]
    pending = [s for s in services if s.is_pending]

    compliance_pct = (len(met) / len(completed) * 100) if completed else 0

    # Breakdowns
    by_tipo_op = {}
    by_asignacion = {}
    by_punto_cargue = {}

    for s in services:
        # By tipo operacion
        key = s.tipo_operacion or "Sin tipo"
        if key not in by_tipo_op:
            by_tipo_op[key] = {"total": 0, "met": 0, "missed": 0, "pending": 0}
        by_tipo_op[key]["total"] += 1
        if s.met_appointment:
            by_tipo_op[key]["met"] += 1
        elif s.missed_appointment:
            by_tipo_op[key]["missed"] += 1
        elif s.is_pending:
            by_tipo_op[key]["pending"] += 1

        # By asignacion
        key = s.asignacion_servicio or "Sin asignación"
        if key not in by_asignacion:
            by_asignacion[key] = {"total": 0, "met": 0, "missed": 0, "pending": 0}
        by_asignacion[key]["total"] += 1
        if s.met_appointment:
            by_asignacion[key]["met"] += 1
        elif s.missed_appointment:
            by_asignacion[key]["missed"] += 1
        elif s.is_pending:
            by_asignacion[key]["pending"] += 1

        # By punto cargue
        key = s.punto_cargue or "Sin punto"
        if key not in by_punto_cargue:
            by_punto_cargue[key] = {"total": 0, "met": 0, "missed": 0, "pending": 0}
        by_punto_cargue[key]["total"] += 1
        if s.met_appointment:
            by_punto_cargue[key]["met"] += 1
        elif s.missed_appointment:
            by_punto_cargue[key]["missed"] += 1
        elif s.is_pending:
            by_punto_cargue[key]["pending"] += 1

    # Add compliance % to breakdowns
    for breakdown in [by_tipo_op, by_asignacion, by_punto_cargue]:
        for v in breakdown.values():
            completed_count = v["met"] + v["missed"]
            v["compliance_pct"] = round(v["met"] / completed_count * 100, 1) if completed_count else 0

    # Computed compliance (time-based, independent of manual CUMPLIO CITA column)
    computed_completed = [s for s in services if s.computed_met_appointment is not None]
    computed_met = [s for s in services if s.computed_met_appointment is True]
    computed_missed = [s for s in services if s.computed_met_appointment is False]
    computed_compliance_pct = (len(computed_met) / len(computed_completed) * 100) if computed_completed else 0

    # Average delta for completed services
    deltas = [s.arrival_delta_minutes for s in services if s.arrival_delta_minutes is not None]
    avg_delta = round(sum(deltas) / len(deltas), 1) if deltas else 0

    return {
        "total": total,
        "completed": len(completed),
        "met": len(met),
        "missed": len(missed),
        "pending": len(pending),
        "compliance_pct": round(compliance_pct, 1),
        "computed_met": len(computed_met),
        "computed_missed": len(computed_missed),
        "computed_completed": len(computed_completed),
        "computed_compliance_pct": round(computed_compliance_pct, 1),
        "avg_delta_minutes": avg_delta,
        "by_tipo_op": dict(sorted(by_tipo_op.items())),
        "by_asignacion": dict(sorted(by_asignacion.items())),
        "by_punto_cargue": dict(sorted(by_punto_cargue.items())),
    }


def _filter_services(services, fecha=None, tipo_op=None, punto_cargue=None,
                     placa=None, asignacion=None, cumplio=None):
    """Apply filters to services list."""
    filtered = services
    if fecha:
        filtered = [s for s in filtered if fecha in s.fecha]
    if tipo_op:
        filtered = [s for s in filtered if s.tipo_operacion.upper() == tipo_op.upper()]
    if punto_cargue:
        filtered = [s for s in filtered if punto_cargue.upper() in s.punto_cargue.upper()]
    if placa:
        filtered = [s for s in filtered if placa.upper() in s.placa.upper()]
    if asignacion:
        filtered = [s for s in filtered if s.asignacion_servicio.upper() == asignacion.upper()]
    if cumplio:
        if cumplio.upper() in ("SI", "SÍ"):
            filtered = [s for s in filtered if s.met_appointment]
        elif cumplio.upper() == "NO":
            filtered = [s for s in filtered if s.missed_appointment]
        elif cumplio.upper() == "PENDIENTE":
            filtered = [s for s in filtered if s.is_pending]
    return filtered


def _get_filter_options(services):
    """Extract unique filter values from current data."""
    return {
        "tipos_operacion": sorted(set(s.tipo_operacion for s in services if s.tipo_operacion)),
        "puntos_cargue": sorted(set(s.punto_cargue for s in services if s.punto_cargue)),
        "placas": sorted(set(s.placa for s in services if s.placa)),
        "asignaciones": sorted(set(s.asignacion_servicio for s in services if s.asignacion_servicio)),
        "fechas": sorted(set(s.fecha for s in services if s.fecha)),
    }


# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    fecha: str = Query(None),
    tipo_op: str = Query(None),
    punto_cargue: str = Query(None),
    placa: str = Query(None),
    asignacion: str = Query(None),
    cumplio: str = Query(None),
):
    """Main operational dashboard."""
    all_services = _cache.services
    filters = _get_filter_options(all_services)
    services = _filter_services(all_services, fecha, tipo_op, punto_cargue, placa, asignacion, cumplio)
    metrics = _compute_metrics(services)
    incidencias = [s for s in services if s.missed_appointment]

    active_filters = {
        "fecha": fecha or "",
        "tipo_op": tipo_op or "",
        "punto_cargue": punto_cargue or "",
        "placa": placa or "",
        "asignacion": asignacion or "",
        "cumplio": cumplio or "",
    }

    return _render(
        "dashboard.html",
        metrics=metrics,
        services=services,
        incidencias=incidencias,
        filters=filters,
        active_filters=active_filters,
        tipologias=_cache.tipologias,
        last_updated=_cache.last_updated,
        view="operational",
    )


@app.get("/executive", response_class=HTMLResponse)
async def executive_view(request: Request):
    """Executive KPI dashboard."""
    services = _cache.services
    metrics = _compute_metrics(services)

    return _render(
        "executive.html",
        metrics=metrics,
        services=services,
        last_updated=_cache.last_updated,
        view="executive",
    )


@app.get("/client", response_class=HTMLResponse)
async def client_view(request: Request):
    """Client-facing compliance report for Orlando."""
    services = _cache.services
    metrics = _compute_metrics(services)
    incidencias = [s for s in services if s.missed_appointment]

    return _render(
        "client.html",
        metrics=metrics,
        incidencias=incidencias,
        services=services,
        last_updated=_cache.last_updated,
        view="client",
    )


@app.get("/api/services")
async def api_services(
    fecha: str = Query(None),
    tipo_op: str = Query(None),
    punto_cargue: str = Query(None),
    placa: str = Query(None),
    asignacion: str = Query(None),
    cumplio: str = Query(None),
):
    """JSON API for filtered services."""
    services = _filter_services(
        _cache.services, fecha, tipo_op, punto_cargue, placa, asignacion, cumplio
    )
    return {
        "count": len(services),
        "services": [
            {
                "fecha": s.fecha,
                "hora_cargue": s.hora_cargue,
                "punto_cargue": s.punto_cargue,
                "cliente": s.cliente,
                "tipo_operacion": s.tipo_operacion,
                "placa": s.placa,
                "asignacion_servicio": s.asignacion_servicio,
                "punto_entrega": s.punto_entrega,
                "hora_salida": s.hora_salida,
                "fecha_entrega": s.fecha_entrega,
                "cita_entrega": s.cita_entrega,
                "hora_llegada": s.hora_llegada,
                "cumplio_cita": s.cumplio_cita,
                "arrival_delta_minutes": s.arrival_delta_minutes,
                "computed_met_appointment": s.computed_met_appointment,
                "lead_time_delta_minutes": s.lead_time_delta_minutes,
                "observaciones": s.observaciones,
            }
            for s in services
        ],
        "last_updated": _cache.last_updated.isoformat() if _cache.last_updated else None,
    }


@app.get("/api/metrics")
async def api_metrics():
    """JSON API for dashboard metrics."""
    return _compute_metrics(_cache.services)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "services_count": len(_cache.services),
        "last_updated": _cache.last_updated.isoformat() if _cache.last_updated else None,
    }
