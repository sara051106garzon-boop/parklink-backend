"""UNIT 045 · Admin · Validar cupo rechaza un tipo de usuario que no existe."""

from app.database.database import db
from app.models.configuracion import Configuracion


def test_validar_cupo_rechaza_perfil_no_valido(client_de_diego, headers_admin, test_database):
    """Un `tipo_usuario` desconocido responde 400 con el motivo del perfil."""
    # Arrange
    db.session.add(Configuracion())
    db.session.commit()

    payload_validacion = {
        "placa": "XYZ-999",
        "tipo_usuario": "visitante",
        "planta": 1
    }

    # Act
    response = client_de_diego.post(
        "/api/admin/ingresos/validar-cupo",
        json=payload_validacion,
        headers=headers_admin
    )

    # Assert
    assert response.status_code == 400
    datos = response.get_json()
    mensaje = datos.get("error", datos.get("message", datos.get("mensaje", "")))
    assert "perfil" in mensaje.lower()
