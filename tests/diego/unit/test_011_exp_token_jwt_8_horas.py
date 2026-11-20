"""UNIT 011 · Config · El token JWT de ParkLink debe expirar en 8 horas."""

from datetime import timedelta

from app.config.settings import Config


def test_config_token_jwt_expira_en_8_horas():
    """La sesión del usuario se cierra sola a las 8 horas de haber iniciado."""
    # Arrange
    tiempo_esperado = timedelta(hours=8)

    # Act
    tiempo_configurado = Config.JWT_ACCESS_TOKEN_EXPIRES

    # Assert
    assert tiempo_configurado == tiempo_esperado, (
        f"Se esperaba una expiración de {tiempo_esperado}, pero se obtuvo {tiempo_configurado}"
    )
