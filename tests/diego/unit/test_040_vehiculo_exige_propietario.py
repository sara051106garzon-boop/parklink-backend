"""UNIT 040 · Vehiculo · Un vehículo no puede existir sin su propietario."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.database.database import db
from app.models.vehiculo import Vehiculo


def test_modelo_vehiculo_exige_propietario_existente(app_context, test_database):
    """La llave foránea rechaza un vehículo cuyo usuario no existe."""
    # Arrange
    usuario_id_inexistente = 9999
    nuevo_vehiculo = Vehiculo(
        placa="KLR987",
        marca="Toyota",
        tipo_vehiculo="carro",
        area="Funcionario",
        usuario_id=usuario_id_inexistente
    )

    # Act / Assert
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        db.session.add(nuevo_vehiculo)
        db.session.commit()

    db.session.rollback()
