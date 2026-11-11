"""UNIT 042 · usuario_service.obtener_mis_vehiculos · Serializa los vehículos del usuario."""

from types import SimpleNamespace
from unittest.mock import patch

from app.services.usuario_service import obtener_mis_vehiculos


@patch("app.services.usuario_service.Vehiculo")
def test_obtener_mis_vehiculos_devuelve_lista_de_diccionarios_con_los_campos_esperados(mock_vehiculo):
    """Cada vehículo se convierte en un dict con id, placa, tipo, marca, color y área."""
    # Arrange
    vehiculo = SimpleNamespace(
        id=7, placa="XYZ987", tipo_vehiculo="Motocicleta",
        marca="Yamaha", color="Negro", area="Operaciones",
    )
    mock_vehiculo.query.filter_by.return_value.all.return_value = [vehiculo]

    # Act
    resultado = obtener_mis_vehiculos("3")

    # Assert
    assert resultado == [{
        "id": 7, "placa": "XYZ987", "tipo_vehiculo": "Motocicleta",
        "marca": "Yamaha", "color": "Negro", "area": "Operaciones",
    }]
