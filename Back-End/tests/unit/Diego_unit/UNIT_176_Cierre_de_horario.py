from app.services.reserva_service import crear_reserva
from datetime import datetime, timedelta

def test_crear_reserva_rechaza_hora_20_59_fuera_del_horario_declarado(app_context):
    # --- ARRANGE (Preparar) ---
    usuario_id_valido = 1
    fecha_futura = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    datos_reserva = {
        "vehiculo_id": 10,
        "fecha": fecha_futura,
        "hora": "20:59"
    }

    # --- ACT (Actuar) ---
    resultado = crear_reserva(usuario_id_valido, datos_reserva)

    # --- ASSERT (Afirmar) ---
    assert "error" in resultado
    assert "Fuera del horario operativo" in resultado["error"], (
        "Defecto: El sistema aceptó una reserva a las 20:59 a pesar de cerrar a las 20:00"
    )