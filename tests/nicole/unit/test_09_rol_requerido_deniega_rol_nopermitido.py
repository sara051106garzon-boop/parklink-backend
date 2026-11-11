"""UNIT 048 · rol_requerido · Un rol no permitido recibe 403 y la vista no se ejecuta."""

from unittest.mock import patch

from flask import Flask

from app.middlewares.roles import rol_requerido


def test_rol_requerido_responde_403_si_el_rol_del_token_no_esta_permitido():
    """Un token con rol 'usuario' no puede entrar a una vista exclusiva de administrador."""
    # Arrange
    aplicacion = Flask(__name__)
    llamadas = []

    @rol_requerido("administrador")
    def vista_protegida():
        llamadas.append("ejecutada")
        return "ok"

    # Act
    with aplicacion.test_request_context():
        with patch("app.middlewares.roles.verify_jwt_in_request"), patch(
            "app.middlewares.roles.get_jwt", return_value={"rol": "usuario"}
        ):
            respuesta, codigo = vista_protegida()

    # Assert
    assert codigo == 403 and llamadas == []
