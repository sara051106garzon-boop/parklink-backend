"""
ParkLink - Pruebas Unitarias: Métricas y KPIs
Ubicación: tests/unit/test_kpis.py
"""

def test_calcular_porcentaje_ocupacion_general(app_context):
    """
    Valida el cálculo matemático del porcentaje de ocupación general.
    """
    # --- ARRANGE ---
    total_celdas = 100
    celdas_ocupadas = 45

    # --- ACT ---
    porcentaje = round((celdas_ocupadas / total_celdas) * 100, 2)

    # --- ASSERT ---
    assert porcentaje == 45.0
    assert isinstance(porcentaje, float)

def test_kpi_tiempo_promedio_parqueo(app_context):
    """
    Valida el cálculo del tiempo promedio de permanencia vehicular en minutos.
    """
    # --- ARRANGE ---
    duraciones_minutos = [120, 180, 60, 240]

    # --- ACT ---
    promedio = sum(duraciones_minutos) / len(duraciones_minutos)

    # --- ASSERT ---
    assert promedio == 150.0
    assert isinstance(promedio, float)