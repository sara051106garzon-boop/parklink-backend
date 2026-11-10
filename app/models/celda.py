from app.database.database import db

class Celda(db.Model):
    __tablename__ = 'celdas'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo_celda = db.Column(db.String(10), unique=True, nullable=False, index=True) # Ej: EL-01, MR-05
    tipo_celda = db.Column(db.String(30), nullable=False)  # "administrativas", "operativas", "movilidad", "eléctricos"
    ocupada = db.Column(db.Boolean, default=False, nullable=False)

    # Ubicación y estado dinámico mostrado en el mapa del parqueadero
    planta = db.Column(db.Integer, default=1, nullable=False)  # 1 = primer piso, 2 = segundo piso, -1 = sótano
    estado = db.Column(db.String(20), nullable=True)  # "libre", "ocupado", "reservado" (None se deriva de `ocupada`)

    # Datos del vehículo estacionado en la celda (se limpian al liberar la celda)
    placa = db.Column(db.String(10), nullable=True)
    usuario = db.Column(db.String(100), nullable=True)
    marca = db.Column(db.String(50), nullable=True)
    modelo = db.Column(db.String(50), nullable=True)
    color_hex = db.Column(db.String(20), nullable=True)
    hora_ingreso = db.Column(db.String(20), nullable=True)  # Ej: "10:30 AM"

    # Relación con accesos activos
    movimientos = db.relationship('Acceso', backref='celda', lazy=True)

    def __repr__(self):
        return f"<Celda {self.codigo_celda} - Ocupada: {self.ocupada}>"