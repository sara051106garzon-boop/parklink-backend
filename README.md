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

Esta sección describe **exactamente** cómo está desplegado el back-end de ParkLink
en AWS EC2 y cómo reproducirlo desde cero. El repositorio implementa **dos
entornos aislados en la misma instancia**:

| Entorno | Disparador habitual | Puerto público | Contenedor web | Base de datos | Ruta en la EC2 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `staging` | push o merge a `main` | `8000` | `parklink-staging-web` | `parklink_staging` | `/home/ubuntu/parklink-staging` |
| `production` | `workflow_dispatch` o tag `v*`¹ | `8001` | `parklink-production-web` | `parklink_production` | `/home/ubuntu/parklink-production` |

> ¹ El job resuelve `production` para un tag `v*`, pero el paso SSH del workflow
> actual se omite en un push de tag. Usa `workflow_dispatch` para producción y
> revisa la nota de precisión en la sección de GitHub Actions.

**Flujo real de una petición y de un despliegue:**

```
GitHub (push a main / tag v* / workflow_dispatch)
   │
   ├─ Job "tests"  → pytest sobre SQLite en memoria  (si falla, no se despliega)
   │
   └─ Job "deploy" → SSH con EC2_SSH_KEY ─────────────────────────────┐
                                                                        │
                                                                        ▼
                                            AWS EC2 · Ubuntu + Docker + Compose
                                            /home/ubuntu/parklink-<entorno>
                                              ├─ proyecto  parklink-<entorno>
                                              ├─ web  parklink-<entorno>-web  :5000
                                              │     └─ host :8000 (staging) / :8001 (production)
                                              ├─ db   parklink-<entorno>-db-1 (mysql:8.0)
                                              │     └─ red interna, SIN puerto público
                                              └─ volumen parklink-<entorno>-db
                                                                        │
Vercel (frontend) ── HTTPS /api/* ── rewrite ───────────────────────────┘
                     https://parklink-app.vercel.app/api/* → http://3.138.221.70:8001/api/*
```

**Dos caminos válidos (se complementan):**

| Camino | Cuándo usarlo | Qué hace |
| :--- | :--- | :--- |
| **Manual** (Pasos 1–5) | Primera instalación, recuperación o depuración | Instala Docker, clona el repo, escribe `.env`, levanta contenedores, migra, siembra y verifica. |
| **Automático** (sección GitHub Actions) | Día a día, staging y producción | GitHub Actions ejecuta `pytest`, entra por SSH, actualiza el código, reescribe `.env`, reconstruye, migra y comprueba `/health`. |

### Qué pieza hace qué (mapa exacto del repositorio)

| Archivo | Rol en el despliegue |
| :--- | :--- |
| `Dockerfile` | Imagen `python:3.11-slim`; instala dependencias del sistema para `mysqlclient`; corre como usuario `appuser`; expone `5000`; arranca **Gunicorn** con `--worker-class gthread --workers 2 --threads 100 --timeout 120 wsgi:app`. |
| `docker-compose.yml` | Define `web` y `db`; publica `${APP_PORT:-5000}:5000`; espera a que MySQL esté `healthy`; usa `env_file: .env`; aísla proyecto, contenedor, red y volumen con el sufijo `PARKLINK_ENV`. |
| `wsgi.py` | Punto de entrada de producción: `app = create_app()`. Es lo que ejecuta Gunicorn dentro del contenedor. |
| `run.py` | Solo desarrollo local (`python run.py`); **no** se usa en EC2. |
| `seed.py` | Crea de forma idempotente `admin@gmail.com` y `guardia1@gmail.com` con hash **Flask-Bcrypt** (`$2b$...`). **No lo ejecuta el workflow**: se corre una vez a mano. |
| `app/config/settings.py` | Lee `.env` con `python-dotenv` (`override=False`, las variables reales del contenedor mandan); normaliza `DATABASE_URL` a PyMySQL + `utf8mb4`; define `CORS_ORIGINS`, `APP_PORT`, `FLASK_DEBUG`, `SECRET_KEY`, `JWT_SECRET_KEY`, `MAIL_*`. |
| `app/__init__.py` | Crea la app, registra blueprints `/api/*`, CORS, SocketIO, Flask-Migrate y la ruta **`GET /health`** que usa el healthcheck. |
| `.github/workflows/deploy.yml` | Pipeline **Despliegue a AWS EC2**: job `tests` (puerta obligatoria) + job `deploy` (SSH a la instancia). |
| `.github/actions/pruebas-parklink/action.yml` | Acción compuesta reutilizada por `tests.yml` y `deploy.yml`: Python 3.12, dependencias, verificación de aislamiento de BD y `pytest -v`. |
| `cargar-secrets.ps1` | Helper de Windows para crear/actualizar los **8 secrets** de cada GitHub Environment (`staging` y `production`). |

### Paso 0 — Requisitos previos

Antes de tocar AWS, ten a mano:

- Una cuenta de AWS con permisos para **EC2**, **Security Groups** y **Elastic IP**.
- El repositorio `sara051106garzon-boop/parklink-backend` en GitHub (es público; el
  servidor lo clona por HTTPS, sin token).
- Un cliente **OpenSSH** (`ssh`) en tu equipo. En Windows 10/11 viene incluido.
- **GitHub CLI** (`gh`) instalado y autenticado si vas a usar `cargar-secrets.ps1`:

  ```powershell
  gh --version
  gh auth login
  gh auth status
  ```

- `ssh-keygen` disponible (viene con OpenSSH) para validar la llave `.pem`.
- Los valores reales que usa este proyecto:

  | Dato | Valor |
  | :--- | :--- |
  | IP pública / Elastic IP de la EC2 | `3.138.221.70` |
  | Usuario SSH | `ubuntu` |
  | Llave privada | `parklink-key.pem` (o el nombre que le hayas dado) |
  | Ruta del repo en la EC2 (staging) | `/home/ubuntu/parklink-staging` |
  | Ruta del repo en la EC2 (production) | `/home/ubuntu/parklink-production` |
  | Puerto staging | `8000` |
  | Puerto production | `8001` |
  | Puerto interno del contenedor | `5000` |
  | Servicio MySQL interno | `db:3306` |

> 💡 Si la IP `3.138.221.70` no es tuya, reemplázala en **toda** la guía. Ese
> valor aparece en los secrets `EC2_HOST`, en el `rewrite` de Vercel del frontend y
> en los ejemplos de `curl`.

### Paso 1 — Crear y configurar la instancia en AWS EC2

**En la consola de AWS:**

1. Entra a **AWS Console → EC2 → Instances → Launch instance**.
2. Configura la instancia:
   - **Name**: `parklink-ec2`.
   - **Application and OS Images (AMI)**: `Ubuntu Server 22.04 LTS` o `24.04 LTS`
     (64-bit x86). El workflow asume el usuario `ubuntu`, propio de estas AMIs.
   - **Instance type**: `t3.small` (2 vCPU / 2 GB, mínimo para Docker + MySQL) o
     `t3.medium` (recomendado si staging y production conviven con tráfico real).
   - **Key pair (login)**: crea uno nuevo (p. ej. `parklink-key`) y **descarga el
     `.pem`**. Guárdalo en un lugar seguro: no podrás descargarlo de nuevo. Esa
     misma llave se carga como secret `EC2_SSH_KEY`.
   - **Storage**: `20–30 GiB` **gp3**. El volumen por defecto de 8 GiB se llena
     rápido con imágenes de Docker, capas de build y el volumen de MySQL.
3. En **Network settings → Edit**, crea o edita el **Security Group** con estas
   reglas de entrada:

   | Tipo | Puerto | Origen | Uso |
   | :--- | :--- | :--- | :--- |
   | SSH | `22` | **Tu IP** (`x.x.x.x/32`) | SSH (tú y/o runners, ver nota) |
   | Custom TCP | `8001` | `0.0.0.0/0` | API producción |
   | Custom TCP | `8000` | `0.0.0.0/0` | API staging (opcional) |
   | MySQL | `3306` | — | **No abrir** |

   > ⚠️ No abras `3306` (MySQL): solo se usa dentro de la red interna de Docker
   > entre `web` y `db`. El `docker-compose.yml` **no publica** ese puerto.
   >
   > 🔐 El puerto `22` no debería quedar en `0.0.0.0/0`. Pero ten en cuenta que
   > **GitHub Actions usa runners hospedados con IPs de salida dinámicas**: si
   > limitas `22` a “Mi IP”, el job `deploy` fallará con `Connection timed out`.
   > Opciones, de más a menos segura:
   >
   > 1. Usar **AWS Systems Manager Session Manager** o un **self-hosted runner**
   >    dentro de la VPC (sin abrir `22` a Internet).
   > 2. Permitir `22` desde los rangos publicados en
   >    `https://api.github.com/meta` (campo `actions`), sabiendo que cambian.
   > 3. Abrir `22` a `0.0.0.0/0` **solo** con autenticación por llave, sin
   >    contraseñas, y con `fail2ban`/límite de intentos.
   >
   > Los puertos `8000`/`8001` sí deben ser alcanzables desde Vercel; sus IPs de
   > salida también son dinámicas, por eso el ejemplo usa `0.0.0.0/0`.
   >
   > 🌐 El backend se sirve por **HTTP**. El navegador no lo nota porque Vercel
   > reenvía `/api/*` servidor-a-servidor, pero el tramo Vercel → EC2 viaja sin
   > TLS. Para cifrarlo, añade un ALB con ACM o un reverse proxy con HTTPS
   > (Nginx/Caddy) y actualiza el `rewrite` del frontend.

   **Salida (egress):** deja la regla por defecto (todo el tráfico). Docker
   necesita descargar imágenes de Docker Hub y paquetes de Ubuntu.

4. Haz clic en **Launch instance** y espera a que el estado sea *Running* y los
   **2/2 status checks** estén en verde.
5. Copia la **Public IPv4 address** de la instancia (ej. `3.138.221.70`).

**Asigna una Elastic IP (muy recomendado):**

La IP pública de una EC2 cambia si la instancia se detiene y se vuelve a iniciar.
Como esa IP está fijada en los secrets `EC2_HOST` y en el `rewrite` de Vercel, asígnala
de forma estable:

1. **EC2 → Elastic IPs → Allocate Elastic IP address → Allocate**.
2. Selecciona la IP → **Actions → Associate Elastic IP address**.
3. Elige la instancia `parklink-ec2` y asóciala.
4. Usa esa IP en todos los pasos siguientes (`3.138.221.70` en esta guía).

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

**Verifica el servidor y Docker** (si Docker aún no está instalado, el comando
fallará: instálalo en el Paso 2 y vuelve a comprobar):

```bash
whoami                     # ubuntu
lsb_release -a             # Ubuntu 22.04 / 24.04
uname -r                   # kernel
free -h                    # memoria (2 GB en t3.small)
df -h                      # disco libre

docker --version
docker compose version
docker ps -a
sudo systemctl status docker --no-pager
```

**Problemas típicos de conexión:**

| Síntoma | Causa | Solución |
| :--- | :--- | :--- |
| `Connection timed out` en el puerto 22 | Security Group sin tu IP | Agrega `SSH 22` con tu IP actual. |
| `Permission denied (publickey)` | Llave equivocada o usuario incorrecto | Usa la llave del Key Pair de esa instancia y el usuario `ubuntu` (no `root`). |
| `UNPROTECTED PRIVATE KEY FILE` | Permisos demasiado abiertos | `chmod 400` / `icacls` como arriba. |
| `docker: command not found` | Docker no instalado | Paso 2. |
| `permission denied ... docker.sock` | Usuario sin grupo `docker` | `sudo usermod -aG docker $USER` y vuelve a entrar por SSH. |

### Paso 2 — Preparar el servidor e instalar Docker y Docker Compose

Conéctate por SSH y ejecuta:

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

# 7. Deja Docker activo al arrancar y verifica
sudo systemctl enable --now docker
docker --version
docker compose version
docker ps -a
```

> Si `docker --version` devuelve un error de permisos, cierra sesión y vuelve a
> entrar por SSH (o usa `sudo docker`). El workflow ejecuta `docker` sin `sudo`,
> así que el usuario `ubuntu` **debe** pertenecer al grupo `docker`.

**Prueba de humo:**

```bash
docker run --rm hello-world
```

**Swap recomendado en `t3.small` (2 GB):**

El build de la imagen (GCC + `mysqlclient`) y MySQL pueden agotar la RAM en la
primera compilación. Un archivo de swap de 2 GB evita que el proceso muera por
OOM:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h
```

**Limpieza de disco (solo cuando haga falta):**

```bash
df -h
docker system df
docker image prune -f      # imágenes huérfanas
docker builder prune -f    # caché de build
# docker system prune -af  # ⚠️ elimina todo lo no usado (contenedores parados, redes, imágenes)
```

### Paso 3 — Clonar el repositorio y configurar `.env`

El workflow **no crea la carpeta**: el script remoto hace `cd "$DEPLOY_PATH"` y
falla si la ruta no existe. Si la carpeta existe pero no tiene `.git`, clona el
repositorio ahí en la primera ejecución. Por eso, antes del primer despliegue
automático debes crear la ruta (o clonar a mano, recomendado la primera vez).
En la EC2:

```bash
sudo mkdir -p /home/ubuntu/parklink-production
sudo chown -R ubuntu:ubuntu /home/ubuntu/parklink-production

git clone https://github.com/sara051106garzon-boop/parklink-backend.git \
  /home/ubuntu/parklink-production
cd /home/ubuntu/parklink-production

cp .env.example .env
nano .env
chmod 600 .env
```

Para **staging**, repite con `/home/ubuntu/parklink-staging`.

> 💡 Si prefieres que el **workflow** haga el `git clone` en su primera ejecución,
> crea solo la carpeta vacía (sin clonar) y asegúrate de que sea escribible:
>
> ```bash
> sudo mkdir -p /home/ubuntu/parklink-production
> sudo chown -R ubuntu:ubuntu /home/ubuntu/parklink-production
> ```
>
> El script remoto detecta que no hay `.git` y clona el ref desplegado. Para el
> primer `seed.py` y las comprobaciones manuales, el clon explícito es más cómodo.

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

Para **staging** cambia `PARKLINK_ENV=staging`, `APP_PORT=8000`,
`parklink_staging` y la ruta de despliegue.

> - `DATABASE_URL` usa el host `db` (servicio interno del compose), **no**
>   `localhost`.
> - `DB_USER` / `DB_PASSWORD` / `DB_NAME` deben **coincidir** con `DATABASE_URL`.
> - Genera los secretos con
>   `python3 -c "import secrets; print(secrets.token_urlsafe(48))"`.
> - **Contraseña de MySQL:** usa solo letras y números (como hace
>   `cargar-secrets.ps1`), o percent-codifica los caracteres especiales. El
>   workflow parte `DATABASE_URL` por el primer `@` y el primer `:`, así que un
>   `@` o `:` sin codificar rompe la derivación de `DB_USER`/`DB_PASSWORD`.
> - `FLASK_DEBUG=0` es obligatorio en producción.
> - `.env` **nunca** se sube al repositorio (está en `.gitignore`) y debe quedar
>   con permisos `600`.

**Qué escribe realmente el workflow en `.env`:**

Cada despliegue automático **reescribe** `DEPLOY_PATH/.env` con exactamente estas
cinco líneas (permisos `600`, `umask 077`):

```dotenv
APP_PORT=<secret APP_PORT>
DATABASE_URL=<secret DATABASE_URL>
SECRET_KEY=<secret SECRET_KEY>
JWT_SECRET_KEY=<secret JWT_SECRET_KEY>
FLASK_DEBUG=0
```

Las credenciales de MySQL (`DB_USER`, `DB_PASSWORD`, `DB_NAME`) y el nombre del
proyecto (`PARKLINK_ENV`, `COMPOSE_PROJECT_NAME`) **no** se escriben en `.env`:
el workflow las exporta en la sesión SSH y Docker Compose las interpola desde el
entorno del shell.

> ⚠️ **Limitación conocida:** el workflow no escribe `CORS_ORIGINS` ni `MAIL_*`.
> Si los necesitas, agrégalos como secrets y añade su `printf` al bloque que
> genera `.env` (o edita `.env` y reinicia los contenedores **solo** hasta el
> siguiente despliegue, porque el workflow lo sobrescribe). Para el frontend
> actual no es imprescindible: el navegador llama al mismo origen de Vercel y el
> proxy evita CORS. `CORS_ORIGINS` solo importa si llamas directo a
> `http://3.138.221.70:8001`.

**Variables que lee `app/config/settings.py`:**

| Variable | Efecto real |
| :--- | :--- |
| `DATABASE_URL` | Tiene prioridad sobre `MYSQL_*`; se normaliza a `mysql+pymysql://...?charset=utf8mb4`. |
| `APP_PORT` | Puerto interno del proceso. En Docker el compose fuerza `5000`; el puerto público es el del host. |
| `FLASK_DEBUG` | `1/true/yes/on` activa debug. En EC2 debe ser `0`. |
| `CORS_ORIGINS` | Lista separada por comas para HTTP y WebSockets. Por defecto `http://localhost:5173,http://127.0.0.1:5173`. |
| `SECRET_KEY` / `JWT_SECRET_KEY` | Firma de sesión y de JWT (8 h de vigencia). |
| `MAIL_*` | Flask-Mailman (opcional). |

### Paso 4 — Levantar contenedores, migrar y sembrar datos

Hazlo una vez para validar la instancia antes de confiar en el pipeline. En la
EC2:

```bash
cd /home/ubuntu/parklink-production

# El compose usa estas variables para nombrar proyecto, red, volumen e imagen.
# Sin ellas, caería en el sufijo "local" y crearía un volumen distinto.
export PARKLINK_ENV=production
export COMPOSE_PROJECT_NAME=parklink-production

# Valida la interpolación antes de construir
docker compose config

# 1. Construye y arranca web + MySQL (aislados por entorno)
docker compose up -d --build

# 2. Revisa que ambos contenedores estén "Up" (y el de MySQL "healthy")
docker ps -a
docker compose ps
```

Debes ver `parklink-production-web` (Up) y `parklink-production-db-1` (Up,
healthy). También se crean:

| Recurso | Nombre exacto |
| :--- | :--- |
| Proyecto Compose | `parklink-production` |
| Imagen | `parklink-production-backend:latest` |
| Red | `parklink-production-net` |
| Volumen MySQL | `parklink-production-db` |

```bash
# 3. Aplica las migraciones Alembic (idempotente; reintenta si MySQL aún arranca)
for intento in $(seq 1 20); do
  docker compose exec -T web flask --app wsgi db upgrade && break
  echo "MySQL aún no acepta conexiones (intento ${intento}/20)..."
  sleep 3
done

# 4. Verifica la conexión real a MySQL (debe imprimir 1)
docker compose exec -T web python -c \
  "from sqlalchemy import text; from app import create_app; from app.database.database import db; app=create_app(); ctx=app.app_context(); ctx.push(); print(db.session.execute(text('SELECT 1')).scalar()); ctx.pop()"

# 5. Carga los usuarios iniciales (admin / vigilante) si no existen
docker compose exec -T web python seed.py
```

> `seed.py` crea `admin@gmail.com` y `guardia1@gmail.com` usando el **setter de
> contraseñas del modelo**, que aplica el hash con **Flask-Bcrypt** (`$2b$...`).
> Es idempotente: si el usuario ya existe, lo salta. **El workflow no ejecuta
> `seed.py`**; hazlo una vez por base de datos nueva.

Comprueba el healthcheck dentro del contenedor y desde el host:

```bash
docker compose exec -T web python -c \
  "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/health').read().decode())"

curl -sS http://127.0.0.1:8001/health
```

Respuesta esperada:

```json
{"project":"ParkLink","status":"online","version":"1.0.0","websocket":"enabled"}
```

Comandos de operación diaria:

```bash
docker compose ps
docker compose logs --tail=100 web
docker compose logs -f web
docker compose restart web
docker compose stop
docker compose start
# ⚠️ docker compose down -v  → elimina el volumen y BORRA la base de datos
```

Para **staging**, repite todo con `PARKLINK_ENV=staging`,
`COMPOSE_PROJECT_NAME=parklink-staging`, `APP_PORT=8000` y
`/home/ubuntu/parklink-staging`.

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

**Verificación del proxy en el frontend:**

El `vercel.json` del repo `parklink-app` debe reenviar `/api/*` a la IP y puerto
correctos:

```json
{ "source": "/api/:path*", "destination": "http://3.138.221.70:8001/api/:path*" }
```

Si cambiaste la Elastic IP o el puerto, actualiza ese `destination`, haz push y
vuelve a desplegar el frontend. En DevTools → Network, las peticiones del
navegador deben ir a `https://parklink-app.vercel.app/api/...`, **nunca** a
`http://3.138.221.70:8001`.

> 🔐 Cambia las contraseñas por defecto de `seed.py` (`AdminPassword123*`,
> `VigilantePassword123*`) tras el primer acceso.

### Despliegue automatizado con GitHub Actions (opcional)

El workflow `.github/workflows/deploy.yml` automatiza los pasos anteriores por
SSH. Es la vía recomendada para el día a día, pero **no sustituye** el primer
`seed.py` ni la creación inicial de los GitHub Environments.

#### Cómo está construido el workflow

- **Nombre:** `Despliegue a AWS EC2`.
- **Permisos:** `contents: read`.
- **Concurrencia:** `deploy-<entorno>`, sin cancelar el despliegue en curso.
- **Entorno resuelto una sola vez** en `env.DEPLOY_ENV`:
  `workflow_dispatch` → input; tag → `production`; push a `main` → `staging`.
- **Job `tests`** (`Pruebas (bloquean el despliegue)`, 15 min):
  `actions/checkout@v4` + `./.github/actions/pruebas-parklink`. Corre sobre
  SQLite en memoria, sin secrets de entorno, y **aborta si detecta
  `DATABASE_URL`**.
- **Job `deploy`** (20 min): `needs: tests`, usa el GitHub Environment resuelto,
  hace checkout en el runner y ejecuta por SSH el script remoto.
- **Resumen:** publica entorno, resultado de las pruebas, estado del job, commit
  y ref en el **GitHub Step Summary**.

**Disparadores reales:**

| Evento | `github.ref_type` | Entorno resuelto | ¿Ejecuta el paso SSH? |
| :--- | :--- | :--- | :--- |
| `push` a `main` | `branch` | `staging` | Sí |
| `push` de tag `v*` | `tag` | `production` | **No** con la condición actual² |
| `workflow_dispatch` en `main` | `branch` | input (`staging`/`production`) | Sí |
| Pull Request | — | — | No: solo corre `tests.yml` |
| Push a otra rama | — | — | No: solo corre `tests.yml` |

> ² **Nota de precisión sobre los tags.** El job resuelve `production` para un
> tag `v*`, pero el paso `Conectar por SSH y desplegar` tiene
> `if: ${{ !(github.ref_type == 'tag' && github.event_name == 'push') }}`. En un
> push de tag esa condición es falsa y el paso se omite: el job termina solo con
> el resumen y **no despliega**. Mientras esa línea siga así, el camino
> garantizado a producción es `workflow_dispatch` con
> `environment: production` (UI o `gh workflow run`). Si quieres que los tags
> desplieguen de verdad, elimina ese `if` del paso (o ajústalo) y pruébalo con un
> tag de prueba; el resto de la guía no cambia.

#### 1. Crear los GitHub Environments

Los secrets del proyecto son **por entorno**, no del repositorio:

1. En GitHub, abre el repo → **Settings → Environments → New environment**.
2. Crea exactamente dos: `staging` y `production` (los nombres deben coincidir
   con los que resuelve el workflow).
3. (Opcional, recomendado) En `production`, activa **Required reviewers**,
   **Wait timer** o restringe **Deployment branches** a `main`.
4. No hace falta configurar nada más: el job `deploy` declara
   `environment: <entorno>` y recibe sus secrets.

#### 2. Configurar los 8 secrets

| Secret | staging | production | Cómo obtenerlo |
| :--- | :--- | :--- | :--- |
| `EC2_HOST` | `3.138.221.70` | `3.138.221.70` | Elastic IP de la instancia. |
| `EC2_USER` | `ubuntu` | `ubuntu` | Usuario de la AMI Ubuntu. |
| `EC2_SSH_KEY` | Contenido del `.pem` | Contenido del `.pem` | El archivo completo, con `-----BEGIN ...-----` y `-----END ...-----`. |
| `APP_PORT` | `8000` | `8001` | Puerto público del host. |
| `DATABASE_URL` | `mysql+pymysql://parklink:<clave>@db:3306/parklink_staging` | `mysql+pymysql://parklink:<clave>@db:3306/parklink_production` | Host `db`, puerto `3306`, base por entorno. |
| `SECRET_KEY` | Aleatoria | Aleatoria | `python -c "import secrets; print(secrets.token_urlsafe(48))"`. |
| `JWT_SECRET_KEY` | Aleatoria | Aleatoria | Igual, **distinta** de `SECRET_KEY`. |
| `DEPLOY_PATH` | `/home/ubuntu/parklink-staging` | `/home/ubuntu/parklink-production` | Carpeta del repo en la EC2. |

> Los 8 son obligatorios: el workflow valida uno por uno y falla con
> `::error::Falta el secret <NOMBRE> en el entorno '<entorno>'` si falta alguno.
> `EC2_SSH_KEY` debe ser la llave privada completa; si copias solo el cuerpo
> (sin las líneas `BEGIN/END`), SSH falla con `Permission denied (publickey)`.

**Opción A — helper automático (Windows):**

`cargar-secrets.ps1` lee la llave del disco, genera las claves aleatorias y define
los 8 secrets en cada entorno. Requisitos: `gh` autenticado y la llave en
`%USERPROFILE%\parklink-key.pem` (o pasarla con `-KeyPath`).

```powershell
powershell -ExecutionPolicy Bypass -File .\cargar-secrets.ps1
```

Ejemplos con parámetros:

```powershell
# Solo staging
powershell -ExecutionPolicy Bypass -File .\cargar-secrets.ps1 -Entornos staging

# Otra ruta de llave / otro repo
powershell -ExecutionPolicy Bypass -File .\cargar-secrets.ps1 `
  -KeyPath "D:\keys\parklink-key.pem" `
  -Repo "sara051106garzon-boop/parklink-backend"

# Rotar SECRET_KEY, JWT_SECRET_KEY y la clave de MySQL (ver advertencia más abajo)
powershell -ExecutionPolicy Bypass -File .\cargar-secrets.ps1 -RotarClaves
```

Qué hace el script, en orden:

1. Localiza `gh.exe` (ruta por defecto o `PATH`) y valida que `ssh-keygen` pueda
   leer la llave.
2. Reutiliza valores de `%USERPROFILE%\.parklink\secrets-<entorno>.env` si
   existen (es idempotente); si no, genera `SECRET_KEY`/`JWT_SECRET_KEY` (base64
   de 48 bytes) y una clave MySQL alfanumérica de 32 caracteres.
3. Construye `DATABASE_URL` con host `db:3306` y base `parklink_<entorno>`.
4. Define los 7 secrets de texto y sube `EC2_SSH_KEY` por **stdin** (nunca aparece
   en la línea de comandos).
5. Guarda el respaldo local con ACL restringida y ejecuta
   `gh secret list --env <entorno>` para verificar.

> ⚠️ **Rotar claves con una base de datos existente.** MySQL solo aplica
> `MYSQL_PASSWORD` al inicializar el volumen. Si cambias la clave de
> `DATABASE_URL` con `-RotarClaves`, el contenedor `db` conserva la anterior y la
> app falla con `Access denied`. Opciones: no rotar la clave de BD, cambiarla
> dentro de MySQL con `ALTER USER`, o recrear el volumen con
> `docker compose down -v` (**borra los datos**; luego migra y siembra de nuevo).

**Opción B — `gh secret set` manual:**

```powershell
# Repite con --env production
gh secret set EC2_HOST    --env staging --body "3.138.221.70"
gh secret set EC2_USER    --env staging --body "ubuntu"
gh secret set APP_PORT    --env staging --body "8000"
gh secret set DEPLOY_PATH --env staging --body "/home/ubuntu/parklink-staging"
gh secret set DATABASE_URL --env staging --body "mysql+pymysql://parklink:CLAVE@db:3306/parklink_staging"
gh secret set SECRET_KEY     --env staging --body (python -c "import secrets; print(secrets.token_urlsafe(48))")
gh secret set JWT_SECRET_KEY --env staging --body (python -c "import secrets; print(secrets.token_urlsafe(48))")

# La llave privada se envía por stdin para no dejarla en el historial
Get-Content -Raw "$env:USERPROFILE\parklink-key.pem" |
  gh secret set EC2_SSH_KEY --env staging

gh secret list --env staging
```

#### 3. Ejecutar el despliegue

**Staging (automático):**

```bash
git add .
git commit -m "mi cambio"
git push origin main
```

El workflow corre `tests` y, si pasa, despliega en `staging` por SSH.

**Producción (manual, camino garantizado):**

1. GitHub → **Actions → Despliegue a AWS EC2 → Run workflow**.
2. Rama: `main`; entorno: `production`; **Run workflow**.
3. O por CLI:

   ```bash
   gh workflow run deploy.yml -f environment=production --ref main
   gh run list --workflow=deploy.yml --limit 5
   gh run watch
   ```

**Tag `v*` (revisar la nota²):**

```bash
git tag v1.0.0
git push origin v1.0.0
```

Con el `if` actual del paso SSH, el tag **no** ejecuta el despliegue. Si corriges
esa condición, este comando desplegará `production`.

**Verificación tras el pipeline:**

```bash
curl -sS http://3.138.221.70:8001/health
ssh -i "ruta\tu-llave.pem" ubuntu@3.138.221.70 \
  "cd /home/ubuntu/parklink-production && git rev-parse --short HEAD && docker compose ps"
```

El commit que imprime `git rev-parse` debe coincidir con el `github.sha` del run.

#### 4. Qué hace exactamente el job de despliegue en la EC2

El runner de GitHub **no** construye la imagen: solo se conecta por SSH y ejecuta
un script remoto (`set -euo pipefail`). En orden:

1. **Valida** que `DEPLOY_ENV` sea `staging` o `production` y que los 8 secrets
   no estén vacíos.
2. **Prepara la llave SSH**: `~/.ssh/ec2_deploy_key` con permisos `600`, añade la
   huella del host con `ssh-keyscan` y conecta con
   `StrictHostKeyChecking=yes -o ConnectTimeout=20`.
3. **Actualiza el código** en `DEPLOY_PATH`:
   - Si hay `.git`: `git fetch --prune --tags origin`, `git fetch origin
     "$GITHUB_REF_NAME"`, `git reset --hard FETCH_HEAD`, `git clean -fd`.
   - Si no hay `.git`: `git init`, agrega `origin`, `fetch --depth=1` del ref y
     `checkout -B "$GITHUB_REF_NAME" FETCH_HEAD`.
4. **Escribe `.env`** con las 5 variables indicadas en el Paso 3, permisos `600`.
5. **Exporta** `COMPOSE_PROJECT_NAME=parklink-<entorno>` y
   `PARKLINK_ENV=<entorno>`; deriva `DB_USER`, `DB_PASSWORD` y `DB_NAME` desde
   `DATABASE_URL` y valida el formato.
6. **Comprueba Docker** (`docker info`) y que exista `docker-compose.yml`;
   detecta `docker compose` (plugin v2) o `docker-compose` (v1).
7. **Reinicia** con `docker compose down --remove-orphans` y luego
   `docker compose up -d --build --remove-orphans`. Antes de levantar, aborta si
   el puerto `${APP_PORT}` ya está publicado por otro contenedor (protege el
   caso staging/production en el mismo host).
8. **Migra** con `docker compose exec -T web flask --app wsgi db upgrade`,
   reintentando hasta 20 veces cada 3 s mientras MySQL arranca.
9. **Verifica la BD** con un `SELECT 1` real.
10. **Espera `/health`** hasta 30 intentos × 3 s (90 s). Si falla, imprime
    `docker compose ps`, el healthcheck de Docker y los últimos 80 logs.
11. **Publica el resumen** en GitHub Step Summary.

> ⚠️ `git reset --hard` + `git clean -fd` descartan cualquier cambio hecho a mano
> en la EC2. No edites código en el servidor: hazlo en una rama y despliega.
>
> ⚠️ `docker compose down` implica una **breve interrupción** del servicio en cada
> despliegue. Para cero downtime haría falta un balanceador o un despliegue
> blue/green (no implementado).

**Lo que el workflow NO hace:**

- No ejecuta `seed.py` (hazlo una vez por base nueva).
- No escribe `CORS_ORIGINS` ni `MAIL_*` en `.env`.
- No publica MySQL en `3306` (correcto: solo red interna).
- No configura TLS ni un dominio para el backend.
- No hace backup de la base de datos antes de migrar (hazlo tú si hay datos
  críticos).

#### 5. Primer despliegue automatizado: checklist

1. La EC2 está **Running**, con Elastic IP `3.138.221.70`.
2. El Security Group permite `22` desde los runners de GitHub (ver Paso 1) y
   `8001`/`8000` según el entorno.
3. `docker --version`, `docker compose version` y `docker run --rm hello-world`
   funcionan sin `sudo` con el usuario `ubuntu`.
4. La carpeta `DEPLOY_PATH` existe y es escribible por `ubuntu` (el workflow no la
   crea; ver Paso 3).
5. Existen los Environments `staging` y `production` con sus **8 secrets**.
6. Ejecuta primero **staging** (`workflow_dispatch` o push a `main`) y revisa el
   run en verde.
7. Verifica `curl http://3.138.221.70:8000/health`.
8. Si la base es nueva, siembra **una vez**:

   ```bash
   ssh -i "ruta\tu-llave.pem" ubuntu@3.138.221.70
   cd /home/ubuntu/parklink-staging
   export PARKLINK_ENV=staging COMPOSE_PROJECT_NAME=parklink-staging
   docker compose exec -T web python seed.py
   ```

9. Repite para **production** y verifica
   `curl http://3.138.221.70:8001/health` y el login.
10. Confirma que el `rewrite` de Vercel apunta a `http://3.138.221.70:8001`.

#### 6. Rollback y operación

**Rollback por CI (recomendado):** revierte el commit con un PR (`main` está
protegida) y deja que el pipeline despliegue de nuevo.

```bash
git checkout -b rollback/<sha>
git revert <sha>
git push origin rollback/<sha>
# Abre un PR a main; al mergear, staging se redespliega solo.
# Cuando el PR esté mergeado, despliega production:
gh workflow run deploy.yml -f environment=production --ref main
```

**Rollback manual de emergencia** (el siguiente deploy de CI lo sobrescribe):

```bash
ssh -i "ruta\tu-llave.pem" ubuntu@3.138.221.70
cd /home/ubuntu/parklink-production
export PARKLINK_ENV=production COMPOSE_PROJECT_NAME=parklink-production

git fetch --all --tags
git reset --hard <commit-anterior>
docker compose up -d --build
docker compose exec -T web flask --app wsgi db upgrade
curl -fsS http://127.0.0.1:8001/health
```

**Backup y restauración de MySQL** (sin exponer credenciales; usa las variables
del propio contenedor):

```bash
cd /home/ubuntu/parklink-production
export PARKLINK_ENV=production COMPOSE_PROJECT_NAME=parklink-production

# Backup
docker compose exec -T db sh -c \
  'exec mysqldump -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"' \
  > "backup-$(date +%F-%H%M).sql"

# Restauración (⚠️ sobrescribe datos)
docker compose exec -T db sh -c \
  'exec mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"' \
  < backup-2026-11-24-1200.sql
```

**Operación diaria:**

```bash
cd /home/ubuntu/parklink-production
export PARKLINK_ENV=production COMPOSE_PROJECT_NAME=parklink-production

docker compose ps
docker compose logs --tail=100 web
docker inspect --format '{{.State.Status}} | {{.State.Health.Status}}' parklink-production-web
git rev-parse --short HEAD
df -h
docker system df
```

> Recuerda exportar `PARKLINK_ENV` y `COMPOSE_PROJECT_NAME` en **cualquier**
> terminal manual. Sin ellas, un `docker compose up` usaría el sufijo `local` y
> crearía un volumen/red distintos (base vacía).

#### 7. Checklist de seguridad

- [ ] `3306` **no** está abierto en el Security Group.
- [ ] `22` está restringido a tu IP y/o a los runners de GitHub (ver Paso 1).
- [ ] La llave `.pem` tiene permisos `400/600` y nunca se commitea.
- [ ] Los 8 secrets viven en los GitHub Environments, no en el código.
- [ ] `.env` está en `.gitignore` y con permisos `600` en la EC2.
- [ ] `FLASK_DEBUG=0` en producción.
- [ ] `SECRET_KEY` y `JWT_SECRET_KEY` son largas, aleatorias y distintas.
- [ ] Las contraseñas de `seed.py` fueron cambiadas tras el primer login.
- [ ] `CORS_ORIGINS` incluye solo el dominio real si llamas directo a la API.
- [ ] Hay backups de MySQL y una alarma de disco/RAM en CloudWatch.
- [ ] El tramo Vercel → EC2 está cifrado (ALB/ACM o reverse proxy HTTPS) si
      manejas datos sensibles.

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
| `::error::Falta el secret <NOMBRE> en el entorno '<entorno>'` | Secret ausente o con otro nombre | Créalo en **Settings → Environments → `<entorno>` → Secrets** (los secrets del repo no sustituyen a los del Environment). |
| `Permission denied (publickey)` desde GitHub Actions | `EC2_SSH_KEY` incompleta o `EC2_USER` incorrecto | Pega el `.pem` completo (con `BEGIN/END`) y usa `ubuntu`. |
| `ssh: connect to host ... port 22: Connection timed out` | Security Group sin la IP del runner o `EC2_HOST` viejo | Habilita `22`, verifica la Elastic IP y actualiza `EC2_HOST`. |
| El job `deploy` aparece como *skipped* | El job `tests` falló o hay un revisor pendiente | Corrige las pruebas; si production tiene *Required reviewers*, apruébalo en el run. |
| Un tag `v*` no despliega producción | Condición `if` del paso SSH en `deploy.yml` | Usa `workflow_dispatch` con `environment: production` (ver nota²). |
| `docker compose` crea `parklink-local-*` o una base vacía | Falta exportar `PARKLINK_ENV`/`COMPOSE_PROJECT_NAME` en la sesión manual | `export PARKLINK_ENV=production COMPOSE_PROJECT_NAME=parklink-production` antes de cualquier `docker compose`. |
| `Access denied` tras `cargar-secrets.ps1 -RotarClaves` | El volumen MySQL conserva la clave anterior | Restaura la clave anterior, cámbiala con `ALTER USER` o recrea el volumen con `docker compose down -v` (⚠️ borra datos). |
| `/health` no responde tras 90 s | Primer build lento, MySQL/migraciones fallando o puerto ocupado | Revisa `docker compose ps` y `docker compose logs --tail=100`; el workflow los imprime al fallar. |
| `no space left on device` | Imágenes/caché de build o volumen lleno | `docker system df`, `docker image prune -f`, `docker builder prune -f`; amplía el EBS si persiste. |
| Cambios manuales en la EC2 desaparecen | El workflow hace `git reset --hard` + `git clean -fd` | No edites en el servidor; haz commit/PR y vuelve a desplegar. |
| `Cannot connect to the Docker daemon` | `ubuntu` no está en el grupo `docker` | `sudo usermod -aG docker $USER`, cierra sesión y vuelve a entrar por SSH. |

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
