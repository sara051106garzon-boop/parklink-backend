from unittest.mock import patch

import pytest

from app.models.celda import Celda
from app.routes.celdas import notificar_cambio_celda


@pytest.mark.parametrize(
    "estado, ocupada",
    [
        ("libre", False),
        ("ocupado", True),
        ("reservado", False),
    ]
)
def test_estado_explicito_es_consistente_con_ocupada(estado, ocupada):

    # ==========================================
    # 1. ARRANGE (Preparar el escenario)
    # ==========================================
    celda = Celda(
        id=1,
        codigo_celda="A-01",
        tipo_celda="carro",
        planta=1,
        estado=estado,
        ocupada=ocupada
    )

    # ==========================================
    # 2. ACT (Calcular el estado dinámico de la celda)
    # ==========================================
    with patch("app.routes.celdas.socketio.emit") as mock_emit:
        notificar_cambio_celda(celda)

    # ==========================================
    # 3. ASSERT (Verificar la consistencia)
    # ==========================================
    mock_emit.assert_called_once()
    nombre_evento, payload = mock_emit.call_args.args

    assert nombre_evento == "celda_actualizada"
    assert payload["estado"] == estado
    assert payload["ocupada"] is ocupada

    # Regla de consistencia: solo el estado "ocupado" representa una celda ocupada
    assert payload["ocupada"] is (payload["estado"] == "ocupado")


@pytest.mark.parametrize(
    "ocupada, estado_esperado",
    [
        (False, "libre"),
        (True, "ocupado"),
    ]
)
def test_estado_dinamico_se_deriva_de_ocupada_si_estado_es_nulo(ocupada, estado_esperado):

    # ==========================================
    # 1. ARRANGE (Preparar el escenario)
    # ==========================================
    # Celda sin estado explícito: el estado debe calcularse desde el booleano 'ocupada'
    celda = Celda(
        id=2,
        codigo_celda="B-02",
        tipo_celda="carro",
        planta=2,
        ocupada=ocupada
    )
    celda.estado = None

    # ==========================================
    # 2. ACT (Calcular el estado dinámico de la celda)
    # ==========================================
    with patch("app.routes.celdas.socketio.emit") as mock_emit:
        notificar_cambio_celda(celda)

    # ==========================================
    # 3. ASSERT (Verificar el estado calculado)
    # ==========================================
    mock_emit.assert_called_once()
    nombre_evento, payload = mock_emit.call_args.args

    assert nombre_evento == "celda_actualizada"
    assert payload["estado"] == estado_esperado
    assert payload["ocupada"] is ocupada
    assert payload["codigo"] == "B-02"
    assert payload["planta"] == 2
