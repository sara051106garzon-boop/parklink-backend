def test_salida_vigilante_error_de_negocio_devuelve_400(client, headers_vigilante):
    # --- ARRANGE (Preparar) ---
    payload_salida = {
        "placa": "ABC123"
    }

    # --- ACT (Actuar) ---
    response = client.post(
        "/api/vigilante/salida",
        json=payload_salida,
        headers=headers_vigilante
    )

    # --- ASSERT (Afirmar) ---
    assert response.status_code == 400
    datos = response.get_json()
    assert datos.get("mensaje") == "El vehículo nunca ha ingresado"