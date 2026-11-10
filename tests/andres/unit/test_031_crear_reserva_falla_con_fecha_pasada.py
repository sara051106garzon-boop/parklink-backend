from datetime import date, timedelta
from unittest.mock import patch, MagicMock
from app.services.reserva_service import crear_reserva


@patch("app.services.reserva_service.Vehiculo.query")
def test_crear_reserva_falla_si_fecha_es_pasada(mock_vehiculo_query, app_con_contexto_de_prueba):
    
    # ==========================================
    # 1. ARRANGE (Preparar el escenario)
    # ==========================================
    # A. Superar la validación previa del vehículo
    vehiculo_simulado = MagicMock()
    vehiculo_simulado.id = 5
    vehiculo_simulado.usuario_id = 1
    mock_vehiculo_query.filter_by.return_value.first.return_value = vehiculo_simulado

    # B. Generar una fecha dinámica de ayer (YYYY-MM-DD) para asegurar que sea pasada
    fecha_ayer = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    datos_reserva = {
        "vehiculo_id": 5,
        "fecha": fecha_ayer,
        "hora": "10:00"
    }

    # ==========================================
    # 2. ACT (Ejecutar la función del servicio)
    # ==========================================
    respuesta = crear_reserva(usuario_id=1, data=datos_reserva)

    # ==========================================
    # 3. ASSERT (Verificar que se rechazó la solicitud)
    # ==========================================
    assert "error" in respuesta
    assert respuesta["error"] == "No puedes reservar en fechas pasadas."