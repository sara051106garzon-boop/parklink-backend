# API — ParkLink Back-End

Referencia de todos los endpoints expuestos por el servidor.

- **URL base local:** `http://127.0.0.1:5000`
- **Formato:** JSON (`Content-Type: application/json`)
- **Autenticación:** JWT en el header `Authorization: Bearer <token>`
- **Roles:** `ADMIN` · `VIGILANTE` · `USUARIO`

---

## Autenticación

### `POST /api/auth/login`

Inicia sesión y devuelve el token JWT.

```json
{
  "correo": "sara@parklink.com",
  "password": "MiClave123"
}
```

**Respuesta `200`**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "usuario": {
    "id": 1,
    "nombre_completo": "Sara Garzón",
    "correo": "sara@parklink.com",
    "rol": "ADMIN"
  }
}
```

### `GET /api/auth/perfil`

Devuelve los datos del usuario autenticado. **Requiere token.**

---

## Administrador

| Método | Ruta | Qué hace |
| :--- | :--- | :--- |
| `POST` | `/api/admin/registrar-usuario` | Crea un usuario con rol asignado |
| `GET` | `/api/admin/vehiculos` | Lista los vehículos registrados |
| `POST` | `/api/admin/vehiculos` | Vincula un vehículo a un usuario |
| `DELETE` | `/api/admin/vehiculos/{id}` | Elimina un vehículo |
| `POST` | `/api/admin/ingresos/validar-cupo` | Comprueba si hay cupo disponible antes de ingresar |
| `GET` | `/api/admin/kpis` | Métricas del dashboard (ocupación, ingresos, salidas) |
| `GET` | `/api/admin/kpis-ocupacion` | KPIs específicos de ocupación por tipo de celda |

### Celdas

| Método | Ruta | Qué hace |
| :--- | :--- | :--- |
| `GET` | `/api/admin/celdas` | Mapa completo de celdas y su estado |
| `POST` | `/api/admin/celdas` | Registra una celda nueva |
| `PUT` | `/api/admin/celdas/{id}/estado` | Cambia el estado de la celda |
| `POST` | `/api/admin/celdas/{id}/ocupar` | Marca la celda como ocupada |
| `POST` | `/api/admin/celdas/{id}/liberar` | Marca la celda como libre |
| `PATCH` | `/api/admin/celdas/{id}/reserva` | Activa o desactiva la reserva |
| `DELETE` | `/api/admin/celdas/{id}` | Elimina la celda |

### Accesos e historial

| Método | Ruta | Qué hace |
| :--- | :--- | :--- |
| `GET` | `/api/admin/historial` | Historial de entradas y salidas |
| `POST` | `/api/admin/registrar-acceso` | Registra un movimiento manualmente |

### Alertas

| Método | Ruta | Qué hace |
| :--- | :--- | :--- |
| `GET` | `/api/admin/alertas` | Lista las alertas publicadas |
| `POST` | `/api/admin/alertas` | Publica una alerta (`informativo`, `advertencia`, `urgente`) |
| `DELETE` | `/api/admin/alertas/{id}` | Elimina una alerta |

### Analítica y auditoría

| Método | Ruta | Qué hace |
| :--- | :--- | :--- |
| `GET` | `/api/admin/tendencias` | Tendencias de ocupación en el tiempo |
| `GET` | `/api/admin/logs` | Log de auditoría de acciones |
| `GET` | `/api/admin/config` | Configuración actual del parqueadero |
| `PUT` / `POST` | `/api/admin/config` | Actualiza horarios, cupos y políticas |

---

## Vigilante

| Método | Ruta | Qué hace |
| :--- | :--- | :--- |
| `POST` | `/api/vigilante/apertura-turno` | Abre el turno del vigilante |
| `POST` | `/api/vigilante/cierre-turno` | Cierra el turno y guarda el resumen |
| `GET` | `/api/vigilante/turnos` | Lista los turnos del vigilante |
| `GET` | `/api/vigilante/resumen-turno` | Resumen del turno activo |
| `POST` | `/api/vigilante/entrada` | Registra la entrada de un vehículo |
| `POST` | `/api/vigilante/salida` | Registra la salida de un vehículo |
| `GET` | `/api/vigilante/vehiculos-activos` | Vehículos dentro del parqueadero |
| `GET` | `/api/vigilante/historial-turno` | Movimientos del turno |
| `GET` | `/api/vigilante/vehiculo/{placa}` | Busca un vehículo por placa |
| `GET` | `/api/vigilante/visitantes` | Lista los visitantes registrados |
| `POST` | `/api/vigilante/visitantes` | Registra un visitante |
| `GET` | `/api/vigilante/novedades` | Novedades reportadas |
| `POST` | `/api/vigilante/novedades` | Reporta una novedad |

---

## Usuario

| Método | Ruta | Qué hace |
| :--- | :--- | :--- |
| `GET` | `/api/usuario/panel` | Datos del panel principal |
| `GET` | `/api/usuario/perfil` | Perfil del usuario |
| `PUT` | `/api/usuario/cambiar-password` | Cambia la contraseña |
| `GET` | `/api/usuario/vehiculos` | Vehículos del usuario |
| `POST` | `/api/usuario/vehiculos` | Registra un vehículo propio |
| `GET` | `/api/usuario/reservas` | Reservas del usuario |
| `POST` | `/api/usuario/reservas` | Crea una reserva de celda |
| `GET` | `/api/usuario/historial` | Historial de accesos del usuario |
| `GET` | `/api/usuario/notificaciones` | Notificaciones y alertas |

---

## Reportes

| Método | Ruta | Qué hace |
| :--- | :--- | :--- |
| `GET` | `/api/reportes/exportar` | Exporta el historial en el formato pedido |
| `GET` | `/api/reportes/historial/excel` | Descarga el historial en Excel |
| `GET` | `/api/reportes/historial/pdf` | Descarga el historial en PDF |

---

## Estado del servicio

| Método | Ruta | Qué hace |
| :--- | :--- | :--- |
| `GET` | `/health` | Comprueba que el servidor responde (no requiere token) |

```json
{ "status": "ok", "service": "parklink-backend" }
```

---

## Códigos de respuesta

| Código | Significado |
| :--- | :--- |
| `200` | Operación exitosa |
| `201` | Recurso creado |
| `400` | Datos inválidos o incompletos |
| `401` | Falta el token o es inválido/expirado |
| `403` | El rol del usuario no tiene permiso |
| `404` | El recurso no existe |
| `409` | Conflicto (placa o correo duplicado) |
| `500` | Error interno del servidor |

---

## Ejemplo completo

```bash
# 1. Iniciar sesión
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"correo":"sara@parklink.com","password":"MiClave123"}'

# 2. Usar el token en una ruta protegida
curl http://127.0.0.1:5000/api/admin/kpis \
  -H "Authorization: Bearer <TOKEN>"
```

---

## Total

**52 endpoints** distribuidos en 7 módulos, más el chequeo de salud del servicio.
