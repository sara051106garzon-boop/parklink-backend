"""UNIT 048 · Vigilante · Salida de un vehículo que nunca ingresó devuelve 400."""

from app.database.database import db
from app.models.turno import Turno
from app.models.usuario import RolEnum, Usuario
from app.models.vehiculo import Vehiculo


def test_salida_vigilante_error_de_negocio_devuelve_400(client_de_diego, headers_vigilante, test_database):
    """No se puede registrar la salida de un vehículo sin ingreso previo."""
    # Arrange
    payload_salida = {
        "placa": "ABC123"
    }

    usuario = Usuario(
        id=1,
        nombre_completo="Vigilante de prueba",
        correo="vigilante@parklink.com",
        password_hash="hash-de-prueba",
        rol=RolEnum.VIGILANTE,
        activo=True
    )
    db.session.add(usuario)
    db.session.flush()
    db.session.add_all([
        Vehiculo(
            placa="ABC123",
            usuario_id=usuario.id,
            tipo_vehiculo="carro",
            area="Funcionario"
        ),
        Turno(usuario_id=usuario.id, estado="Activo")
    ])
    db.session.commit()

    # Act
    response = client_de_diego.post(
        "/api/vigilante/salida",
        json=payload_salida,
        headers=headers_vigilante
    )

    # Assert
    assert response.status_code == 400
    datos = response.get_json()
    assert datos.get("error") == "El vehículo nunca ha ingresado"
