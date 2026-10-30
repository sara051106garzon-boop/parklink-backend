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
