# tests/andres/e2e/test_operacion_vigilante.py
"""
E2E · Vigilante · Turno completo con entrada, consulta y salida de un vehículo.

Usa el fixture ``cliente_con_bd``: base SQLite en memoria con tablas reales,
así cubre login → apertura de turno → entrada → vehículos activos → salida →
cierre de turno sin depender de MySQL.
"""

from app.database.database import db
from app.models.celda import Celda
from app.models.usuario import RolEnum, Usuario
from app.models.vehiculo import Vehiculo


def test_flujo_completo_operacion_vigilancia(cliente_con_bd):
    """El vigilante debe registrar entrada y salida de un vehículo dentro de su turno."""
    # Arrange: vigilante, dueño del vehículo y una celda libre.
    vigilante = Usuario(
        nombre_completo="Guarda Porteria",
        correo="vigilante@empresa.com",
        activo=True,
        rol=RolEnum.VIGILANTE,
    )
    vigilante.password = "Seguridad2026*"

    usuario = Usuario(
        nombre_completo="Ana Ruiz",
        correo="ana@empresa.com",
        activo=True,
        rol=RolEnum.USUARIO,
    )
    usuario.password = "Clave123*"

    celda = Celda(
        codigo_celda="B-201",
        tipo_celda="operativas",
        ocupada=False,
        estado="libre",
    )

    db.session.add_all([vigilante, usuario, celda])
    db.session.flush()

    vehiculo = Vehiculo(
        placa="KHM321",
        tipo_vehiculo="Automóvil",
        area="Funcionario",
        usuario_id=usuario.id,
    )
    db.session.add(vehiculo)
    db.session.commit()

    # Act 1: login del vigilante.
    login_resp = cliente_con_bd.post(
        "/api/auth/login",
        json={"correo": "vigilante@empresa.com", "password": "Seguridad2026*"},
    )
    assert login_resp.status_code == 200, login_resp.get_json()
    headers = {"Authorization": f"Bearer {login_resp.get_json()['token']}"}

    # Act 2: apertura del turno.
    apertura_resp = cliente_con_bd.post("/api/vigilante/apertura-turno", headers=headers)
    assert apertura_resp.status_code == 201, apertura_resp.get_json()

    # Act 3: registro de entrada del vehículo.
    entrada_resp = cliente_con_bd.post(
        "/api/vigilante/entrada",
        headers=headers,
        json={"placa": "KHM321"},
    )
    assert entrada_resp.status_code == 201, entrada_resp.get_json()

    # Assert intermedio: el vehículo figura dentro del parqueadero.
    activos_resp = cliente_con_bd.get("/api/vigilante/vehiculos-activos", headers=headers)
    assert activos_resp.status_code == 200
    assert "KHM321" in [vehiculo["placa"] for vehiculo in activos_resp.get_json()]

    # Act 4: registro de salida del vehículo.
    salida_resp = cliente_con_bd.post(
        "/api/vigilante/salida",
        headers=headers,
        json={"placa": "KHM321"},
    )
    assert salida_resp.status_code == 201, salida_resp.get_json()

    # Act 5: cierre del turno.
    cierre_resp = cliente_con_bd.post("/api/vigilante/cierre-turno", headers=headers)
    assert cierre_resp.status_code == 200, cierre_resp.get_json()
