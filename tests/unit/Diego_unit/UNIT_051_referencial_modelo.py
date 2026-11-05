import pytest
from sqlalchemy.exc import IntegrityError
from app.database.database import db
from app.models.vehiculo import Vehiculo

def test_modelo_vehiculo_exige_propietario_existente(app_context):
    # --- ARRANGE (Preparar) ---
    usuario_id_inexistente = 9999
    nuevo_vehiculo = Vehiculo(
        placa="KLR987",
        marca="Toyota",
        modelo="Corolla",
        tipo_vehiculo="carro",
        usuario_id=usuario_id_inexistente
    )

    # --- ACT & ASSERT (Actuar y Afirmar) ---
    with pytest.raises(IntegrityError):
        db.session.add(nuevo_vehiculo)
        db.session.commit()
    
    # Revertir la transacción fallida
    db.session.rollback()