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
