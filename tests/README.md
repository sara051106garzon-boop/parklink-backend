# Pruebas — ParkLink Back-End

Guía para el equipo. Cada integrante tiene **su propia carpeta** y dentro de
ella separa sus pruebas en `unit/` e `integration/`.

## Estructura

```
tests/
├── conftest.py          # raíz: sys.path, fixtures de Flask, marcadores automáticos
├── README.md            # este archivo
│
├── sara/                # Sara
│   └── unit/            # 10 pruebas unitarias puras
│       ├── test_001_roles_enum.py
│       ├── test_002_config_jwt.py
│       ├── test_003_config_uri.py
│       ├── test_004_correo_valido.py
│       ├── test_005_correo_invalido.py
│       ├── test_006_password_corta.py
│       ├── test_007_password_valida.py
│       ├── test_008_usuario_to_dict.py
│       ├── test_009_password_no_legible.py
│       └── test_010_repr_vehiculo.py
│
├── diego/               # Diego   → ver README dentro de la carpeta
├── andres/              # Andrés  → ver README dentro de la carpeta
└── nicole/              # Nicole  → ver README dentro de la carpeta
```

## ¿Unitarias o de integración?

| | `unit/` | `integration/` |
|---|---|---|
| Construye la app Flask | ❌ No | ✅ Sí (`create_app()`) |
| Usa `test_client` | ❌ No | ✅ Sí |
| Necesita MySQL | ❌ No | ❌ No |
| Qué se prueba | Modelos, configuración, servicios | Rutas, CORS, JWT, blueprints |

**Regla:** si tu prueba pide el fixture `client` o `flask_app`, va en
`integration/`. Si solo importa una clase o función y la llama directamente,
va en `unit/`.

## Comandos

```bash
# Toda la suite del equipo
pytest

# Solo las pruebas de una persona
pytest tests/sara
pytest tests/diego

# Solo unitarias / solo integración (de todo el equipo)
pytest -m unit
pytest -m integration

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
| `025` en adelante | quien agregue | libre |

> Antes de crear una prueba nueva, revisa qué número quedó libre para no
> pisar el de un compañero.

## Convenciones

1. **Ruta:** `tests/<persona>/<unit|integration>/test_<número>_<tema>.py`
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

Son perezosos: si tu prueba no los pide, la aplicación ni se construye.

## Notas

- Los marcadores `unit` e `integration` se asignan **automáticamente** según la
  carpeta donde esté el archivo.
- `pytest.ini` activa `--strict-markers`: si escribes un marcador que no exista,
  la suite falla a propósito para evitar errores de tipeo.
- Ninguna prueba toca MySQL: la app se construye pero nunca se ejecuta una
  consulta real.
