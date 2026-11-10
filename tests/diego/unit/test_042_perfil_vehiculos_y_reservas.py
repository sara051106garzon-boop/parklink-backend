"""UNIT 042 · UsuarioService · El perfil incluye el conteo de vehículos y reservas."""

from unittest.mock import MagicMock, patch

from app.models.usuario import RolEnum
from app.services.usuario_service import obtener_perfil


def test_obtener_perfil_incluye_conteo_de_vehiculos_y_reservas(app_context):
    """El resumen del perfil del usuario debe traer sus totales."""
    # Arrange
    usuario_id_mock = 5

    with patch("app.services.usuario_service.get_jwt_identity", return_value=usuario_id_mock), \
         patch("app.models.usuario.Usuario.query") as mock_usuario_query, \
         patch("app.models.vehiculo.Vehiculo.query") as mock_vehiculo_query, \
         patch("app.models.reserva.Reserva.query") as mock_reserva_query:
        usuario_mock = MagicMock()
        usuario_mock.nombre_completo = "Diego Plazas"
        usuario_mock.correo = "diego@parklink.com"
        usuario_mock.rol = RolEnum.USUARIO

        mock_usuario_query.get.return_value = usuario_mock
        mock_vehiculo_query.filter_by.return_value.count.return_value = 2
        mock_reserva_query.filter_by.return_value.count.return_value = 1

        # Act
        perfil = obtener_perfil()

        # Assert
        assert perfil == {
            "nombre_completo": "Diego Plazas",
            "correo": "diego@parklink.com",
            "rol": "usuario",
            "vehiculos": 2,
            "reservas": 1
        }
