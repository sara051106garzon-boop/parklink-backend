"""UNIT 047 · EmailService.enviar_correo_bienvenida · Un fallo de envío no rompe el flujo."""

from types import SimpleNamespace
from unittest.mock import patch

from app.services.email_service import EmailService

# ``current_app`` es un proxy de Flask: con ``new=`` mock no intenta inspeccionarlo.
CONFIG_FALSA = SimpleNamespace(config={"MAIL_USERNAME": "soporte@parklink.com"})


@patch("app.services.email_service.current_app", new=CONFIG_FALSA)
@patch("app.services.email_service.EmailMessage")
def test_enviar_correo_bienvenida_devuelve_false_si_el_envio_falla(mock_email):
    """Si el servidor SMTP lanza una excepción, el servicio la captura y devuelve False."""
    # Arrange
    mock_email.return_value.send.side_effect = Exception("SMTP no disponible")

    # Act
    resultado = EmailService.enviar_correo_bienvenida(
        "ana@empresa.com", "Ana Pérez", "Temporal123*"
    )

    # Assert
    assert resultado is False