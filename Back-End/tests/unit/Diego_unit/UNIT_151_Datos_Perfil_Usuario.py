from unittest.mock import patch, MagicMock
from app.services.usuario_service import UsuarioService

def test_obtener_perfil_incluye_conteo_de_vehiculos_y_reservas(app_context):
    # --- ARRANGE (Preparar) ---
    usuario_id_mock = 5
    
    with patch("app.models.usuario.Usuario.query") as mock_query:
        usuario_mock = MagicMock()
        usuario_mock.nombre = "Diego Plazas"
        usuario_mock.correo = "diego@parklink.com"
        usuario_mock.rol = "usuario"
        
        # Mocks para relaciones y conteos (2 vehículos, 1 reserva activa)
        usuario_mock.vehiculos = [MagicMock(), MagicMock()]
        usuario_mock.reservas = [MagicMock(estado="activa")]
        
        mock_query.get.return_value = usuario_mock

        # --- ACT (Actuar) ---
        perfil = UsuarioService.obtener_perfil(usuario_id_mock)

        # --- ASSERT (Afirmar) ---
        assert perfil["nombre"] == "Diego Plazas"
        assert perfil["total_vehiculos"] == 2
        assert perfil["reservas_activas"] == 1