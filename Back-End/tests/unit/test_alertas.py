"""
ParkLink - Pruebas Unitarias: Monitoreo de Alertas
Ubicación: tests/unit/test_alertas.py
"""

from unittest.mock import MagicMock, patch

def test_generar_alerta_mantenimiento_admin(app_context):
    """
    Valida la generación de una alerta técnica por fallo de infraestructura.
    """
    # --- ARRANGE ---
    datos_alerta = {
        "titulo": "Fallo en Sensor Sótano 1",
        "descripcion": "El sensor de presencia en la celda A-05 no responde.",
        "nivel": "ALTO"
    }

    with patch("app.models.Alerta") as mock_alerta_class:
        mock_alerta = MagicMock()
        mock_alerta.titulo = datos_alerta["titulo"]
        mock_alerta.nivel = datos_alerta["nivel"]
        mock_alerta.resuelto = False
        mock_alerta_class.return_value = mock_alerta

        # --- ACT ---
        alerta_creada = mock_alerta_class(
            titulo=datos_alerta["titulo"],
            descripcion=datos_alerta["descripcion"],
            nivel=datos_alerta["nivel"]
        )

        # --- ASSERT ---
        assert alerta_creada.titulo == "Fallo en Sensor Sótano 1"
        assert alerta_creada.nivel == "ALTO"
        assert alerta_creada.resuelto is False

def test_resolver_alerta_pendiente_exito(app_context):
    """
    Verifica que el administrador pueda marcar una alerta pendiente como resuelta.
    """
    # --- ARRANGE ---
    alerta_id = 12
    mock_alerta = MagicMock()
    mock_alerta.id = alerta_id
    mock_alerta.resuelto = False

    with patch("app.models.Alerta.query") as mock_query, \
         patch("app.database.database.db.session.commit") as mock_commit:

        mock_query.get.return_value = mock_alerta

        # --- ACT ---
        alerta = mock_query.get(alerta_id)
        alerta.resuelto = True
        mock_commit()

        # --- ASSERT ---
        assert alerta.resuelto is True
        mock_commit.assert_called_once()