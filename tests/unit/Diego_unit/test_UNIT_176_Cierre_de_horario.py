from unittest.mock import patch, MagicMock
from app.services.reserva_service import crear_reserva
from datetime import datetime, timedelta

def test_crear_reserva_rechaza_hora_20_59_fuera_del_horario_declarado(app_context):
    # --- ARRANGE ---
    usuario_id_valido = 1
    fecha_futura = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    datos_reserva = {
        "vehiculo_id": 10,
        "fecha": fecha_futura,
        "hora": "20:59"
    }

    with patch("app.models.vehiculo.Vehiculo.query") as mock_vehiculo:
        mock_vehiculo.filter_by.return_value.first.return_value = MagicMock(
            id=10,
            usuario_id=usuario_id_valido,
            placa="ABC123"
        )

        # --- ACT ---
        resultado = crear_reserva(usuario_id_valido, datos_reserva)

        # --- ASSERT ---
        assert isinstance(resultado, dict) and "error" in resultado
        assert "entre las 06:00 y las 20:00" in resultado["error"]


def test_crear_reserva_acepta_hora_de_cierre_20_00(app_context):
    fecha_futura = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    datos_reserva = {
        "vehiculo_id": 10,
        "fecha": fecha_futura,
        "hora": "20:00"
    }

    with patch("app.models.vehiculo.Vehiculo.query") as mock_vehiculo, \
         patch("app.models.reserva.Reserva.query") as mock_reserva, \
         patch("app.database.database.db.session.add"), \
         patch("app.database.database.db.session.commit"):
        mock_vehiculo.filter_by.return_value.first.return_value = MagicMock(
            id=10,
            usuario_id=1,
            placa="ABC123"
        )
        mock_reserva.filter_by.return_value.first.return_value = None

        resultado = crear_reserva(1, datos_reserva)

    assert resultado["mensaje"] == "Reserva creada correctamente."