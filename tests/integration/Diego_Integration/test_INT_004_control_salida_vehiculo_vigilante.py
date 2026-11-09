"""Integración de la salida de vehículos en el módulo de vigilancia."""

from flask_jwt_extended import create_access_token

from app.models.acceso import Acceso
from app.models.celda import Celda
from app.models.turno import Turno
from app.models.usuario import RolEnum, Usuario
from app.models.vehiculo import Vehiculo


def test_segunda_salida_es_rechazada_sin_alterar_estado(
    client, app, db_session
):
    """INT-004 | Severidad: Alta. Una segunda salida no debe duplicar movimientos."""
    # Arrange
    with app.app_context():
        vigilante = Usuario(
            nombre_completo="Luis Guardia",
            correo="luis.guardia@parklink.com",
            rol=RolEnum.VIGILANTE,
            activo=True,
        )
        vigilante.password = "ClaveSegura123!"
        db_session.add(vigilante)
        db_session.flush()

        vehiculo = Vehiculo(
            placa="XYZ987",
            usuario_id=vigilante.id,
            tipo_vehiculo="carro",
            area="Funcionario",
        )
        turno = Turno(usuario_id=vigilante.id, estado="Activo")
        celda = Celda(
            codigo_celda="P1-01",
            tipo_celda="carro",
            ocupada=True,
        )
        db_session.add_all([vehiculo, turno, celda])
        db_session.flush()

        db_session.add(Acceso(
            placa=vehiculo.placa,
            vehiculo_id=vehiculo.id,
            tipo_movimiento="Entrada",
            tipo_vehiculo=vehiculo.tipo_vehiculo,
            tipo_usuario="Funcionario",
            celda_id=celda.id,
            celda_asignada=celda.codigo_celda,
            turno_id=turno.id,
        ))
        db_session.commit()

        vigilante_id = vigilante.id
        vehiculo_id = vehiculo.id
        token = create_access_token(identity=str(vigilante_id))
        placa = vehiculo.placa

    headers = {"Authorization": f"Bearer {token}"}

    # Act
    primera_respuesta = client.post(
        "/api/vigilante/salida",
        json={"placa": placa},
        headers=headers,
    )
    segunda_respuesta = client.post(
        "/api/vigilante/salida",
        json={"placa": placa},
        headers=headers,
    )

    # Assert
    assert primera_respuesta.status_code == 201
    assert segunda_respuesta.status_code == 400
    assert segunda_respuesta.get_json()["error"] == "El vehículo ya salió del parqueadero"
    assert db_session.query(Acceso).filter_by(vehiculo_id=vehiculo_id).count() == 2
    turno_actualizado = db_session.query(Turno).filter_by(usuario_id=vigilante_id).one()
    assert turno_actualizado.total_salidas == 1
    celda_actualizada = db_session.query(Celda).filter_by(codigo_celda="P1-01").one()
    assert celda_actualizada.ocupada is False
