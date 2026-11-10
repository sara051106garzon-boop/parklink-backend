from unittest.mock import MagicMock, patch

from flask_jwt_extended import create_access_token

from app.services.kpis_service import calcular_metricas


def test_calcular_metricas_usa_porcentaje_cero_si_capacidad_es_cero(
    app_con_contexto_de_prueba,
):
    """Si no hay celdas ni capacidad configurada, evitar dividir por cero."""

    # ==========================================
    # 1. ARRANGE (Preparar el escenario)
    # ==========================================
    limites_cero = {
        "admin": 0,
        "operativas": 0,
        "movilidad": 0,
    }

    with patch(
        "app.services.kpis_service._limites_configuracion",
        return_value=limites_cero,
    ), patch(
        "app.services.kpis_service._accesos_activos",
        return_value=[],
    ), patch(
        "app.services.kpis_service.Celda.query"
    ) as mock_celda_query, patch(
        "app.services.kpis_service.Vehiculo.query"
    ) as mock_vehiculo_query, patch(
        "app.services.kpis_service.Alerta.query"
    ) as mock_alerta_query:

        mock_celda_query.all.return_value = []
        mock_vehiculo_query.all.return_value = []
        mock_alerta_query.count.return_value = 0

        # ==========================================
        # 2. ACT (Ejecutar el cálculo de métricas)
        # ==========================================
        resultado = calcular_metricas()

    # ==========================================
    # 3. ASSERT (Verificar que no se divide por cero)
    # ==========================================
    assert resultado["capacidad_total"] == 0
    assert resultado["ocupacion_total"] == 0
    assert resultado["porcentaje_ocupacion"] == 0


def test_kpis_ocupacion_usa_porcentajes_cero_si_capacidad_configurada_es_cero(
    app_con_contexto_de_prueba,
):
    """El endpoint debe responder con porcentajes 0 y no lanzar ZeroDivisionError."""

    app = app_con_contexto_de_prueba

    # ==========================================
    # 1. ARRANGE (Preparar el escenario)
    # ==========================================
    configuracion_cero = MagicMock(
        celdas_admin=0,
        celdas_operativas=0,
        celdas_movilidad=0,
    )

    with app.app_context():
        token = create_access_token(identity="1")

    with patch(
        "app.routes.admin.Configuracion.query"
    ) as mock_config_query, patch(
        "app.routes.admin.Celda.query"
    ) as mock_celda_query:

        mock_config_query.first.return_value = configuracion_cero
        # Cada categoría consulta: Celda.query.filter(...).filter(...).count()
        mock_celda_query.filter.return_value.filter.return_value.count.return_value = 0

        cliente = app.test_client()

        # ==========================================
        # 2. ACT (Consultar el endpoint de ocupación)
        # ==========================================
        respuesta = cliente.get(
            "/api/admin/kpis-ocupacion",
            headers={"Authorization": f"Bearer {token}"},
        )

    # ==========================================
    # 3. ASSERT (Verificar la respuesta segura)
    # ==========================================
    assert respuesta.status_code == 200

    datos = respuesta.get_json()

    assert datos["totales"]["capacidad_maxima"] == 0
    assert datos["totales"]["ocupacion_actual"] == 0
    assert datos["totales"]["porcentaje_uso_global"] == 0

    for detalle in datos["detalles_por_perfil"].values():
        assert detalle["maximo"] == 0
        assert detalle["dentro"] == 0
        assert detalle["porcentaje"] == 0
