# ParkLink — Back-End

[![Pruebas](https://github.com/sara051106garzon-boop/parklink-backend/actions/workflows/tests.yml/badge.svg)](https://github.com/sara051106garzon-boop/parklink-backend/actions/workflows/tests.yml)
[![Versión](https://img.shields.io/github/v/release/sara051106garzon-boop/parklink-backend?style=flat&color=2f81f7)](https://github.com/sara051106garzon-boop/parklink-backend/releases)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.x-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-yellow.svg)](LICENSE)

API REST del sistema de gestión de parqueaderos **ParkLink**: control de entrada y
salida de vehículos, cupos, tarifas, usuarios y reportes, con autenticación por JWT
y roles.

## Stack

- **Flask** — framework web
- **SQLAlchemy + Flask-Migrate (Alembic)** — ORM y migraciones
- **JWT** — autenticación y control de roles
- **Pytest** — pruebas unitarias
- **Docker / docker-compose** — despliegue

## Estructura

```
app/
├── config/        Configuración y variables de entorno
├── controllers/   Lógica de los endpoints
├── database/      Conexión e inicialización de la BD
├── middlewares/   Validación de roles
├── models/        Modelos de datos
├── routes/        Blueprints por módulo
└── services/      Lógica de negocio
migrations/        Migraciones Alembic
tests/             Pruebas unitarias
run.py             Punto de entrada
seed.py            Carga de datos de prueba
```

## Módulos de la API

`auth` · `usuario` · `admin` · `vigilante` · `accesos` · `celdas` ·
`reservas` · `alertas` · `kpis` · `tendencias` · `logs` · `reportes` ·
`configuraciones`

## Instalación local

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python seed.py               # datos de prueba
python run.py
```

La API queda disponible en `http://127.0.0.1:5000`.

## Pruebas

Cada integrante tiene su carpeta en `tests/<persona>/`, con `unit/` (pruebas
unitarias puras) e `integration/` (rutas, CORS y JWT con el `test_client` de
Flask). Guía completa para el equipo: [`tests/README.md`](tests/README.md).

```bash
pytest                  # toda la suite
pytest -m unit          # solo unitarias
pytest -m integration   # solo integración
pytest -v               # detalle de cada prueba
```

## Flujo de trabajo con Git

`main` está **protegida**: no se puede hacer push directo. Todo entra por Pull
Request y solo se puede mergear si las pruebas automáticas pasan.

```
rama personal  →  Pull Request  →  GitHub Actions (pytest)  →  merge a main
```

### Ramas por integrante

| Integrante | Rama |
|---|---|
| Sara | `sara_DEV` |
| Diego | `diego_DEV` |
| Andrés | `andres_DEV` |
| Nicole | `nicole_DEV` |

### Pasos

```bash
# 1. Ubicarse en tu rama
git checkout diego_DEV
git pull origin diego_DEV

# 2. Trabajar y subir
git add .
git commit -m "Agrega pruebas de validación de placas"
git push origin diego_DEV

# 3. En GitHub: abrir Pull Request de diego_DEV → main
```

El PR queda bloqueado hasta que el check **`pytest`** termine en verde. Si
alguna prueba falla, el botón de merge se desactiva.

## Integración continua

Workflow: [`.github/workflows/tests.yml`](.github/workflows/tests.yml)

Se dispara en **cada push a cualquier rama** y en **cada Pull Request hacia
`main`**. Ejecuta:

1. `python -c "import app"` — verifica que la aplicación importa.
2. `pytest -v` — corre toda la suite del equipo.

Si algo falla, el PR no se puede mergear.

## Docker

```bash
docker compose up --build
```

## Repositorios relacionados

- Front-end Flutter: [parklink-app](https://github.com/sara051106garzon-boop/parklink-app)

## Documentación

- [Arquitectura del sistema](docs/ARQUITECTURA.md) — diagramas de capas, modelo de datos y flujos.
- [Referencia de la API](docs/API.md) — los 52 endpoints, roles y códigos de respuesta.
- [Guía de estudio: las 10 pruebas unitarias](docs/GUIA_ESTUDIO_10_PRUEBAS_UNITARIAS_PARKLINK.md) — explica prueba por prueba qué se valida, por qué importa y cómo se ejecuta.
- [Guía de pruebas para el equipo](tests/README.md) — estructura de carpetas, numeración y convenciones.

## Autor

**Sara Garzón** · [github.com/sara051106garzon-boop](https://github.com/sara051106garzon-boop)

## Licencia

Este proyecto está bajo la licencia [MIT](LICENSE).
