from app.database.database import db
from app.models.turno import Turno
from app.models.usuario import RolEnum, Usuario
from app.models.vehiculo import Vehiculo


def test_salida_vigilante_error_de_negocio_devuelve_400(client, headers_vigilante, test_database):
    # --- ARRANGE ---
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

    # --- ACT ---
    response = client.post(
        "/api/vigilante/salida",
        json=payload_salida,
        headers=headers_vigilante
    )

    # --- ASSERT ---
    assert response.status_code == 400
    datos = response.get_json()
    assert datos.get("error") == "El vehículo nunca ha ingresado"