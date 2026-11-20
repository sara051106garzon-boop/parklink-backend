"""Integración de la API REST de reservas con SQLAlchemy."""

from datetime import date, time, timedelta

from flask_jwt_extended import create_access_token

from app.models.reserva import Reserva
from app.models.usuario import RolEnum, Usuario
from app.models.vehiculo import Vehiculo


def test_crear_reserva_persiste_datos_en_bd(client_de_diego, app, db_session):
    """INT 051 | Severidad: Alta. Reserva válida debe quedar persistida."""
    # Arrange
    with app.app_context():
        usuario = Usuario(
            nombre_completo="Carlos Ruiz",
            correo="carlos@parklink.com",
            rol=RolEnum.USUARIO,
            activo=True,
        )
        usuario.password = "ClaveSegura123!"
        db_session.add(usuario)
        db_session.flush()

        vehiculo = Vehiculo(
            placa="ABC123",
            usuario_id=usuario.id,
            tipo_vehiculo="carro",
            marca="Toyota",
            area="Funcionario",
        )
        db_session.add(vehiculo)
        db_session.commit()

        usuario_id = usuario.id
        vehiculo_id = vehiculo.id
        token = create_access_token(identity=str(usuario_id))

    fecha_reserva = date.today() + timedelta(days=2)
    payload = {
        "vehiculo_id": vehiculo_id,
        "fecha": fecha_reserva.isoformat(),
        "hora": "10:30",
    }

    # Act
    response = client_de_diego.post(
        "/api/usuario/reservas",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    # Assert
    assert response.status_code == 201
    data = response.get_json()
    assert data["reserva"]["fecha"] == payload["fecha"]
    assert data["reserva"]["hora"] == payload["hora"]

    reserva = db_session.query(Reserva).filter_by(usuario_id=usuario_id).one()
    assert reserva.vehiculo_id == vehiculo_id
    assert reserva.fecha == fecha_reserva
    assert reserva.hora == time(10, 30)
    assert reserva.estado == "Pendiente"
