from app.database.database import db
from app.models.configuracion import Configuracion


def test_validar_cupo_rechaza_perfil_no_valido(client, headers_admin, test_database):
    # --- ARRANGE ---
    db.session.add(Configuracion())
    db.session.commit()

    payload_validacion = {
        "placa": "XYZ-999",
        "tipo_usuario": "visitante",
        "planta": 1
    }

    # --- ACT ---
    response = client.post(
        "/api/admin/ingresos/validar-cupo",
        json=payload_validacion,
        headers=headers_admin
    )

    # --- ASSERT ---
    assert response.status_code == 400
    datos = response.get_json()
    mensaje = datos.get("error", datos.get("message", datos.get("mensaje", "")))
    assert "perfil" in mensaje.lower()