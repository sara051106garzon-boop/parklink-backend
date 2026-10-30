# ParkLink — Back-End

API REST del sistema de gestión de parqueaderos **ParkLink**.

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

La suite está organizada en `tests/unit/` (pruebas unitarias puras) y
`tests/integration/` (rutas, CORS y JWT con el `test_client` de Flask).
Guía completa para el equipo: [`tests/README.md`](tests/README.md).

```bash
pytest                  # toda la suite
pytest -m unit          # solo unitarias
pytest -m integration   # solo integración
pytest -v               # detalle de cada prueba
```

## Docker

```bash
docker compose up --build
```

## Repositorios relacionados

- Front-end Flutter: [parklink-app](https://github.com/sara051106garzon-boop/parklink-app)
