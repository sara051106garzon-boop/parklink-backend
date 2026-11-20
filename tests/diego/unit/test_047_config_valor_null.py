"""UNIT 047 · Configuraciones · Un valor `null` en un entero se rechaza con 400."""

from app.database.database import db
from app.models.configuracion import Configuracion


def test_config_put_valor_null_devuelve_400(client_de_diego, headers_admin, test_database):
    """La configuración de cupos no admite `null`: responde 400."""
    # Arrange
    db.session.add(Configuracion())
    db.session.commit()

    payload_invalido = {
        "celdas_admin": None
    }

    # Act
    response = client_de_diego.put(
        "/api/admin/config",
        json=payload_invalido,
        headers=headers_admin
    )

    # Assert
    assert response.status_code == 400, (
        f"Se esperaba HTTP 400 por valor 'null' en entero, pero devolvió HTTP {response.status_code}"
    )
