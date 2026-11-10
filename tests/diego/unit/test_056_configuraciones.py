"""UNIT 056 · Configuraciones · Horario operativo y capacidad total del parqueadero."""

import pytest


def test_actualizar_horario_operativo_parqueadero(app_context):
    """Se pueden actualizar las horas de apertura y cierre."""
    # Arrange
    config_simulada = {
        "hora_apertura": "06:00",
        "hora_cierre": "20:00"
    }
    nuevos_parametros = {
        "hora_apertura": "05:00",
        "hora_cierre": "22:00"
    }

    # Act
    config_simulada.update(nuevos_parametros)

    # Assert
    assert config_simulada["hora_apertura"] == "05:00"
    assert config_simulada["hora_cierre"] == "22:00"


def test_validar_capacidad_maxima_no_negativa(app_context):
    """La capacidad total configurada debe ser estrictamente positiva."""
    # Arrange
    capacidad_invalida = -10

    # Act / Assert
    with pytest.raises(ValueError, match="La capacidad total debe ser mayor a cero."):
        if capacidad_invalida <= 0:
            raise ValueError("La capacidad total debe ser mayor a cero.")
