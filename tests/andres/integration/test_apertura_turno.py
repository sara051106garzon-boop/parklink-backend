from datetime import datetime

from app.database.database import db
from app.models.log_auditoria import LogAuditoria
from app.models.turno import Turno
from app.models.usuario import Usuario
from app.services.vigilante_service import abrir_turno


def test_apertura_turno_crea_turno_activo_y_registra_log(app_con_contexto_de_prueba):

    # ==========================================
    # 1. ARRANGE (Preparar el escenario)
    # ==========================================
    # Creamos el vigilante que abrirá el turno
    vigilante = Usuario(
        nombre_completo="Pedro Vigilante",
        correo="pedro.vigilante@empresa.com",
        password_hash="hash_de_prueba_123"
    )
    db.session.add(vigilante)
    db.session.commit()

    momento_antes = datetime.utcnow()

    # ==========================================
    # 2. ACT (Ejecutar la acción a probar)
    # ==========================================
    respuesta = abrir_turno(vigilante.id)

    # ==========================================
    # 3. ASSERT (Verificar los resultados)
    # ==========================================
    # A. La función confirma la apertura
    assert respuesta == "Turno abierto correctamente"

    # B. Se creó un turno en estado "Activo" para el vigilante
    turno = Turno.query.filter_by(usuario_id=vigilante.id).first()
    assert turno is not None
    assert turno.estado == "Activo"
    assert turno.usuario_id == vigilante.id

    # C. Se registró la fecha de apertura
    assert turno.fecha_apertura is not None
    assert turno.fecha_apertura >= momento_antes

    # D. Se disparó un log informativo asociado a la apertura del turno
    log = LogAuditoria.query.filter_by(
        usuario_id=vigilante.id,
        modulo="Turnos"
    ).first()
    assert log is not None
    assert log.nivel == "informativo"
    assert log.descripcion == "Se abrió un turno"


def test_apertura_turno_rechaza_si_ya_existe_un_turno_activo(app_con_contexto_de_prueba):

    # ==========================================
    # 1. ARRANGE (Preparar el escenario)
    # ==========================================
    # Creamos el vigilante que ya tiene un turno activo
    vigilante = Usuario(
        nombre_completo="Pedro Vigilante",
        correo="pedro.vigilante@empresa.com",
        password_hash="hash_de_prueba_123"
    )
    db.session.add(vigilante)
    db.session.commit()

    turno_activo = Turno(
        usuario_id=vigilante.id,
        jornada="Mañana",
        estado="Activo"
    )
    db.session.add(turno_activo)
    db.session.commit()

    # ==========================================
    # 2. ACT (Intentar abrir un segundo turno)
    # ==========================================
    respuesta = abrir_turno(vigilante.id)

    # ==========================================
    # 3. ASSERT (Verificar que se rechazó la apertura)
    # ==========================================
    # A. La función informa que ya existe un turno activo
    assert respuesta == "Ya existe un turno activo"

    # B. No se creó un turno adicional para el vigilante
    turnos_del_usuario = Turno.query.filter_by(
        usuario_id=vigilante.id
    ).all()
    assert len(turnos_del_usuario) == 1
    assert turnos_del_usuario[0].id == turno_activo.id
    assert turnos_del_usuario[0].estado == "Activo"

    # C. No se registró un log de apertura porque la operación fue rechazada
    logs = LogAuditoria.query.filter_by(
        usuario_id=vigilante.id,
        modulo="Turnos"
    ).all()
    assert len(logs) == 0
