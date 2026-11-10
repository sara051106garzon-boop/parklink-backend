# Pruebas de Diego

Esta carpeta es tuya. Aquí van **solo tus pruebas**, para que no choquen con
las de los demás.

```
tests/diego/
├── conftest.py        # fixtures propias: app con SQLite, tokens JWT y mocks de celdas
├── unit/              # pruebas unitarias puras (modelos, config, servicios)
│   ├── test_011_exp_token_jwt_8_horas.py
│   ├── test_040_vehiculo_exige_propietario.py
│   ├── test_041_bcrypt_limite_72_bytes.py
│   ├── test_042_perfil_vehiculos_y_reservas.py
│   ├── test_043_cierre_de_horario.py
│   ├── test_044_registro_usuario_admin.py
│   ├── test_045_rechazo_perfil_no_encontrado.py
│   ├── test_046_ruta_protegida_sin_token.py
│   ├── test_047_config_valor_null.py
│   ├── test_048_salida_vigilante_error_negocio.py
│   ├── test_053_accesos.py
│   ├── test_055_alertas.py
│   ├── test_056_configuraciones.py
│   ├── test_057_kpis.py
│   └── test_058_logs.py
├── integration/       # pruebas con el `test_client` de Flask (rutas, JWT, BD en memoria)
│   ├── test_049_login_jwt_perfil.py
│   ├── test_050_middleware_jwt_invalido.py
│   ├── test_051_reserva_interaccion_bd.py
│   └── test_052_salida_vehiculo_vigilante.py
└── README.md          # este archivo
```

## Reglas

1. **Numeración:** cada archivo lleva el número global del equipo. Diego usa
   `011` y del `040` al `058`; las siguientes libres empiezan en `059`.
2. **Nombre del archivo:** `test_<número>_<tema_en_snake_case>.py`
3. **Nombre de la función:** `test_<qué_hace>_<resultado_esperado>`
4. **Docstring** de una línea + cuerpo en `# Arrange`, `# Act`, `# Assert`.

## Plantilla

```python
# tests/diego/unit/test_059_mi_prueba.py
"""UNIT 059 · Clase · Regla de negocio que se valida."""

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

## Fixtures

Las globales de `tests/conftest.py` (`flask_app`, `client`, `cliente_con_bd`)
están disponibles en toda la suite. Las propias de Diego están en
`tests/diego/conftest.py`:

| Fixture | Para qué sirve |
|---|---|
| `app` | App Flask sobre SQLite en memoria, con llaves foráneas activas |
| `test_database` | Esquema limpio (tablas creadas) por prueba |
| `db_session` | Sesión de SQLAlchemy de esa base |
| `client_de_diego` | `test_client` sobre la app con base |
| `app_context` | Contexto de aplicación para llamar servicios |
| `token_admin` / `token_usuario` / `token_vigilante` | Tokens JWT por rol |
| `headers_admin` / `headers_usuario` / `headers_vigilante` | Cabeceras Bearer listas |
| `mock_celda_libre` / `mock_celda_ocupada` / `mock_celda_reservada` | Celdas simuladas |

## Comandos

```bash
pytest tests/diego          # solo tus pruebas
pytest -m unit              # todas las unitarias del equipo
pytest -m integration       # todas las de integración del equipo
pytest                      # toda la suite
```
