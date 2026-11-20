# app/config/settings.py
"""
ParkLink - Configuración centralizada de la aplicación.

Carga variables de entorno desde el archivo .env (python-dotenv),
pero SIEMPRE respeta las variables que ya existan en el entorno real
(por ejemplo, el .env inyectado por Docker en staging/production).
Si no existe ninguna, usa valores por defecto seguros para desarrollo local con XAMPP.
"""

import os
from datetime import timedelta
from urllib.parse import parse_qsl, quote, unquote, urlsplit

from dotenv import load_dotenv

# Carga el archivo .env ubicado junto a este archivo (o en la raíz del proyecto).
# override=False: las variables del entorno (Docker, GitHub Actions, SO) mandan.
load_dotenv(override=False)


def _texto_entorno(nombre, defecto=None):
    """Devuelve la variable de entorno sin espacios sobrantes (o el valor por defecto)."""
    valor = os.getenv(nombre)
    if valor is None:
        return defecto
    valor = valor.strip()
    return valor if valor else defecto


def normalizar_database_url(url):
    """
    Normaliza una URI de base de datos para SQLAlchemy + PyMySQL.

    - ``mysql://...`` y ``mysql+pymysql://...`` se aceptan igual.
    - Se eliminan los parámetros de query que no entiende PyMySQL
      (``ssl-mode``, ``charset``...) y se conservan los demás.
    - Se garantiza ``charset=utf8mb4``.
    - Las contraseñas con caracteres especiales se codifican (percent-encoding).

    Si la cadena no tiene un formato reconocido (no es un ``*://``), se
    devuelve tal cual para no romper configuraciones especiales (SQLite, etc.).
    """
    url = (url or "").strip()
    if not url or "://" not in url:
        return url

    # El driver debe ser PyMySQL (el que está en requirements.txt).
    if url.startswith("mysql://"):
        url = "mysql+pymysql://" + url[len("mysql://"):]
    elif url.startswith("mysql+mysqldb://"):
        url = "mysql+pymysql://" + url[len("mysql+mysqldb://"):]

    partes = urlsplit(url)
    if not partes.scheme.startswith("mysql"):
        return url

    # Credenciales: codificar solo la contraseña (el usuario normalmente no lo necesita).
    usuario = partes.username
    contrasena = partes.password
    if usuario is not None and contrasena is not None:
        netloc = f"{quote(unquote(usuario), safe='')}:{quote(unquote(contrasena), safe='')}"
        if partes.hostname:
            netloc += f"@{partes.hostname}"
            if partes.port:
                netloc += f":{partes.port}"
        partes = partes._replace(netloc=netloc)

    # Parámetros de conexión compatibles con PyMySQL.
    parametros = [(clave, valor) for clave, valor in parse_qsl(partes.query, keep_blank_values=True)]
    parametros = [(clave, valor) for clave, valor in parametros if clave not in {"ssl-mode", "charset"}]
    parametros.append(("charset", "utf8mb4"))

    return partes._replace(query="&".join(f"{clave}={valor}" for clave, valor in parametros)).geturl()


class Config:
    # ── Claves secretas ───────────────────────────────────────────────────────
    SECRET_KEY = _texto_entorno("SECRET_KEY", "parklink_secret_key_cambia_esto_en_produccion")
    JWT_SECRET_KEY = _texto_entorno("JWT_SECRET_KEY", "parklink_jwt_key_cambia_esto_en_produccion")

    # Tiempo de vida del token JWT (8 horas de sesión de trabajo)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

    # ── Puerto de la aplicación ───────────────────────────────────────────────
    # Puerto interno del contenedor/proceso. En Docker la aplicación escucha
    # SIEMPRE en 5000 y el puerto público se expone con APP_PORT.
    APP_PORT = int(_texto_entorno("APP_PORT", "5000"))

    # ── Modo de ejecución ─────────────────────────────────────────────────────
    # FLASK_DEBUG="1" activa el modo desarrollo; en despliegues debe quedar vacío.
    DEBUG = _texto_entorno("FLASK_DEBUG", "0") in {"1", "true", "True", "yes", "on"}

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Orígenes permitidos para HTTP y WebSockets (separados por comas).
    # En despliegues se configura con el dominio del front-end.
    CORS_ORIGINS = [
        origen.strip()
        for origen in _texto_entorno(
            "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origen.strip()
    ]

    # ── Conexión MySQL / XAMPP ────────────────────────────────────────────────
    MYSQL_USER     = _texto_entorno("MYSQL_USER",     "root")
    MYSQL_PASSWORD = _texto_entorno("MYSQL_PASSWORD", "")        # Sin contraseña en XAMPP por defecto
    MYSQL_HOST     = _texto_entorno("MYSQL_HOST",     "localhost")
    MYSQL_PORT     = _texto_entorno("MYSQL_PORT",     "3306")
    MYSQL_DATABASE = _texto_entorno("MYSQL_DATABASE", "parklink")

    # URI de SQLAlchemy con el driver PyMySQL.
    # Prioridad:
    #   1. DATABASE_URL (usada en staging/production; Aiven, RDS, PlanetScale...).
    #   2. Variables MYSQL_* por separado (desarrollo local con XAMPP).
    DATABASE_URL = _texto_entorno("DATABASE_URL")

    SQLALCHEMY_DATABASE_URI = normalizar_database_url(DATABASE_URL) if DATABASE_URL else (
        f"mysql+pymysql://{quote(MYSQL_USER, safe='')}:{quote(MYSQL_PASSWORD, safe='')}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        "?charset=utf8mb4"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Opciones del pool de conexiones ──────────────────────────────────────
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
        "pool_size": 5,
        "max_overflow": 10,
        "connect_args": {
            "connect_timeout": 10,
        },
    }

    # ── Configuración para Flask-Mailman (Servicio de Mensajería) ──────────────
    MAIL_SERVER   = _texto_entorno("MAIL_SERVER",   "smtp.gmail.com")
    MAIL_PORT     = int(_texto_entorno("MAIL_PORT", "465"))
    MAIL_USE_TLS  = False  # 💥 Lo dejamos quemado en False para que no choque nunca
    MAIL_USE_SSL  = True   # 💥 Forzamos que use SSL para el puerto 465
    MAIL_USERNAME = _texto_entorno("MAIL_USERNAME")
    MAIL_PASSWORD = _texto_entorno("MAIL_PASSWORD")

    # ── Configuración de roles por correo ────────────────────────────────────
    EMAIL_VIGILANTE_DOMINIO = _texto_entorno("EMAIL_VIGILANTE_DOMINIO", "guardia1@gmail.com")

    EMAIL_ADMIN_EXACTOS = [
        correo.strip().lower()
        for correo in _texto_entorno("ADMIN_EMAILS", "admin@gmail.com").split(",")
        if correo.strip()
    ]
