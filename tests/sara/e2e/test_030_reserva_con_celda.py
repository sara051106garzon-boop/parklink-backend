# tests/sara/e2e/test_030_reserva_con_celda.py
"""
E2E 030 · Reservas · Elegir una celda específica debe respetarse.

Usa el fixture ``cliente_con_bd`` (SQLite en memoria) porque el flujo real
guarda la reserva y marca la celda como ocupada.
"""

from datetime import date, timedelta

from app.database.database import db
from app.models.celda import Celda
from app.models.reserva import Reserva
from app.models.usuario import RolEnum, Usuario
from app.models.vehiculo import Vehiculo


def test_reserva_con_celda_la_guarda_y_la_marca_como_reservada(cliente_con_bd):
    """Si el usuario elige una celda, la reserva debe quedar atada a ella."""
    # Arrange
    usuario = Usuario(
        nombre_completo="Sara Prueba",
        correo="sara@parklink.com",
        rol=RolEnum.USUARIO,
        activo=True,
    )
    usuario.password = "Parklink2026*"
    db.session.add(usuario)
    db.session.commit()

    vehiculo = Vehiculo(
        placa="ABC123",
        usuario_id=usuario.id,
        tipo_vehiculo="Automóvil",
        area="Funcionario",
    )
    celda_elegida = Celda(codigo_celda="A-02", tipo_celda="administrativas", ocupada=False)
    db.session.add_all([vehiculo, celda_elegida])
    db.session.commit()

    login = cliente_con_bd.post(
        "/api/auth/login",
        json={"correo": "sara@parklink.com", "password": "Parklink2026*"},
    )
    cabeceras = {"Authorization": f"Bearer {login.get_json()['token']}"}

    # La reserva debe ser para mañana: el servicio no acepta fechas pasadas.
    datos = {
        "vehiculo_id": vehiculo.id,
        "fecha": (date.today() + timedelta(days=1)).isoformat(),
        "hora": "10:00",
        "celda_id": celda_elegida.codigo_celda,
    }

    # Act
    respuesta = cliente_con_bd.post("/api/usuario/reservas", json=datos, headers=cabeceras)
    reserva = Reserva.query.filter_by(usuario_id=usuario.id).first()

    # Assert
    assert respuesta.status_code == 201, respuesta.get_json()
    assert respuesta.get_json()["reserva"]["celda"] == "A-02"
    assert reserva is not None and reserva.celda_id == celda_elegida.id
    assert db.session.get(Celda, celda_elegida.id).ocupada is True
