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
