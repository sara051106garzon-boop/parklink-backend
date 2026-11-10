# tests/andres/e2e/test_reserva_funcionario.py
"""
E2E · Reservas · Un funcionario registra su vehículo y reserva una celda.

Usa el fixture ``cliente_con_bd``: base SQLite en memoria con tablas reales,
así cubre el camino completo login → registro de vehículo → reserva → historial.
"""

from datetime import date, timedelta

from app.database.database import db
from app.models.celda import Celda
from app.models.usuario import RolEnum, Usuario
from app.models.vehiculo import Vehiculo


def test_flujo_completo_reserva_usuario(cliente_con_bd):
    """El funcionario debe reservar una celda y verla reflejada en su historial."""
    # Arrange: usuario con contraseña real (hash Bcrypt) y una celda libre.
    usuario = Usuario(
        nombre_completo="Carlos Gomez",
        correo="carlos@empresa.com",
        activo=True,
        rol=RolEnum.USUARIO,
    )
    usuario.password = "Password123*"

    celda = Celda(
        codigo_celda="A-101",
        tipo_celda="administrativas",
        ocupada=False,
        estado="libre",
    )

    db.session.add_all([usuario, celda])
    db.session.commit()

    # Act 1: login real para obtener el token JWT.
    login_resp = cliente_con_bd.post(
        "/api/auth/login",
        json={"correo": "carlos@empresa.com", "password": "Password123*"},
    )
    assert login_resp.status_code == 200, login_resp.get_json()
    headers = {"Authorization": f"Bearer {login_resp.get_json()['token']}"}

    # Act 2: registro del vehículo propio.
    vehiculo_resp = cliente_con_bd.post(
        "/api/usuario/vehiculos",
        headers=headers,
        json={
            "placa": "XYZ789",
            "tipo_vehiculo": "Automóvil",
            "marca": "Mazda",
            "color": "Gris",
        },
    )
    assert vehiculo_resp.status_code == 201, vehiculo_resp.get_json()

    vehiculo = Vehiculo.query.filter_by(placa="XYZ789").first()

    # Act 3: reserva para mañana (el servicio no acepta fechas pasadas).
    reserva_resp = cliente_con_bd.post(
        "/api/usuario/reservas",
        headers=headers,
        json={
            "vehiculo_id": vehiculo.id,
            "fecha": (date.today() + timedelta(days=1)).isoformat(),
            "hora": "08:00",
            "celda_id": celda.codigo_celda,
        },
    )

    # Assert: la reserva queda creada con la celda elegida.
    assert reserva_resp.status_code == 201, reserva_resp.get_json()
    assert reserva_resp.get_json()["reserva"]["celda"] == "A-101"

    # Assert: el historial del usuario incluye la reserva del vehículo.
    historial_resp = cliente_con_bd.get("/api/usuario/reservas", headers=headers)
    assert historial_resp.status_code == 200
    assert [reserva["placa"] for reserva in historial_resp.get_json()] == ["XYZ789"]
