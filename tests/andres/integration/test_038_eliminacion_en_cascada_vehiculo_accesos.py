from app.database.database import db
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.models.acceso import Acceso

def test_eliminacion_en_cascada_vehiculo_accesos(app_con_contexto_de_prueba):
    
    # ==========================================
    # 1. ARRANGE (Preparar el escenario y datos)
    # ==========================================
    # Creamos el usuario dueño
    usuario = Usuario(
        nombre_completo="Carlos Gómez",
        correo="carlos@empresa.com",
        password_hash="hash_de_prueba_123"
    )
    db.session.add(usuario)
    db.session.commit()

    # Creamos el vehículo asociado al usuario
    vehiculo = Vehiculo(
        placa="KTM-123",
        usuario_id=usuario.id,
        tipo_vehiculo="Motocicleta",
        area="Operaciones"
    )
    db.session.add(vehiculo)
    db.session.commit()

    # Creamos dos registros de acceso para ese vehículo
    acceso_entrada = Acceso(
        placa=vehiculo.placa,
        vehiculo_id=vehiculo.id,
        tipo_movimiento="Entrada",
        tipo_vehiculo=vehiculo.tipo_vehiculo
    )
    acceso_salida = Acceso(
        placa=vehiculo.placa,
        vehiculo_id=vehiculo.id,
        tipo_movimiento="Salida",
        tipo_vehiculo=vehiculo.tipo_vehiculo
    )
    db.session.add_all([acceso_entrada, acceso_salida])
    db.session.commit()

    # Verificación previa de que los accesos sí existen antes de borrar
    assert Acceso.query.filter_by(vehiculo_id=vehiculo.id).count() == 2

    # ==========================================
    # 2. ACT (Acción: Eliminar el vehículo)
    # ==========================================
    id_vehiculo_borrado = vehiculo.id
    db.session.delete(vehiculo)
    db.session.commit()

    # ==========================================
    # 3. ASSERT (Verificar que los accesos se borraron)
    # ==========================================
    # A. Comprobamos que el vehículo ya no existe
    vehiculo_en_bd = Vehiculo.query.get(id_vehiculo_borrado)
    assert vehiculo_en_bd is None

    # B. Comprobamos que sus accesos fueron eliminados en cascada por delete-orphan
    accesos_restantes = Acceso.query.filter_by(vehiculo_id=id_vehiculo_borrado).all()
    assert len(accesos_restantes) == 0