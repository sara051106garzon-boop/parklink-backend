# GUÍA DE ESTUDIO: 10 PRUEBAS UNITARIAS PARKLINK (UNIT 014 - 024)

**Objetivo:** Entender cómo se hacen, para qué sirven y explicar línea por línea cada prueba.  
**Tecnologías:** Flask, Flask-JWT-Extended, Flask-CORS, PyTest, Python 3.12  
**Ubicación:** `Back-End/tests/`  
**Fecha:** 27/10/2026

---

## 1) CONFIGURACIÓN COMÚN (conftest.py)

**Ruta:** `Back-End/tests/conftest.py`

```python
# tests/conftest.py
"""
Configuración común para las pruebas unitarias de ParkLink.

Centraliza la preparación de la aplicación Flask y del cliente HTTP para que
cada caso de prueba pueda vivir en su propio archivo sin repetir código.
"""

import sys
from pathlib import Path

import pytest

# Permite ejecutar `pytest` desde la raíz del repositorio o desde Back-End.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import app as app_module


@pytest.fixture(scope="module")
def flask_app():
    """
    Crea la aplicación una sola vez por archivo de prueba.

    SocketIO se configura con async_mode="gevent"; gevent es el motor de
    producción y no interviene en estas pruebas unitarias. Se sustituye
    init_app por un no-op para no levantar un servidor de WebSockets.
    """
    init_app_original = app_module.socketio.init_app
    app_module.socketio.init_app = lambda *args, **kwargs: None
    try:
        aplicacion = app_module.create_app()
    finally:
        app_module.socketio.init_app = init_app_original

    aplicacion.config.update(TESTING=True)
    return aplicacion


@pytest.fixture()
def client(flask_app):
    """Cliente HTTP de Flask para invocar las rutas sin abrir un puerto."""
    return flask_app.test_client()
```

### Explicación línea por línea

| Línea | Explicación |
|---|---|
| `# tests/conftest.py` | Comentario que identifica el archivo. |
| `"""..."""` (docstring) | Describe para qué sirve el archivo: reutilizar fixtures entre tests. |
| `import sys` | Importa módulo para manipular rutas de Python. |
| `from pathlib import Path` | Permite obtener rutas absolutas/relativas de forma moderna. |
| `import pytest` | Framework de pruebas. |
| `BACKEND_DIR = Path(__file__).resolve().parents[1]` | `__file__` es la ruta del conftest; `parents[1]` sube un nivel hasta `Back-End/`. |
| `if str(BACKEND_DIR) not in sys.path: sys.path.insert(0, str(BACKEND_DIR))` | Añade `Back-End/` al `sys.path` para poder hacer `import app`, `from app...` aunque ejecutes pytest desde fuera. |
| `import app as app_module` | Importa el paquete `app` (archivo `app/__init__.py`) con alias. |
| `@pytest.fixture(scope="module")` | Fixture reutilizable por todo el módulo de pruebas. Se crea una vez por archivo de test. |
| `def flask_app():` | Función que devuelve la app Flask configurada para tests. |
| `init_app_original = app_module.socketio.init_app` | Guarda el método original por si acaso. |
| `app_module.socketio.init_app = lambda *args, **kwargs: None` | Reemplaza `init_app` por una función vacía. Evita arrancar el servidor SocketIO (necesita gevent). |
| `try: ... finally:` | Asegura restaurar el método original al finalizar. |
| `aplicacion = app_module.create_app()` | Llama a la función fábrica `create_app()` definida en `app/__init__.py`. |
| `aplicacion.config.update(TESTING=True)` | Activa modo testing de Flask (comportamiento más explícito, menos redirecciones). |
| `return aplicacion` | Devuelve la app para usarla en las pruebas. |
| `@pytest.fixture()` | Fixture sin scope → se crea nuevo por test (o por llamada). |
| `def client(flask_app):` | Recibe el fixture `flask_app` como parámetro (inyección de dependencias de pytest). |
| `return flask_app.test_client()` | `test_client()` permite hacer peticiones HTTP sin levantar un servidor real (`client.get/post/...`). |

**¿Para qué sirve?** Tener una única fuente de verdad para crear la app y el cliente en todas estas pruebas.

---

## 2) UNIT 014 - `tests/test_014_instancias_unicas.py`

**Ruta:** `Back-End/tests/test_014_instancias_unicas.py`

```python
# tests/test_014_instancias_unicas.py
"""UNIT 014 · database.py · Instancias únicas de db, bcrypt y jwt."""

from app import jwt as jwt_desde_app
from app.database import database as database_module
from app.models.usuario import bcrypt as bcrypt_modelos
from app.models.usuario import db as db_modelos


def test_extensiones_db_bcrypt_jwt_son_instancias_unicas():
    """Las extensiones conservan la misma identidad en todos los módulos."""
    # Arrange
    # db y bcrypt se importan desde el modelo; jwt desde la aplicación.

    # Act
    db_es_misma_instancia = db_modelos is database_module.db
    bcrypt_es_misma_instancia = bcrypt_modelos is database_module.bcrypt
    jwt_es_misma_instancia = jwt_desde_app is database_module.jwt

    # Assert
    assert db_es_misma_instancia
    assert bcrypt_es_misma_instancia
    assert jwt_es_misma_instancia
```

### Explicación línea por línea

| Línea | Explicación |
|---|---|
| Docstring | Identifica el caso UNIT 014. |
| `from app import jwt as jwt_desde_app` | Importa `jwt` desde `app/__init__.py`. Ahí se importó desde `app.database.database`. |
| `from app.database import database as database_module` | Importa el módulo `app/database/database.py` completo. |
| `from app.models.usuario import bcrypt as bcrypt_modelos` | Importa `bcrypt` desde `app/models/usuario.py`. El modelo lo importa desde `app.database.database`. |
| `from app.models.usuario import db as db_modelos` | Importa `db` desde `app/models/usuario.py` (también viene de `database.py`). |
| `def test_extensiones_db_bcrypt_jwt_son_instancias_unicas():` | Nombre del test (pytest lo descubre por `test_*`). |
| `"""..."""` | Describe qué valida. |
| `# Arrange` / `# Act` / `# Assert` | Patrón AAA (Arrange-Act-Assert). Aquí Arrange implícito (imports). |
| `db_es_misma_instancia = db_modelos is database_module.db` | `is` compara identidad de objeto (misma instancia en memoria), no igualdad. |
| `bcrypt_es_misma_instancia = bcrypt_modelos is database_module.bcrypt` | Verifica que el `bcrypt` que usa el modelo es el mismo que está en `database.py`. |
| `jwt_es_misma_instancia = jwt_desde_app is database_module.jwt` | Verifica que `jwt` de `app` es el mismo que `database.py`. |
| `assert db_es_misma_instancia` | Si es `True`, pasa. Si `False`, falla (significaría dos instancias distintas). |
| `assert bcrypt_es_misma_instancia` | Ídem. |
| `assert jwt_es_misma_instancia` | Ídem. |

**¿Para qué sirve?** Garantizar que todas las partes usan **la misma instancia** de `SQLAlchemy`, `Bcrypt` y `JWTManager`. Si se crearan instancias separadas, podrían perder configuración o romper la app.

**Referencia:** Ver `app/database/database.py` - ahí se crean `db = SQLAlchemy()`, `bcrypt = Bcrypt()`, `jwt = JWTManager()` **una sola vez**.

---

## 3) UNIT 015 - `tests/test_015_create_app.py`

**Ruta:** `Back-End/tests/test_015_create_app.py`

```python
# tests/test_015_create_app.py
"""UNIT 015 · create_app() · Construcción de la aplicación."""

from datetime import timedelta

from flask import Flask


def test_create_app_devuelve_instancia_flask_configurada(flask_app):
    """create_app() devuelve Flask con JWT configurado y sesión de 8 horas."""
    # Arrange
    aplicacion = flask_app

    # Act
    es_instancia_flask = isinstance(aplicacion, Flask)
    jwt_secret_key = aplicacion.config.get("JWT_SECRET_KEY")
    expiracion = aplicacion.config.get("JWT_ACCESS_TOKEN_EXPIRES")

    # Assert
    assert es_instancia_flask
    assert jwt_secret_key
    assert expiracion == timedelta(hours=8)
```

### Explicación línea por línea

| Línea | Explicación |
|---|---|
| `from datetime import timedelta` | Necesario para comparar `JWT_ACCESS_TOKEN_EXPIRES`. |
| `from flask import Flask` | Clase base para usar `isinstance()`. |
| `def test_create_app_devuelve_instancia_flask_configurada(flask_app):` | Usa fixture `flask_app` del conftest (que ya llama a `create_app()`). |
| `aplicacion = flask_app` | Asigna a variable local (más legible). |
| `es_instancia_flask = isinstance(aplicacion, Flask)` | Verifica que sea una instancia de `Flask`. |
| `jwt_secret_key = aplicacion.config.get("JWT_SECRET_KEY")` | Obtiene la clave JWT desde la configuración. |
| `expiracion = aplicacion.config.get("JWT_ACCESS_TOKEN_EXPIRES")` | Obtiene el tiempo de expiración del token. |
| `assert es_instancia_flask` | Debe ser True. |
| `assert jwt_secret_key` | Debe existir (truthy) - no puede estar vacío. |
| `assert expiracion == timedelta(hours=8)` | Debe ser exactamente 8 horas (coincide con `Config.JWT_ACCESS_TOKEN_EXPIRES`). |

**¿Para qué sirve?** Validar que `create_app()` construye correctamente la app y carga la configuración esperada.

**Referencia:** `app/config/settings.py` línea 23: `JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)`, `app/__init__.py` línea 34: `app.config.from_object(Config)`

---

## 4) UNIT 016 - `tests/test_016_health.py`

**Ruta:** `Back-End/tests/test_016_health.py`

```python
# tests/test_016_health.py
"""UNIT 016 · GET /health · Ruta de salud."""


def test_health_check_responde_online(client):
    """GET /health responde 200 con los datos base del proyecto."""
    # Arrange
    ruta = "/health"

    # Act
    respuesta = client.get(ruta)
    cuerpo = respuesta.get_json()

    # Assert
    assert respuesta.status_code == 200
    assert cuerpo["status"] == "online"
    assert cuerpo["project"] == "ParkLink"
    assert cuerpo["version"] == "1.0.0"
```

### Explicación línea por línea

| Línea | Explicación |
|---|---|
| `def test_health_check_responde_online(client):` | Usa fixture `client` (test_client de Flask). |
| `ruta = "/health"` | Ruta definida en `app/__init__.py`. |
| `respuesta = client.get(ruta)` | Simula petición GET HTTP. No hace llamada real por red. |
| `cuerpo = respuesta.get_json()` | Convierte el JSON de respuesta a diccionario Python. |
| `assert respuesta.status_code == 200` | Código HTTP OK. |
| `assert cuerpo["status"] == "online"` | Debe devolver status online. |
| `assert cuerpo["project"] == "ParkLink"` | Nombre del proyecto. |
| `assert cuerpo["version"] == "1.0.0"` | Versión. |

**¿Para qué sirve?** Verificar que el endpoint de salud funciona y retorna la estructura esperada.

**Referencia:** `app/__init__.py` líneas 119-126:
```python
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "online",
        "project": "ParkLink",
        "websocket": "enabled",
        "version": "1.0.0"
    }), 200
```
*(Nota: en la app hay "websocket": "enabled" pero la prueba solo valida los 3 campos requeridos)*

---

## 5) UNIT 017 - `tests/test_017_blueprints.py`

**Ruta:** `Back-End/tests/test_017_blueprints.py`

```python
# tests/test_017_blueprints.py
"""UNIT 017 · create_app() · Registro de blueprints y prefijos."""


def test_create_app_registra_los_blueprints_esperados(flask_app):
    """Las rutas representativas de cada blueprint quedan registradas."""
    # Arrange
    rutas_esperadas = {
        "/api/auth/login",
        "/api/admin/registrar-usuario",
        "/api/admin/logs",
        "/api/admin/tendencias",
        "/api/vigilante/entrada",
        "/api/usuario/panel",
    }

    # Act
    rutas_registradas = {str(regla) for regla in flask_app.url_map.iter_rules()}

    # Assert
    assert rutas_esperadas.issubset(rutas_registradas)
```

### Explicación línea por línea

| Línea | Explicación |
|---|---|
| `def test_create_app_registra_los_blueprints_esperados(flask_app):` | Usa `flask_app` para inspeccionar el `url_map`. |
| `rutas_esperadas = {...}` | Conjunto con rutas representativas que deben existir. |
| `rutas_registradas = {str(regla) for regla in flask_app.url_map.iter_rules()}` | `url_map` contiene todas las reglas de rutas. `iter_rules()` itera sobre ellas. `str(regla)` convierte a string con el patrón de ruta. Se guarda en un `set`. |
| `assert rutas_esperadas.issubset(rutas_registradas)` | Verifica que **todos** los elementos de `rutas_esperadas` estén en `rutas_registradas` (sin importar el orden). |

**¿Para qué sirve?** Comprobar que los blueprints se registraron correctamente con sus prefijos.

**Referencia:** `app/__init__.py` líneas 95-107:
- `app.register_blueprint(auth_bp, url_prefix="/api/auth")`
- `app.register_blueprint(admin_bp, url_prefix="/api/admin")`
- `app.register_blueprint(logs_bp)` (logs_bp ya tiene `url_prefix="/api/admin"` en `app/routes/logs.py:7`)
- `app.register_blueprint(tendencias_bp)` (tiene prefix en `app/routes/tendencias.py:7`)
- `app.register_blueprint(vigilante_bp, url_prefix="/api/vigilante")`
- `app.register_blueprint(usuario_bp, url_prefix="/api/usuario")` (revisar - en usuario.py línea 22-26 tiene `url_prefix="/api/usuario"`)

---

## 6) UNIT 019 - `tests/test_019_cors_permitido.py`

**Ruta:** `Back-End/tests/test_019_cors_permitido.py`

```python
# tests/test_019_cors_permitido.py
"""UNIT 019 · CORS · Origen permitido http://localhost:5173."""


def test_cors_permite_origen_del_frontend_en_rutas_api(client):
    """El preflight del frontend autorizado recibe las cabeceras CORS."""
    # Arrange
    origen_permitido = "http://localhost:5173"
    cabeceras = {
        "Origin": origen_permitido,
        "Access-Control-Request-Method": "POST",
    }

    # Act
    respuesta = client.options("/api/auth/login", headers=cabeceras)

    # Assert
    assert respuesta.status_code == 200
    assert respuesta.headers.get("Access-Control-Allow-Origin") == origen_permitido
    assert respuesta.headers.get("Access-Control-Allow-Credentials") == "true"
```

### Explicación línea por línea

| Línea | Explicación |
|---|---|
| `origen_permitido = "http://localhost:5173"` | Puerto típico de Vite (frontend). Coincide con configuración CORS. |
| `cabeceras = {"Origin": ..., "Access-Control-Request-Method": "POST"}` | En una petición **preflight OPTIONS**, el navegador envía `Origin` y el método que quiere usar. |
| `respuesta = client.options("/api/auth/login", headers=cabeceras)` | Simula preflight OPTIONS a `/api/auth/login`. |
| `assert respuesta.status_code == 200` | Flask-CORS responde 200 al preflight. |
| `respuesta.headers.get("Access-Control-Allow-Origin") == origen_permitido` | Debe devolver el **mismo origen** que se solicitó (o `*`, pero aquí es origen específico). |
| `assert respuesta.headers.get("Access-Control-Allow-Credentials") == "true"` | Debe permitir credenciales (cookies/headers auth). |

**¿Para qué sirve?** Verificar que el frontend autorizado puede hacer peticiones CORS a las rutas `/api/*`.

**Referencia:** `app/__init__.py` líneas 38-42:
```python
CORS(
    app,
    resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}},
    supports_credentials=True,
)
```

---

## 7) UNIT 020 - `tests/test_020_cors_rechazado.py`

**Ruta:** `Back-End/tests/test_020_cors_rechazado.py`

```python
# tests/test_020_cors_rechazado.py
"""UNIT 020 · CORS · Origen no permitido."""


def test_cors_rechaza_origen_no_autorizado(client):
    """Un origen ajeno no recibe la cabecera Access-Control-Allow-Origin."""
    # Arrange
    origen_no_autorizado = "http://sitio-malicioso.com"
    cabeceras = {
        "Origin": origen_no_autorizado,
        "Access-Control-Request-Method": "POST",
    }

    # Act
    respuesta = client.options("/api/auth/login", headers=cabeceras)

    # Assert
    assert "Access-Control-Allow-Origin" not in respuesta.headers
```

### Explicación línea por línea

| Línea | Explicación |
|---|---|
| `origen_no_autorizado = "http://sitio-malicioso.com"` | Origen no incluido en la lista permitida. |
| Petición OPTIONS igual que antes | Preflight desde origen no autorizado. |
| `assert "Access-Control-Allow-Origin" not in respuesta.headers` | **Clave:** Si el origen NO está permitido, Flask-CORS NO añade esa cabecera. El navegador bloqueará la petición real. |

**¿Para qué sirve?** Probar que CORS bloquea orígenes no autorizados (seguridad básica).

---

## 8) UNIT 021 - `tests/test_021_jwt_sin_token.py`

**Ruta:** `Back-End/tests/test_021_jwt_sin_token.py`

```python
# tests/test_021_jwt_sin_token.py
"""UNIT 021 · jwt.unauthorized_loader · Petición sin token."""


def test_jwt_sin_token_devuelve_401_authorization_required(client):
    """Una ruta protegida sin cabecera Authorization responde 401."""
    # Arrange
    ruta_protegida = "/api/auth/perfil"

    # Act
    respuesta = client.get(ruta_protegida)
    cuerpo = respuesta.get_json()

    # Assert
    assert respuesta.status_code == 401
    assert cuerpo["error"] == "authorization_required"
```

### Explicación línea por línea

| Línea | Explicación |
|---|---|
| `ruta_protegida = "/api/auth/perfil"` | Ruta con `@jwt_required()` (ver `app/routes/auth.py`). |
| `respuesta = client.get(ruta_protegida)` | GET sin `Authorization: Bearer ...` |
| `cuerpo = respuesta.get_json()` | Obtiene JSON del error personalizado. |
| `assert respuesta.status_code == 401` | No autorizado. |
| `assert cuerpo["error"] == "authorization_required"` | Coincide con el loader definido. |

**¿Para qué sirve?** Verificar el manejador personalizado cuando falta el token.

**Referencia:** `app/__init__.py` líneas 73-78:
```python
@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "mensaje": "Se requiere autenticación. No se encontró un token de acceso.",
        "error": "authorization_required"
    }), 401
```

**Ruta protegida:** `app/routes/auth.py` línea 23: `@jwt_required()` en `obtener_perfil()`

---

## 9) UNIT 022 - `tests/test_022_jwt_token_corrupto.py`

**Ruta:** `Back-End/tests/test_022_jwt_token_corrupto.py`

```python
# tests/test_022_jwt_token_corrupto.py
"""UNIT 022 · jwt.invalid_token_loader · Token mal formado."""


def test_jwt_token_corrupto_devuelve_401_invalid_token(client):
    """Un token con estructura inválida responde 401 invalid_token."""
    # Arrange
    cabeceras = {"Authorization": "Bearer abc.def.ghi"}

    # Act
    respuesta = client.get("/api/auth/perfil", headers=cabeceras)
    cuerpo = respuesta.get_json()

    # Assert
    assert respuesta.status_code == 401
    assert cuerpo["error"] == "invalid_token"
```

### Explicación línea por línea

| Línea | Explicación |
|---|---|
| `cabeceras = {"Authorization": "Bearer abc.def.ghi"}` | Token con formato JWT inválido (no tiene 3 partes válidas o firma incorrecta). |
| `client.get("/api/auth/perfil", headers=cabeceras)` | Envía el token corrupto. |
| `assert cuerpo["error"] == "invalid_token"` | Debe usar `invalid_token_loader`. |

**¿Para qué sirve?** Verificar rechazo de tokens malformados.

**Referencia:** `app/__init__.py` líneas 66-71:
```python
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        "mensaje": "Token inválido o corrupto.",
        "error": "invalid_token"
    }), 401
```

---

## 10) UNIT 023 - `tests/test_023_jwt_token_expirado.py`

**Ruta:** `Back-End/tests/test_023_jwt_token_expirado.py`

```python
# tests/test_023_jwt_token_expirado.py
"""UNIT 023 · jwt.expired_token_loader · Token vencido."""

from datetime import timedelta

from flask_jwt_extended import create_access_token


def test_jwt_token_expirado_devuelve_401_token_expired(flask_app, client):
    """Un token emitido con expiración negativa responde 401 token_expired."""
    # Arrange
    with flask_app.app_context():
        token_expirado = create_access_token(
            identity="1",
            expires_delta=timedelta(hours=-1),
        )
    cabeceras = {"Authorization": f"Bearer {token_expirado}"}

    # Act
    respuesta = client.get("/api/auth/perfil", headers=cabeceras)
    cuerpo = respuesta.get_json()

    # Assert
    assert respuesta.status_code == 401
    assert cuerpo["error"] == "token_expired"
```

### Explicación línea por línea

| Línea | Explicación |
|---|---|
| `from datetime import timedelta` | Para crear delta negativo. |
| `from flask_jwt_extended import create_access_token` | Función para crear tokens JWT válidos. |
| `def test_jwt_token_expirado_devuelve_401_token_expired(flask_app, client):` | Necesita `flask_app` para usar `app_context()`. |
| `with flask_app.app_context():` | Algunas operaciones de Flask-JWT-Extended requieren contexto de aplicación. |
| `token_expirado = create_access_token(identity="1", expires_delta=timedelta(hours=-1))` | Crea token que **ya expiró** (hace 1 hora). |
| `cabeceras = {"Authorization": f"Bearer {token_expirado}"}` | Formato correcto: `Bearer <token>`. |
| `respuesta = client.get("/api/auth/perfil", headers=cabeceras)` | Envía token expirado. |
| `assert cuerpo["error"] == "token_expired"` | Debe activar `expired_token_loader`. |

**¿Para qué sirve?** Verificar el manejo de tokens caducados.

**Referencia:** `app/__init__.py` líneas 59-64:
```python
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "mensaje": "El token ha expirado. Inicia sesión nuevamente.",
        "error": "token_expired"
    }), 401
```

---

## 11) UNIT 024 - `tests/test_024_jwt_firma_invalida.py`

**Ruta:** `Back-End/tests/test_024_jwt_firma_invalida.py`

```python
# tests/test_024_jwt_firma_invalida.py
"""UNIT 024 · JWTManager · Firma inválida."""

import jwt as pyjwt


def test_jwt_token_firmado_con_otra_clave_es_rechazado(flask_app, client):
    """Un token forjado con otra clave responde 401 invalid_token."""
    # Arrange
    clave_no_autorizada = "clave-de-prueba-no-autorizada-para-parklink-2026"
    token_forjado = pyjwt.encode(
        {
            "sub": "1",
            "type": "access",
            "iat": 1_700_000_000,
            "exp": 4_000_000_000,
        },
        clave_no_autorizada,
        algorithm="HS256",
    )
    assert clave_no_autorizada != flask_app.config["JWT_SECRET_KEY"]

    # Act
    respuesta = client.get(
        "/api/auth/perfil",
        headers={"Authorization": f"Bearer {token_forjado}"},
    )
    cuerpo = respuesta.get_json()

    # Assert
    assert respuesta.status_code == 401
    assert cuerpo["error"] == "invalid_token"
```

### Explicación línea por línea

| Línea | Explicación |
|---|---|
| `import jwt as pyjwt` | Importa la librería `PyJWT` directamente (instalada). |
| `clave_no_autorizada = "..."` | Clave distinta a la de la app. |
| `token_forjado = pyjwt.encode({...}, clave_no_autorizada, algorithm="HS256")` | Crea un token válido con estructura correcta pero **firmado con otra clave**. |
| `{"sub": "1", "type": "access", "iat": ..., "exp": ...}` | Claims típicos de Flask-JWT-Extended. |
| `assert clave_no_autorizada != flask_app.config["JWT_SECRET_KEY"]` | Verificación defensiva para asegurar que realmente son distintas. |
| `client.get("/api/auth/perfil", headers={"Authorization": f"Bearer {token_forjado}"})` | Envía el token forjado. |
| `assert cuerpo["error"] == "invalid_token"` | Flask-JWT-Extended detecta firma inválida → `invalid_token_loader`. |

**¿Para qué sirve?** Probar seguridad: tokens firmados con clave incorrecta deben ser rechazados.

**Diferencia con UNIT 022:** UNIT 022 envía token **malformado** (no se puede decodificar). UNIT 024 envía token **bien formado pero con firma incorrecta**. Ambos terminan en `invalid_token` en este proyecto.

---

## 12) Código clave del proyecto a estudiar

### `app/__init__.py` (puntos relevantes)

```python
from app.database.database import db, bcrypt, jwt  # Instancias únicas
...
app.config.from_object(Config)  # Carga config
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}}, supports_credentials=True)
db.init_app(app); bcrypt.init_app(app); jwt.init_app(app)
...
@jwt.expired_token_loader / @jwt.invalid_token_loader / @jwt.unauthorized_loader  # Handlers
...
app.register_blueprint(auth_bp, url_prefix="/api/auth")
...
@app.route("/health", methods=["GET"])
```

### `app/database/database.py`
```python
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
```
**Importante:** Solo se crean aquí. Todo lo demás las importa.

### `app/config/settings.py`
```python
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "parklink_jwt_key_cambia_esto_en_produccion")
```

### `app/routes/auth.py`
```python
@auth_bp.route("/perfil", methods=["GET"])
@jwt_required()
def obtener_perfil():
    usuario_id = get_jwt_identity()
    ...
    return jsonify({"usuario": usuario.to_dict()}), 200
```
`/api/auth/perfil` está **protegida** con `@jwt_required()` → dispara los loaders JWT.

---

## Resumen para estudiar

| Test | Tipo | Concepto | Qué valida |
|---|---|---|---|
| 014 | Estructura/Singleton | Identidad de objetos | Mismas instancias `db/bcrypt/jwt` en todo el proyecto |
| 015 | Configuración | `create_app()` | Devuelve `Flask`, tiene `JWT_SECRET_KEY` y `JWT_ACCESS_TOKEN_EXPIRES=8h` |
| 016 | Endpoint público | `/health` | Responde 200 con `status/project/version` |
| 017 | Routing | Blueprints | Se registran rutas con prefijos correctos |
| 019 | Seguridad/CORS | Preflight permitido | Origen autorizado recibe cabeceras CORS + credentials |
| 020 | Seguridad/CORS | Preflight bloqueado | Origen no autorizado **sin** `Access-Control-Allow-Origin` |
| 021 | JWT | Sin token | `unauthorized_loader` → 401 + `authorization_required` |
| 022 | JWT | Token malformado | `invalid_token_loader` → 401 + `invalid_token` |
| 023 | JWT | Token expirado | `expired_token_loader` → 401 + `token_expired` |
| 024 | JWT | Firma inválida | `invalid_token_loader` → 401 + `invalid_token` |

**Patrón usado:** Arrange-Act-Assert (AAA).  
**Técnica:** Caja blanca (según tabla del caso de prueba).  
**Framework:** PyTest con fixtures (`conftest.py`).
