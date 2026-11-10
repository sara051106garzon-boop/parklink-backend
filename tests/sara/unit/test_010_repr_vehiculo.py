# tests/unit/test_010_repr_vehiculo.py
"""UNIT 010 · Vehiculo.__repr__ · Representación legible."""

from app.models.vehiculo import Vehiculo


def test_repr_de_vehiculo_muestra_la_placa():
    """La representación del vehículo debe incluir su placa."""
    # Arrange
    vehiculo = Vehiculo(placa="XYZ987")

    # Act
    representacion = repr(vehiculo)

    # Assert
    assert representacion == "<Vehiculo XYZ987>"
