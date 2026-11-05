from datetime import timedelta
from app.config import Config

def test_config_token_jwt_expira_en_8_horas():
    # --- ARRANGE (Preparar) ---
    tiempo_esperado = timedelta(hours=8)

    # --- ACT (Actuar) ---
    tiempo_configurado = Config.JWT_ACCESS_TOKEN_EXPIRES

    # --- ASSERT (Afirmar) ---
    assert tiempo_configurado == tiempo_esperado, (
        f"Se esperaba una expiración de {tiempo_esperado}, pero se obtuvo {tiempo_configurado}"
    )