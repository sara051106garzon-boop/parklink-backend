# Pruebas — ParkLink Back-End

Guía para el equipo. Cada integrante tiene **su propia carpeta** y dentro de
ella separa sus pruebas en `unit/`, `integration/` y `e2e/`.

## Estructura

```
tests/
├── conftest.py          # raíz: sys.path, fixtures de Flask, marcadores automáticos
├── README.md            # este archivo
│
├── sara/                # Sara
│   ├── unit/            # 10 pruebas unitarias puras
│   │   ├── test_001_roles_enum.py
│   │   ├── test_002_config_jwt.py
│   │   ├── test_003_config_uri.py
│   │   ├── test_004_correo_valido.py
│   │   ├── test_005_correo_invalido.py
│   │   ├── test_006_password_corta.py
│   │   ├── test_007_password_valida.py
│   │   ├── test_008_usuario_to_dict.py
│   │   ├── test_009_password_no_legible.py
│   │   └── test_010_repr_vehiculo.py
│   ├── integration/     # 4 pruebas con el test_client de Flask (sin base)
│   │   ├── test_025_health.py
│   │   ├── test_026_jwt_sin_token.py
│   │   ├── test_027_jwt_corrupto.py
│   │   └── test_028_login_sin_credenciales.py
│   └── e2e/             # 2 pruebas de flujo completo (base SQLite en memoria)
│       ├── test_029_login_token_perfil.py
│       └── test_030_reserva_con_celda.py
│
├── diego/               # Diego   → ver README dentro de la carpeta
├── andres/              # Andrés  → ver README dentro de la carpeta
└── nicole/              # Nicole  → ver README dentro de la carpeta
```

## ¿Unitarias, de integración o end-to-end?

| | `unit/` | `integration/` | `e2e/` |
|---|---|---|---|
| Construye la app Flask | ❌ No | ✅ Sí (`create_app()`) | ✅ Sí (`create_app()`) |
| Usa `test_client` | ❌ No | ✅ Sí | ✅ Sí |
| Consulta la base de datos | ❌ No | ❌ No | ✅ Sí (SQLite en memoria) |
| Fixture que usa | — | `client` / `flask_app` | `cliente_con_bd` |
| Qué se prueba | Modelos, configuración, servicios | Rutas sin base: health, JWT, payload vacío | Un flujo completo: login real, reservas, historial... |

**Regla:**

- Si solo importa una clase o función y la llama directamente → `unit/`.
- Si pide `client` o `flask_app` pero **no** consulta la base → `integration/`.
- Si pide `cliente_con_bd` y recorre un flujo completo de negocio → `e2e/`.

## Comandos

```bash
# Toda la suite del equipo
pytest

# Solo las pruebas de una persona
pytest tests/sara
pytest tests/diego

# Por tipo, en todo el equipo
pytest -m unit
pytest -m integration
pytest -m e2e

# Solo las end-to-end de una persona
pytest tests/sara/e2e

# Un archivo
pytest tests/sara/unit/test_006_password_corta.py

# Detalle de cada prueba
pytest -v

# Detenerse en el primer fallo
pytest -x
```

## Numeración de pruebas

El número del archivo es **consecutivo y global** para todo el equipo, así
nunca se repiten nombres:

| Rango | Dueño | Estado |
|---|---|---|
| `001 – 010` | Sara | ✅ ocupado |
| `011 – 013` | — | libre |
| `014 – 024` | — | libre |
| `025 – 030` | Sara | ✅ ocupado |
| `031` en adelante | quien agregue | libre |

> Antes de crear una prueba nueva, revisa qué número quedó libre para no
> pisar el de un compañero.

## Convenciones

1. **Ruta:** `tests/<persona>/<unit|integration|e2e>/test_<número>_<tema>.py`
2. **Función:** `test_<qué_hace>_<resultado_esperado>`
3. **Docstring** de una línea con la regla de negocio.
4. **Cuerpo** en tres bloques: `# Arrange`, `# Act`, `# Assert`.
5. **Un `assert` conceptual por prueba.**

### Plantilla

```python
# tests/<persona>/unit/test_025_mi_prueba.py
"""UNIT 025 · Clase · Regla de negocio que se valida."""

from app.modulo import MiClase


def test_mi_clase_devuelve_algo_esperado():
    """Describe en una frase qué debe cumplirse."""
    # Arrange
    entrada = "valor"

    # Act
    resultado = MiClase.metodo(entrada)

    # Assert
    assert resultado == "esperado"
```

## Fixtures disponibles

Están en `tests/conftest.py` y sirven para **todas** las carpetas:

- **`flask_app`** (scope `module`): construye la aplicación una vez por archivo.
  Desactiva `socketio.init_app` para no levantar WebSockets.
- **`client`**: `test_client` de Flask para llamar rutas sin abrir un puerto.
  Sirve para pruebas que **no** consultan la base (health, JWT, payload vacío).
- **`cliente_con_bd`**: igual que `client`, pero sobre **SQLite en memoria** con
  todas las tablas creadas. Al terminar la prueba se borran las tablas y se
  vuelve a la configuración de MySQL. Es el que se usa para las pruebas
  **end-to-end** (login real, guardar reservas, consultar historial...).

Son perezosos: si tu prueba no los pide, la aplicación ni se construye.

### Ejemplo de prueba end-to-end

Va en `tests/<persona>/e2e/`.

```python
def test_mi_flujo_completo(cliente_con_bd):
    """Login real → token → ruta protegida con datos de la base."""
    # Arrange: sembrar datos
    usuario = Usuario(nombre_completo="Sara", correo="sara@correo.com",
                      rol=RolEnum.USUARIO, activo=True)
    usuario.password = "Parklink2026*"
    db.session.add(usuario)
    db.session.commit()

    # Act: login y ruta protegida
    login = cliente_con_bd.post("/api/auth/login",
                                json={"correo": "sara@correo.com",
                                      "password": "Parklink2026*"})
    cabeceras = {"Authorization": f"Bearer {login.get_json()['token']}"}
    respuesta = cliente_con_bd.get("/api/auth/perfil", headers=cabeceras)

    # Assert
    assert respuesta.status_code == 200
```

## Bugs encontrados y corregidos por las pruebas

Una prueba en rojo no siempre está mal escrita: a veces **descubre un bug**. En
ese caso se corrige el código de la app, no la prueba.

| Prueba | Bug que encontró | Corrección |
|---|---|---|
| `sara/e2e/test_030_reserva_con_celda.py` | `Reserva` no tenía `celda_id`: reservar con celda elegida respondía 400. Además el servicio escribía en un atributo `estado` que `Celda` no tiene, así que nunca la marcaba como ocupada. | Se agregó `celda_id` al modelo y la migración `b41f7c9a2e13`; el servicio ahora marca `celda.ocupada = True`. |

## Notas

- Los marcadores `unit`, `integration` y `e2e` se asignan **automáticamente**
  según la carpeta donde esté el archivo.
- `pytest.ini` activa `--strict-markers`: si escribes un marcador que no exista,
  la suite falla a propósito para evitar errores de tipeo.
- Ninguna prueba toca MySQL: la app se construye pero nunca se ejecuta una
  consulta real. Las end-to-end usan SQLite en memoria.
