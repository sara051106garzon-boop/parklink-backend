"""UNIT 049 · kpis_service._accesos_activos · Solo cuenta vehículos cuyo último movimiento fue Entrada."""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from app.services.kpis_service import _accesos_activos


def _acceso(vehiculo_id, movimiento, hora):
    return SimpleNamespace(
        vehiculo_id=vehiculo_id,
        tipo_movimiento=movimiento,
        fecha_hora=datetime(2026, 11, 10, hora, 0),
    )


@patch("app.services.kpis_service.Acceso")
def test_accesos_activos_solo_incluye_vehiculos_cuyo_ultimo_movimiento_fue_entrada(mock_acceso):
    """El vehículo 1 ya salió; los vehículos 2 y 3 siguen dentro del parqueadero."""
    # Arrange: la consulta devuelve los accesos ordenados del más reciente al más antiguo
    mock_acceso.query.order_by.return_value.all.return_value = [
        _acceso(1, "Salida", 15),
        _acceso(3, "Entrada", 14),
        _acceso(2, "Entrada", 11),
        _acceso(1, "Entrada", 8),
    ]

    # Act
    activos = _accesos_activos()

    # Assert
    assert sorted(a.vehiculo_id for a in activos) == [2, 3]
