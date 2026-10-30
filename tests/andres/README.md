# Pruebas de Andrés

Esta carpeta es tuya. Aquí van **solo tus pruebas**, para que no choquen con
las de los demás.

Crea estas dos subcarpetas cuando empieces:

```
tests/andres/
├── unit/           → pruebas unitarias puras (modelos, config, servicios)
└── integration/    → pruebas que usan el `client` de Flask (rutas, CORS, JWT)
```

## Reglas

1. **Numeración:** usa el rango que te asigne el equipo. Sara ya ocupó
   `001–010`, así que las siguientes libres empiezan en `011`.
2. **Nombre del archivo:** `test_<número>_<tema_en_snake_case>.py`
3. **Nombre de la función:** `test_<qué_hace>_<resultado_esperado>`
4. **Docstring** de una línea + cuerpo en `# Arrange`, `# Act`, `# Assert`.

## Plantilla

```python
# tests/andres/unit/test_025_mi_prueba.py
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

## Comandos

```bash
pytest tests/andres         # solo tus pruebas
pytest -m unit              # todas las unitarias del equipo
pytest                      # toda la suite
```

Los fixtures `flask_app` y `client` ya están disponibles globalmente: solo
decláralos como parámetro de tu función y listo.
