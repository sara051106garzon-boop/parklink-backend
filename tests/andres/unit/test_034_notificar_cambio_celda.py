from unittest.mock import patch

from app.models.celda import Celda
from app.routes.celdas import notificar_cambio_celda


@patch("app.routes.celdas.socketio.emit")
def test_notificar_cambio_celda_emite_payload_esperado(mock_emit):

    # ==========================================
    # 1. ARRANGE (Preparar el escenario)
    # ==========================================
    celda = Celda(
        id=7,
        codigo_celda="A-07",
        tipo_celda="carro",
        ocupada=True,
        planta=2,
        estado="ocupado",
        placa="ABC123",
        usuario="Ana Pérez",
        marca="Toyota",
        modelo="Corolla",
        color_hex="#ff0000",
        hora_ingreso="10:30 AM"
    )

    payload_esperado = {
        "id": 7,
        "codigo": "A-07",
        "puesto": "A-07",
        "planta": 2,
        "estado": "ocupado",
        "tipoVehiculo": "carro",
        "ocupada": True,
        "placa": "ABC123",
        "usuario": "Ana Pérez",
        "marca": "Toyota",
        "modelo": "Corolla",
        "colorHex": "#ff0000",
        "horaIngreso": "10:30 AM"
    }

    # ==========================================
    # 2. ACT (Ejecutar la función a probar)
    # ==========================================
    notificar_cambio_celda(celda)

    # ==========================================
    # 3. ASSERT (Verificar la emisión del evento)
    # ==========================================
    # A. Se emitió exactamente una vez el evento 'celda_actualizada'
    # B. La carga útil contiene código, planta y estado (además del resto de datos)
    mock_emit.assert_called_once_with("celda_actualizada", payload_esperado)
