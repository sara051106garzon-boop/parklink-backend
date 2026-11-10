"""
ParkLink - Servicio para el cálculo de KPIs de ocupación del parqueadero.
Capa de negocio (Service Layer).
"""

from app.database.database import db
from app.models.celda import Celda
from app.models.vehiculo import Vehiculo
from app.models.acceso import Acceso
from app.models.alertas import Alerta
from app.models.configuracion import Configuracion

# Límites por defecto cuando todavía no existe fila en `configuraciones`.
LIMITES_POR_DEFECTO = {
    "admin": 40,
    "operativas": 60,
    "movilidad": 10,
}


def _limites_configuracion():
    """
    Lee los límites de capacidad por perfil desde la configuración global.

    Retorna un diccionario ``{"admin": int, "operativas": int, "movilidad": int}``.
    Si no hay fila de configuración, usa los valores por defecto del sistema.
    """
    config = Configuracion.query.first()
    if not config:
        return dict(LIMITES_POR_DEFECTO)

    return {
        "admin": getattr(config, "celdas_admin", LIMITES_POR_DEFECTO["admin"]) or 0,
        "operativas": getattr(config, "celdas_operativas", LIMITES_POR_DEFECTO["operativas"]) or 0,
        "movilidad": getattr(config, "celdas_movilidad", LIMITES_POR_DEFECTO["movilidad"]) or 0,
    }


def _accesos_activos():
    """
    Retorna los accesos de vehículos que siguen DENTRO del parqueadero.

    Regla: por cada vehículo se mira su último movimiento; si fue una
    "Entrada", el vehículo sigue adentro.
    """
    vistos = set()
    activos = []

    for acceso in Acceso.query.order_by(Acceso.fecha_hora.desc()).all():
        if acceso.vehiculo_id in vistos:
            continue
        vistos.add(acceso.vehiculo_id)
        if acceso.tipo_movimiento == "Entrada":
            activos.append(acceso)

    return activos


def calcular_metricas():
    """
    Calcula las métricas de ocupación del parqueadero.

    Si la capacidad configurada es 0 (o no hay celdas), los porcentajes se
    devuelven en 0 en lugar de lanzar ``ZeroDivisionError``.
    """
    # 1. Capacidad parametrizada por perfil
    limites = _limites_configuracion()
    capacidad_total = sum(limites.values())

    # 2. Ocupación actual según los accesos activos (vehículos dentro)
    accesos = _accesos_activos()
    ocupacion_total = len(accesos)

    # 3. Porcentaje global seguro contra división por cero
    porcentaje_ocupacion = (
        round((ocupacion_total / capacidad_total) * 100, 1)
        if capacidad_total > 0
        else 0
    )

    # 4. Métricas complementarias del parqueadero
    celdas = Celda.query.all()
    celdas_ocupadas = [c for c in celdas if getattr(c, "ocupada", False)]

    vehiculos = Vehiculo.query.all()
    motos = sum(
        1
        for v in vehiculos
        if "moto" in str(getattr(v, "tipo_vehiculo", "") or "").lower()
    )
    carros = len(vehiculos) - motos

    try:
        total_alertas = Alerta.query.count()
    except Exception:
        total_alertas = 0

    return {
        "capacidad_total": capacidad_total,
        "ocupacion_total": ocupacion_total,
        "porcentaje_ocupacion": porcentaje_ocupacion,
        "celdas_totales": len(celdas),
        "celdas_ocupadas": len(celdas_ocupadas),
        "celdas_libres": len(celdas) - len(celdas_ocupadas),
        "vehiculos_registrados": len(vehiculos),
        "total_carros": carros,
        "total_motos": motos,
        "alertas_activas": total_alertas,
    }
