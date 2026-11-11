"""INTEGRATION 051 · crear_reserva + cancelar_reserva · Cancelar libera la celda reservada.

Usa SQLite en memoria (``app_con_contexto_de_prueba``) para recorrer el
servicio con datos reales: usuario, vehículo, celda y reserva.
"""

from datetime import date, timedelta

from app.database.database import db
from app.models.celda import Celda
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.services.reserva_service import cancelar_reserva, crear_reserva


def test_cancelar_reserva_pendiente_marca_cancelada_y_libera_la_celda(app_con_contexto_de_prueba):
    """Tras cancelar, la reserva queda 'Cancelada' y la celda vuelve a estar libre."""
    # Arrange
    usuario = Usuario(
        nombre_completo="Ana Pérez", correo="ana@empresa.com", password_hash="hash_de_prueba"
    )
    celda = Celda(codigo_celda="OP-01", tipo_celda="operativas")
    db.session.add_all([usuario, celda])
    db.session.commit()
    vehiculo = Vehiculo(
        placa="ABC123", usuario_id=usuario.id, tipo_vehiculo="Automóvil", area="Operaciones"
    )
    db.session.add(vehiculo)
    db.session.commit()

    creada = crear_reserva(
        usuario.id,
        {
            "vehiculo_id": vehiculo.id,
            "fecha": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "hora": "10:00",
            "celda_id": celda.id,
        },
    )
    reserva_id = creada["reserva"]["id"]
    assert celda.ocupada is True  # la reserva sí había bloqueado la celda

    # Act
    resultado = cancelar_reserva(usuario.id, reserva_id)

    # Assert
    assert resultado == {"mensaje": "Reserva cancelada exitosamente."}
    assert db.session.get(Reserva, reserva_id).estado == "Cancelada"
    assert db.session.get(Celda, celda.id).ocupada is False
    assert db.session.get(Celda, celda.id).estado == "libre"
