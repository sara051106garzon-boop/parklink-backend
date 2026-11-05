def test_config_put_valor_null_devuelve_400(client, headers_admin):
    # --- ARRANGE (Preparar) ---
    payload_invalido = {
        "celdas_admin": None
    }

    # --- ACT (Actuar) ---
    response = client.put(
        "/api/admin/config",
        json=payload_invalido,
        headers=headers_admin
    )

    # --- ASSERT (Afirmar) ---
    assert response.status_code == 400, (
        f"Se esperaba HTTP 400 por valor 'null' en entero, pero devolvió HTTP {response.status_code}"
    )