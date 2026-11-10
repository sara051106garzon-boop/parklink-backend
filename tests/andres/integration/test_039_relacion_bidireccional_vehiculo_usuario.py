from app.database.database import db
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo

def test_relacion_bidireccional_vehiculo_usuario(app_con_contexto_de_prueba):
    
    # ==========================================
    # 1. ARRANGE (Preparar / Crear los datos de prueba)
    # ==========================================
    # Creamos un usuario de prueba en la base de datos temporal
    nuevo_usuario = Usuario(
        nombre_completo="Carlos Gómez",
        correo="carlos@empresa.com",
        password_hash="hash_de_prueba_123"
    )
    db.session.add(nuevo_usuario)
    db.session.commit() # Se guarda para que tenga un ID asignado (ej. ID: 1)

    # Creamos un vehículo y lo asociamos usando el ID del usuario
    nuevo_vehiculo = Vehiculo(
        placa="XYZ-999",
        usuario_id=nuevo_usuario.id,
        tipo_vehiculo="Automóvil",
        area="Sistemas"
    )
    db.session.add(nuevo_vehiculo)
    db.session.commit()

    # ==========================================
    # 2. ACT (Acción / Navegar por las relaciones)
    # ==========================================
    # No necesitamos ejecutar una función compleja, 
    # solo consultamos los objetos de la base de datos para probar la conexión
    vehiculo_consultado = Vehiculo.query.filter_by(placa="XYZ-999").first()
    usuario_consultado = Usuario.query.filter_by(correo="carlos@empresa.com").first()

    # ==========================================
    # 3. ASSERT (Afirmar / Verificar la bidireccionalidad)
    # ==========================================
    # A. Dirección Vehículo -> Usuario: Desde el carro, ¿llegamos al dueño?
    assert vehiculo_consultado.usuario.nombre_completo == "Carlos Gómez"
    assert vehiculo_consultado.usuario.correo == "carlos@empresa.com"

    # B. Dirección Usuario -> Vehículo: Desde el usuario, ¿llegamos a su carro usando el backref?
    assert len(usuario_consultado.vehiculos) == 1
    assert usuario_consultado.vehiculos[0].placa == "XYZ-999"