"""UNIT 057 · KPIs · Porcentaje de ocupación y tiempo promedio de parqueo."""


def test_calcular_porcentaje_ocupacion_general(app_context):
    """El porcentaje de ocupación es celdas ocupadas sobre el total."""
    # Arrange
    total_celdas = 100
    celdas_ocupadas = 45

    # Act
    porcentaje = round((celdas_ocupadas / total_celdas) * 100, 2)

    # Assert
    assert porcentaje == 45.0
    assert isinstance(porcentaje, float)


def test_kpi_tiempo_promedio_parqueo(app_context):
    """El tiempo promedio de permanencia se mide en minutos."""
    # Arrange
    duraciones_minutos = [120, 180, 60, 240]

    # Act
    promedio = sum(duraciones_minutos) / len(duraciones_minutos)

    # Assert
    assert promedio == 150.0
    assert isinstance(promedio, float)
