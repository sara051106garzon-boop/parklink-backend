"""UNIT 041 · usuario_service.registrar_mi_vehiculo · No permite registrar una placa que ya existe."""

from unittest.mock import MagicMock, patch

from app.services.usuario_service import registrar_mi_vehiculo


@patch("app.services.usuario_service.db")
@patch("app.services.usuario_service.Vehiculo")
def test_registrar_mi_vehiculo_rechaza_una_placa_ya_registrada(mock_vehiculo, mock_db):
    """Si la placa (en mayúsculas) ya existe, devuelve el error y no guarda nada."""
    # Arrange
    mock_vehiculo.query.filter_by.return_value.first.return_value = MagicMock()
    datos = {"placa": "abc123", "tipo_vehiculo": "Automóvil"}

    # Act
    resultado = registrar_mi_vehiculo(1, datos)

    # Assert
    assert resultado == {"error": "La placa ya está registrada."}
    mock_db.session.add.assert_not_called()
