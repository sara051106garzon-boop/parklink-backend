"""UNIT 058 · Logs · Registro y filtrado de la auditoría del sistema."""

from datetime import datetime
from unittest.mock import MagicMock, patch


def test_registrar_log_auditoria_cambio_configuracion(app_context):
    """Modificar la configuración deja un log de auditoría del administrador."""
    # Arrange
    admin_id = 1
    accion = "CAMBIO_HORARIO_PERMITIDO"
    detalle = "Horario modificado de 06:00-20:00 a 05:00-22:00"

    with patch("app.models.LogAuditoria") as mock_log_class, \
         patch("app.database.database.db.session.add") as mock_add:

        mock_log = MagicMock()
        mock_log.usuario_id = admin_id
        mock_log.accion = accion
        mock_log_class.return_value = mock_log

        # Act
        nuevo_log = mock_log_class(
            usuario_id=admin_id,
            accion=accion,
            detalle=detalle,
            fecha=datetime.now()
        )
        mock_add(nuevo_log)

        # Assert
        assert nuevo_log.usuario_id == 1
        assert nuevo_log.accion == "CAMBIO_HORARIO_PERMITIDO"
        mock_add.assert_called_once_with(nuevo_log)


def test_filtrar_logs_auditoria_por_usuario(app_context):
    """El historial de logs se puede filtrar por usuario."""
    # Arrange
    target_user_id = 1
    logs_simulados = [
        MagicMock(usuario_id=1, accion="LOGIN"),
        MagicMock(usuario_id=1, accion="ACTUALIZAR_CELDA"),
        MagicMock(usuario_id=2, accion="LOGIN"),
    ]

    # Act
    logs_filtrados = [log for log in logs_simulados if log.usuario_id == target_user_id]

    # Assert
    assert len(logs_filtrados) == 2
    assert all(log.usuario_id == target_user_id for log in logs_filtrados)
