# Phase 1: Project Scaffold & Google Sheets Connection - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-31
**Phase:** 01-project-scaffold-google-sheets-connection
**Areas discussed:** Credential Strategy, Project Structure, Env Configuration, Error Handling

---

## Credential Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Copy SA key to this project | Copiar service-account.json a este repo (en secrets/ con .gitignore). Independiente del proyecto Diageo. | ✓ |
| Keep pointing to Diageo | Seguir apuntando al archivo en proceso-tarificacion-diageo. Simple pero crea dependencia entre proyectos. | |
| Base64 env var only | No archivo local — solo GOOGLE_SA_KEY como base64 en .env. Mismo patrón que Render deployment. | |
| You decide | Claude elige la mejor opción según el contexto | |

**User's choice:** Copy SA key to this project
**Notes:** User wants project independence from Diageo. Key stored at `secrets/service-account.json` with `secrets/` in `.gitignore`.

---

## Credential Location

| Option | Description | Selected |
|--------|-------------|----------|
| secrets/ directory | secrets/service-account.json con secrets/ en .gitignore (mismo patrón que Diageo) | ✓ |
| Root .env only | Base64 encoded dentro del .env, sin archivo JSON separado | |
| You decide | Claude elige la ubicación más segura | |

**User's choice:** secrets/ directory

---

## Project Structure

| Option | Description | Selected |
|--------|-------------|----------|
| Current flat layout | app.py + sheets/ + templates/ + static/. Simple, funciona para este tamaño de proyecto. | |
| Domain-based modules | Separar en modules: sheets/ (data), dashboard/ (views+metrics), core/ (config). Más escalable. | |
| FastAPI standard | routers/ + services/ + models/ + templates/. Patrón estándar de FastAPI con separación clara. | ✓ |
| You decide | Claude elige la estructura según la complejidad del proyecto | |

**User's choice:** FastAPI standard layout

---

## Env Configuration

| Option | Description | Selected |
|--------|-------------|----------|
| .env + python-dotenv | Patrón actual — .env con dotenv. Simple, probado, mismo que Diageo. | |
| pydantic Settings | Clase Settings con validación de tipos, valores por defecto, y .env support. Más robusto. | |
| You decide | Claude elige según best practices para FastAPI | ✓ |

**User's choice:** Claude's discretion

| Option | Description | Selected |
|--------|-------------|----------|
| Solo las actuales | GOOGLE_SERVICE_ACCOUNT_FILE, BOMI_SHEET_ID, POLL_INTERVAL_SECONDS — suficiente | |
| Add log level | Agregar LOG_LEVEL para controlar verbosidad en prod vs dev | ✓ |
| Add port + host | Agregar PORT y HOST para configurar uvicorn desde .env | |

**User's choice:** Add LOG_LEVEL

---

## Error Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Crash and exit | Si no puede leer el spreadsheet al inicio, no arranca. Falla rápido, error claro. | ✓ |
| Start with warning | Arrancar sin datos, mostrar banner de error en el dashboard, reintentar en background. | |
| Retry 3 times then crash | Intentar 3 veces con backoff, si falla — crash con error descriptivo. | |

**User's choice:** Crash and exit on startup failure

| Option | Description | Selected |
|--------|-------------|----------|
| Serve stale data silently | Seguir mostrando la última data buena, reintentar en el próximo ciclo. Sin alerta visual. | ✓ |
| Stale data + visual warning | Seguir sirviendo data vieja pero mostrar un banner amarillo: 'Datos desactualizados desde X' | |
| You decide | Claude elige el approach más robusto | |

**User's choice:** Serve stale data silently on runtime polling failures

---

## Claude's Discretion

- Config management approach (pydantic Settings vs plain dotenv)

## Deferred Ideas

None — discussion stayed within phase scope
