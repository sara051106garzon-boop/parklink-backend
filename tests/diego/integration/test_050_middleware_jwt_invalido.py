"""Integración del middleware JWT para tokens inválidos."""

from sqlalchemy import event

from app.models.acceso import Acceso


def test_historial_rechaza_token_invalido_antes_de_consultar_bd(
    client_de_diego, app, db_session
):
    """INT 050 | Severidad: Alta. JWT inválido debe bloquear la ruta protegida."""
    # Arrange
    cantidad_accesos = db_session.query(Acceso).count()
    sentencias = []
    engine = db_session.get_bind()

    def registrar_sentencia(conn, cursor, statement, parameters, context, executemany):
        sentencias.append(statement)

    event.listen(engine, "before_cursor_execute", registrar_sentencia)

    # Act
    try:
        response = client_de_diego.get(
            "/api/admin/historial",
            headers={"Authorization": "Bearer token-invalido"},
        )
    finally:
        event.remove(engine, "before_cursor_execute", registrar_sentencia)

    # Assert
    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "invalid_token"
    assert data["mensaje"]
    assert sentencias == []
    assert db_session.query(Acceso).count() == cantidad_accesos
