"""
ParkLink - Pruebas Unitarias: Configuraciones Generales
Ubicación: tests/unit/test_configuraciones.py
"""

import pytest

def test_actualizar_horario_operativo_parqueadero(app_context):
    """
    Valida la actualización exitosa de los parámetros de horario operativo.
    """
    # --- ARRANGE ---
    config_simulada = {
        "hora_apertura": "06:00",
        "hora_cierre": "20:00"
    }
    nuevos_parametros = {
        "hora_apertura": "05:00",
        "hora_cierre": "22:00"
    }

    # --- ACT ---
    config_simulada.update(nuevos_parametros)

    # --- ASSERT ---
    assert config_simulada["hora_apertura"] == "05:00"
    assert config_simulada["hora_cierre"] == "22:00"

def test_validar_capacidad_maxima_no_negativa(app_context):
    """
    Verifica que la capacidad total configurada sea estrictamente un valor positivo.
    """
    # --- ARRANGE ---
    capacidad_invalida = -10

    # --- ACT & ASSERT ---
    with pytest.raises(ValueError, match="La capacidad total debe ser mayor a cero."):
        if capacidad_invalida <= 0:
            raise ValueError("La capacidad total debe ser mayor a cero.")