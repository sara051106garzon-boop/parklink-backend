# Pruebas — ParkLink Back-End

Guía rápida para el equipo. Aquí se explica cómo está organizada la suite y
cómo agregar pruebas nuevas sin romper la estructura.

## Estructura

```
tests/
├── conftest.py            # raíz: sys.path + marcadores automáticos unit/integration
├── README.md              # este archivo
│
├── unit/                  # Pruebas unitarias puras
│   ├── test_001_roles_enum.py
│   ├── test_002_config_jwt.py
│   ├── test_003_config_uri.py
│   ├── test_004_correo_valido.py
│   ├── test_005_correo_invalido.py
│   ├── test_006_password_corta.py
│   ├── test_007_password_valida.py
│   ├── test_008_usuario_to_dict.py
│   ├── test_009_password_no_legible.py
│   └── test_010_repr_vehiculo.py
│
└── integration/           # Pruebas de integración con Flask
    ├── conftest.py        # fixtures: flask_app, client
    ├── test_014_instancias_unicas.py
    ├── test_015_create_app.py
    ├── test_016_health.py
    ├── test_017_blueprints.py
    ├── test_019_cors_permitido.py
    ├── test_020_cors_rechazado.py
    ├── test_021_jwt_sin_token.py
    ├── test_022_jwt_token_corrupto.py
    ├── test_023_jwt_token_expirado.py
    └── test_024_jwt_firma_invalida.py
```

## ¿Unitarias o de integración?

| | `unit/` | `integration/` |
|---|---|---|
| Construye la app Flask | ❌ No | ✅ Sí (`create_app()`) |
| Usa `test_client` | ❌ No | ✅ Sí |
| Necesita MySQL | ❌ No | ❌ No |
| Velocidad | Muy rápida (ms) | Rápida (ms) |
| Qué se prueba | Modelos, configuración, servicios | Rutas, CORS, JWT, blueprints |

**Regla:** si tu prueba necesita `client` o `flask_app`, va en `integration/`.
Si solo importa una clase o función y la llama directamente, va en `unit/`.

## Comandos

```bash
# Toda la suite
pytest

# Solo unitarias
pytest -m unit

# Solo integración
pytest -m integration

# Un archivo
pytest tests/unit/test_006_password_corta.py

# Una prueba concreta
pytest tests/unit/test_006_password_corta.py::test_validar_password_rechaza_una_contrasena_de_siete_caracteres

# Ver el detalle de cada prueba
pytest -v

# Detenerse en el primer fallo
pytest -x
```

## Convenciones para agregar pruebas

1. **Nombre del archivo:** `test_<número>_<tema_en_snake_case>.py`
   El número es consecutivo y global (unit e integration comparten numeración).
   Ya están tomados el 001–010 y el 014–024, así que la siguiente es `025`.
2. **Nombre de la función:** `test_<qué_hace>_<resultado_esperado>`.
   Ejemplo: `test_validar_password_rechaza_una_contrasena_de_siete_caracteres`.
3. **Docstring obligatorio:** una línea que describa la regla de negocio.
4. **Cuerpo en tres bloques:** `# Arrange`, `# Act`, `# Assert`.
5. **Un solo `assert` conceptual por prueba.** Si necesitas comprobar dos
   cosas distintas, son dos pruebas.

### Plantilla

```python
# tests/unit/test_025_mi_prueba.py
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

## Los fixtures

Viven en `tests/integration/conftest.py`:

- **`flask_app`** (scope `module`): construye la aplicación una vez por archivo.
  Desactiva `socketio.init_app` para no levantar WebSockets.
- **`client`**: `test_client` de Flask para llamar rutas sin abrir un puerto.

## Notas

- Los marcadores `unit` e `integration` se asignan **automáticamente** según la
  carpeta, no hay que escribirlos en cada archivo.
- `pytest.ini` activa `--strict-markers`, así que si escribes un marcador que no
  esté declarado ahí, la suite falla a propósito (para evitar errores de tipeo).
- Ninguna prueba toca MySQL: la app se construye pero nunca se ejecuta una
  consulta real.
