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
