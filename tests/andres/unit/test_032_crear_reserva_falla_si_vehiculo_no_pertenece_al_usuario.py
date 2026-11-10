from unittest.mock import patch
from app.services.reserva_service import crear_reserva

@patch("app.services.reserva_service.Vehiculo.query")
def test_crear_reserva_falla_si_vehiculo_no_pertenece_al_usuario(mock_vehiculo_query, app_con_contexto_de_prueba):
    
    # ==========================================
    # 1. ARRANGE (Preparar el escenario)
    # ==========================================
    # El usuario autenticado tiene ID 10
    usuario_autenticado_id = 10

    # Intenta reservar con el vehiculo_id = 99 (que pertenece a otro usuario)
    datos_reserva = {
        "vehiculo_id": 99,
        "fecha": "2026-11-05",
        "hora": "10:00"
    }

    # Simulamos que la consulta combinada (id=99 AND usuario_id=10) NO encuentra nada
    mock_vehiculo_query.filter_by.return_value.first.return_value = None

    # ==========================================
    # 2. ACT (Ejecutar la acción a probar)
    # ==========================================
    respuesta = crear_reserva(usuario_autenticado_id, datos_reserva)

    # ==========================================
    # 3. ASSERT (Verificar los resultados)
    # ==========================================
    # A. Verificamos que la consulta filtró OBLIGATORIAMENTE por ambos campos
    mock_vehiculo_query.filter_by.assert_called_once_with(
        id=99,
        usuario_id=10
    )

    # B. Verificamos que la función devolvió el mensaje de error esperado
    assert "error" in respuesta
    assert respuesta["error"] == "Vehículo no encontrado o no pertenece al usuario."