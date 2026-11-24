<div align="center">

# ParkLink — Back-End

[![Pruebas](https://github.com/sara051106garzon-boop/parklink-backend/actions/workflows/tests.yml/badge.svg)](https://github.com/sara051106garzon-boop/parklink-backend/actions/workflows/tests.yml)
[![Versión](https://img.shields.io/github/v/release/sara051106garzon-boop/parklink-backend?style=flat&color=2f81f7)](https://github.com/sara051106garzon-boop/parklink-backend/releases)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.x-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![AWS EC2](https://img.shields.io/badge/AWS-EC2-FF9900?logo=amazonaws&logoColor=white)](https://aws.amazon.com/ec2/)
[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-yellow.svg)](LICENSE)

API REST del sistema de gestión de parqueaderos **ParkLink**: control de entrada
y salida de vehículos, cupos, tarifas, usuarios y reportes, con autenticación por
JWT y roles. Consumida por el frontend en Vercel (`https://parklink-app.vercel.app`)
mediante un proxy `/api/*`.

</div>

---

## Stack

| Capa | Tecnología |
| :--- | :--- |
| **Framework** | Flask 3.x + Gunicorn (workers `gthread`) |
| **ORM / migraciones** | SQLAlchemy 2.0 + Flask-Migrate (Alembic) |
| **Autenticación** | JWT (Flask-JWT-Extended) + contraseñas con **bcrypt** (`$2b$`) |
| **Base de datos** | MySQL 8.0 (PyMySQL / mysqlclient) |
| **Tiempo real** | Flask-SocketIO |
| **CORS / Mail** | Flask-Cors · Flask-Mailman |
| **Pruebas** | Pytest (unit / integration / e2e) |
| **Despliegue** | Docker + Docker Compose en AWS EC2, CI/CD con GitHub Actions |

## Arquitectura

```
Vercel (frontend) ── HTTPS /api/* ──▶ AWS EC2 (3.138.221.70)
                                        └─ Docker: parklink-<entorno>-web
                                             └─ Gunicorn :5000 → Flask (wsgi:app)
                                                  └─ MySQL 8.0 (parklink-<entorno>-db-1)
```

- `staging` corre en el puerto `8000` y `production` en el `8001`, cada uno con
  su propio contenedor, red, volumen y base de datos **aislados**.
- El frontend en Vercel reenvía `/api/*` al back-end mediante un `rewrite`, por
  lo que el navegador nunca llama directo a `http://...:8001` (sin Mixed Content
  ni CORS).

## Estructura

```
app/
├── config/        Configuración y variables de entorno
├── controllers/   Lógica de los endpoints
├── database/      Instancias de SQLAlchemy, Bcrypt y JWT
├── middlewares/   Validación de roles
├── models/        Modelos de datos
├── routes/        Blueprints por módulo
└── services/      Lógica de negocio
migrations/        Migraciones Alembic
tests/             Pruebas unitarias, de integración y e2e
docs/              Arquitectura, referencia de la API y guías
Dockerfile         Imagen de producción (Gunicorn)
docker-compose.yml Servicios web + MySQL por entorno
run.py             Arranque de desarrollo local
wsgi.py            Entrada de producción (Gunicorn)
seed.py            Carga de usuarios iniciales
cargar-secrets.ps1 Carga de secretos en GitHub Environments
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
python seed.py               # datos de prueba (admin / vigilante)
python run.py
```

La API queda disponible en `http://127.0.0.1:5000` (o `http://127.0.0.1:5000/health`).

## Variables de entorno (`.env`)

La configuración se centraliza en `app/config/settings.py`, que lee las variables
del entorno (`.env` con `python-dotenv`, o inyectadas por Docker). Copia
`.env.example` a `.env` y ajusta los valores; **nunca** subas el `.env` real.

| Variable | Descripción |
| :--- | :--- |
| `PARKLINK_ENV` | Entorno: `staging`, `production` o `local` (sufijo de contenedores/redes). |
| `APP_PORT` | Puerto público del host: `8000` (staging) / `8001` (production). El contenedor escucha en `5000`. |
| `DATABASE_URL` | `mysql+pymysql://usuario:clave@db:3306/parklink_production` (host `db` = servicio interno). |
| `DB_USER` / `DB_PASSWORD` / `DB_NAME` | Credenciales del contenedor MySQL; deben coincidir con `DATABASE_URL`. |
| `SECRET_KEY` / `JWT_SECRET_KEY` | Claves secretas de Flask y JWT (cadenas largas y aleatorias). |
| `FLASK_DEBUG` | `0` en producción. |
| `CORS_ORIGINS` | Orígenes permitidos (separados por coma), p. ej. `https://parklink-app.vercel.app`. |
| `MAIL_*` | Configuración de Flask-Mailman (opcional). |

Genera valores seguros:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"   # SECRET_KEY / JWT_SECRET_KEY
openssl rand -hex 16                                            # clave de MySQL
```

## Despliegue en AWS EC2 (paso a paso)

### Paso 1 — Crear y configurar la instancia en AWS EC2

**En la consola de AWS:**

1. Entra a **AWS Console → EC2 → Instances → Launch instance**.
2. Configura la instancia:
   - **Name**: `parklink-ec2`.
   - **Application and OS Images (AMI)**: `Ubuntu Server 22.04 LTS` o `24.04 LTS`
     (64-bit x86).
   - **Instance type**: `t3.small` (mínimo para Docker + MySQL) o `t3.medium`.
   - **Key pair (login)**: crea uno nuevo (p. ej. `parklink-key`) y **descarga el
     `.pem`**. Guárdalo en un lugar seguro: no podrás descargarlo de nuevo.
3. En **Network settings → Edit**, crea o edita el **Security Group** con estas
   reglas de entrada:

   | Tipo | Puerto | Origen | Uso |
   | :--- | :--- | :--- | :--- |
   | SSH | `22` | Tu IP | Conexión remota |
   | Custom TCP | `8001` | `0.0.0.0/0` | API producción |
   | Custom TCP | `8000` | `0.0.0.0/0` | API staging (opcional) |

   > ⚠️ No abras `3306` (MySQL): solo se usa dentro de la red interna de Docker
   > entre `web` y `db`.

4. Haz clic en **Launch instance** y espera a que el estado sea *Running*.
5. Copia la **Public IPv4 address** de la instancia (ej. `3.138.221.70`).

**Desde tu terminal (PowerShell / bash):**

```bash
ssh -i "ruta\tu-llave.pem" ubuntu@3.138.221.70
```

- En Linux/macOS ajusta permisos antes de conectar:

  ```bash
  chmod 400 tu-llave.pem
  ```

- En Windows (PowerShell), con OpenSSH no suele ser obligatorio, pero puedes
  restringir los permisos de la llave:

  ```powershell
  icacls .\tu-llave.pem /inheritance:r /grant:r "$env:USERNAME:F"
  ```

- La primera vez te pedirá confirmar la huella del servidor (`yes/no`): escribe
  `yes`.

### Paso 2 — Preparar el servidor e instalar Docker y Docker Compose

```bash
# 1. Actualiza el sistema
sudo apt-get update && sudo apt-get upgrade -y

# 2. Instala dependencias para el repositorio de Docker
sudo apt-get install -y ca-certificates curl gnupg

# 3. Agrega la clave GPG oficial de Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# 4. Agrega el repositorio de Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. Instala Docker Engine y el plugin de Docker Compose
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

# 6. Agrega tu usuario al grupo docker (para no usar sudo en cada comando)
sudo usermod -aG docker $USER
newgrp docker

# 7. Verifica
docker --version
docker compose version
```

> Si `docker --version` devuelve un error de permisos, cierra sesión y vuelve a
> entrar por SSH (o usa `sudo docker`).

### Paso 3 — Clonar el repositorio y configurar `.env`

```bash
git clone https://github.com/sara051106garzon-boop/parklink-backend.git
cd parklink-backend
cp .env.example .env
nano .env
chmod 600 .env
```

Completa **todas** las variables en `.env`. Ejemplo para **production**:

```dotenv
# Entorno y puerto
PARKLINK_ENV=production
APP_PORT=8001

# MySQL (host interno "db")
DATABASE_URL=mysql+pymysql://parklink:CLAVE_SEGURA@db:3306/parklink_production
DB_USER=parklink
DB_PASSWORD=CLAVE_SEGURA
DB_NAME=parklink_production

# Seguridad
SECRET_KEY=<clave-larga-aleatoria>
JWT_SECRET_KEY=<clave-larga-aleatoria>
FLASK_DEBUG=0

# CORS y correo (correo opcional)
CORS_ORIGINS=https://parklink-app.vercel.app
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
MAIL_USERNAME=
MAIL_PASSWORD=
```

> - `DATABASE_URL` usa el host `db` (servicio interno del compose), **no**
>   `localhost`.
> - `DB_USER` / `DB_PASSWORD` / `DB_NAME` deben **coincidir** con `DATABASE_URL`.
> - Genera los secretos con
>   `python3 -c "import secrets; print(secrets.token_urlsafe(48))"`.

### Paso 4 — Levantar contenedores, migrar y sembrar datos

```bash
export PARKLINK_ENV=production
export COMPOSE_PROJECT_NAME=parklink-production

# 1. Construye y arranca web + MySQL (aislados por entorno)
docker compose up -d --build

# 2. Revisa que ambos contenedores estén "Up" (y el de MySQL "healthy")
docker ps -a
docker compose ps
```

Debes ver `parklink-production-web` (Up) y `parklink-production-db-1` (Up,
healthy).

```bash
# 3. Aplica las migraciones Alembic (idempotente; reintenta si MySQL aún arranca)
docker compose exec web flask --app wsgi db upgrade

# 4. Verifica la conexión real a MySQL (debe imprimir 1)
docker compose exec web python -c \
  "from sqlalchemy import text; from app import create_app; from app.database.database import db; app=create_app(); ctx=app.app_context(); ctx.push(); print(db.session.execute(text('SELECT 1')).scalar()); ctx.pop()"

# 5. Carga los usuarios iniciales (admin / vigilante) si no existen
docker compose exec web python seed.py
```

> `seed.py` crea `admin@gmail.com` y `guardia1@gmail.com` usando el **setter de
> contraseñas del modelo**, que aplica el hash con **Flask-Bcrypt** (`$2b$...`).

### Paso 5 — Verificar el despliegue y la conexión con Vercel

```bash
# 1. Health check local (en la instancia) y público (desde tu máquina)
curl http://127.0.0.1:8001/health
curl http://3.138.221.70:8001/health

# 2. Login directo al backend (credenciales sembradas por seed.py)
curl -i -X POST http://127.0.0.1:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"correo":"admin@gmail.com","password":"AdminPassword123*"}'

# 3. Login a través del proxy de Vercel (como lo hace el frontend)
curl -i -X POST https://parklink-app.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"correo":"admin@gmail.com","password":"AdminPassword123*"}'

# 4. Logs del backend y de la base de datos
docker logs --tail 80 parklink-production-web
docker logs --tail 80 parklink-production-db-1
```

Debes obtener `200` con `access_token`/`token` y `usuario.rol`. Abre
`https://parklink-app.vercel.app`, inicia sesión y confirma que el panel carga
sin errores de Mixed Content, CORS ni `500`.

> 🔐 Cambia las contraseñas por defecto de `seed.py` (`AdminPassword123*`,
> `VigilantePassword123*`) tras el primer acceso.

### Despliegue automatizado con GitHub Actions (opcional)

El workflow `.github/workflows/deploy.yml` automatiza los pasos anteriores por
SSH:

- **Push a `main`** → despliega `staging`.
- **Tag `v*`** → despliega `production`.
- **`workflow_dispatch`** → eliges el entorno.

Primero corre `pytest` (puerta de despliegue) y luego, por SSH, actualiza el
código, escribe el `.env`, levanta Docker, migra y verifica `/health`.

Configura los **8 secrets** en GitHub (Environment `staging`/`production`):

| Secret | Descripción |
| :--- | :--- |
| `EC2_HOST` | IP pública de la instancia (`3.138.221.70`). |
| `EC2_USER` | Usuario SSH (`ubuntu`). |
| `EC2_SSH_KEY` | Llave privada `.pem` completa. |
| `APP_PORT` | `8000` (staging) / `8001` (production). |
| `DATABASE_URL` | `mysql+pymysql://usuario:clave@db:3306/parklink_<entorno>`. |
| `SECRET_KEY` / `JWT_SECRET_KEY` | Claves aleatorias. |
| `DEPLOY_PATH` | Ruta en el servidor, p. ej. `/home/ubuntu/parklink-production`. |

Puedes cargarlos con el helper (Windows + GitHub CLI):

```powershell
powershell -ExecutionPolicy Bypass -File .\cargar-secrets.ps1
```

## Contraseñas: bcrypt (`$2b$...`)

Las contraseñas se cifran con **Flask-Bcrypt** (`bcrypt`), no con el hash por
defecto de Werkzeug (`scrypt`/`pbkdf2`). El setter del modelo
`Usuario.password` usa `bcrypt.generate_password_hash` y el login usa
`bcrypt.check_password_hash`.

- Un hash válido empieza por `$2b$` (o `$2a$`).
- Si en el login aparece **`ValueError: Invalid salt`**, es porque el hash guardado
  **no es bcrypt** (por ejemplo, fue generado con `scrypt`). Solución: regenera la
  contraseña con bcrypt o re-sembra la base:

  ```python
  from app import create_app
  from app.database.database import bcrypt
  app = create_app()
  with app.app_context():
      print(bcrypt.generate_password_hash("TuClaveSegura123*").decode())
  ```

## Pruebas

```bash
pytest                  # toda la suite
pytest -m unit          # solo unitarias
pytest -m integration   # solo integración
pytest -m e2e           # extremo a extremo
pytest -v               # detalle de cada prueba
```

Las pruebas corren sobre **SQLite en memoria** y bloquean cualquier conexión real
a MySQL (no tocan staging ni production). Guía completa: [`tests/README.md`](tests/README.md).

## Flujo de trabajo con Git

`main` está **protegida**: todo entra por Pull Request y solo se mergea si las
pruebas automáticas pasan.

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

```bash
git checkout diego_DEV
git pull origin diego_DEV
# ... trabaja ...
git add . && git commit -m "Agrega pruebas de validación de placas"
git push origin diego_DEV
# En GitHub: abre Pull Request de diego_DEV → main
```

## Solución de problemas

| Síntoma | Causa probable | Solución |
| :--- | :--- | :--- |
| `ValueError: Invalid salt` al iniciar sesión | Hash guardado no es bcrypt (p. ej. `scrypt`) | Regenera la contraseña con `bcrypt` o re-sembra con `python seed.py`. |
| `ERROR 1045 (28000): Access denied for user ...` | Credenciales de MySQL no coinciden o el volumen tiene datos viejos | Verifica `DB_USER`/`DB_PASSWORD` frente a `DATABASE_URL`; si vienen de un despliegue anterior, recrea el volumen con `docker compose down -v` (⚠️ borra datos). |
| `ERROR 2003 / Can't connect to MySQL server on 'db'` | MySQL aún no está listo o el host es incorrecto | Espera el healthcheck y reintenta las migraciones; el host debe ser `db`. |
| `curl /health` no responde | Contenedor caído o puerto mal mapeado | `docker ps -a` y `docker compose logs -f web`. |
| Error de conexión a MySQL | Credenciales/host de `DATABASE_URL` | El host debe ser `db` y coincidir con `DB_USER`/`DB_PASSWORD`/`DB_NAME`. |
| Migraciones no aplican | MySQL aún arrancando | Reintenta `docker compose exec web flask --app wsgi db upgrade`. |
| `El puerto ya está en uso` | Otro entorno usa el mismo `APP_PORT` | Asigna un `APP_PORT` distinto por entorno. |
| Error de CORS desde el navegador | Origen no listado | Agrega el dominio a `CORS_ORIGINS` (o usa el proxy de Vercel). |
| `Permission denied` con Docker | Usuario sin grupo `docker` | `sudo usermod -aG docker $USER` y `newgrp docker`. |
| Login `401`/`403` | Credenciales o cuenta inactiva | Revisa el `mensaje` de la respuesta y las cuentas de `seed.py`. |

## Repositorios relacionados

- Front-end Flutter: [parklink-app](https://github.com/sara051106garzon-boop/parklink-app)

## Documentación

- [Arquitectura del sistema](docs/ARQUITECTURA.md) — capas, modelo de datos y flujos.
- [Referencia de la API](docs/API.md) — los 52 endpoints, roles y códigos de respuesta.
- [Guía de estudio: las 10 pruebas unitarias](docs/GUIA_ESTUDIO_10_PRUEBAS_UNITARIAS_PARKLINK.md).
- [Guía de pruebas para el equipo](tests/README.md) — estructura, numeración y convenciones.

## Autor

**Sara Garzón** · [github.com/sara051106garzon-boop](https://github.com/sara051106garzon-boop)

## Licencia

Este proyecto está bajo la licencia [MIT](LICENSE).
