# Arquitectura — ParkLink Back-End

Este documento explica cómo está construido el sistema y cómo se comunican sus
partes. Está pensado para que alguien que llega nuevo entienda el proyecto sin
leer el código.

---

## 1. Visión general

ParkLink es un sistema de gestión de parqueaderos con tres clientes y un solo
back-end:

```mermaid
flowchart LR
    subgraph Clientes
        A["App móvil<br/>Flutter"]
        B["Panel web<br/>Administrador"]
        C["Consola<br/>Vigilante"]
    end

    subgraph "Back-end (Flask)"
        D["API REST<br/>Blueprints por módulo"]
        E["Middlewares<br/>JWT + roles"]
        F["Servicios<br/>Reglas de negocio"]
    end

    subgraph Datos
        G[("MySQL<br/>SQLAlchemy + Alembic")]
    end

    A -->|"HTTPS · JSON"| E
    B -->|"HTTPS · JSON"| E
    C -->|"HTTPS · JSON"| E
    E --> D
    D --> F
    F --> G
```

**Puntos clave**

| Aspecto | Decisión |
|---|---|
| Autenticación | JWT en el header `Authorization: Bearer <token>` |
| Autorización | Rol del usuario (`ADMIN`, `VIGILANTE`, `USUARIO`) validado en el middleware |
| Persistencia | MySQL vía SQLAlchemy; migraciones versionadas con Alembic |
| Tiempo real | Flask-SocketIO para notificaciones y cambios de estado |
| Pruebas | pytest, separadas por integrante en `tests/<persona>/` |
| CI | GitHub Actions ejecuta `pytest` en cada push y bloquea el merge a `main` |

---

## 2. Capas del back-end

```mermaid
flowchart TD
    R["routes/<br/>Define las URLs y recibe la petición"]
    M["middlewares/<br/>Verifica el token y el rol"]
    C["controllers/<br/>Valida los datos de entrada"]
    S["services/<br/>Aplica las reglas del negocio"]
    MD["models/<br/>Representa las tablas"]
    DB[("MySQL")]

    R --> M --> C --> S --> MD --> DB
```

| Carpeta | Responsabilidad | Ejemplo |
|---|---|---|
| `app/routes/` | Un blueprint por módulo; no contiene lógica | `celdas.py` |
| `app/middlewares/` | `roles.py` decide quién puede entrar | `requiere_rol("ADMIN")` |
| `app/controllers/` | Traduce la petición a llamadas del servicio | `auth_controller.py` |
| `app/services/` | Reglas de negocio reutilizables | `vehiculo_service.py` |
| `app/models/` | Entidades y relaciones | `usuario.py` |
| `app/config/` | Variables por entorno | `settings.py` |

---

## 3. Modelo de datos

```mermaid
erDiagram
    USUARIOS ||--o{ VEHICULOS : "registra"
    USUARIOS ||--o{ TURNOS : "abre"
    USUARIOS ||--o{ RESERVAS : "solicita"
    USUARIOS ||--o{ LOGS_AUDITORIA : "genera"

    VEHICULOS ||--o{ ACCESOS : "protagoniza"
    VEHICULOS ||--o{ RESERVAS : "reserva"

    CELDAS ||--o{ ACCESOS : "ocupa"

    TURNOS ||--o{ ACCESOS : "agrupa"
    TURNOS ||--o{ NOVEDADES : "reporta"

    USUARIOS {
        int id PK
        string nombre_completo
        string correo UK
        string password_hash
        enum rol
        boolean activo
        datetime created_at
    }

    VEHICULOS {
        int id PK
        string placa UK
        int usuario_id FK
        string tipo_vehiculo
        string marca
        string color
        string area
    }

    CELDAS {
        int id PK
        string codigo_celda UK
        string tipo_celda
        boolean ocupada
    }

    TURNOS {
        int id PK
        int usuario_id FK
        string jornada
        datetime fecha_apertura
        datetime fecha_cierre
        int total_entradas
        int total_salidas
        string estado
    }

    ACCESOS {
        int id PK
        string placa
        int vehiculo_id FK
        int celda_id FK
        int turno_id FK
        string tipo_movimiento
        string tipo_vehiculo
        datetime fecha_hora
    }

    NOVEDADES {
        int id PK
        int turno_id FK
        string tipo_novedad
        string placa_relacionada
        text descripcion
    }

    RESERVAS {
        int id PK
        int usuario_id FK
        int vehiculo_id FK
        datetime fecha
        string estado
    }

    VISITANTES {
        int id PK
        string nombre_completo
        string documento
        string placa_vehiculo
        string area_visitada
        text motivo_visita
    }

    ALERTAS {
        int id PK
        string titulo
        string severidad
        text contenido
        datetime fecha_publicacion
    }

    CONFIGURACIONES {
        int id PK
        string hora_apertura
        string hora_cierre
        boolean permitir_festivos
        int tiempo_maximo
        string accion_exceso
    }
```

### Reglas de integridad

| Relación | Comportamiento al borrar |
|---|---|
| `accesos.vehiculo_id` | `SET NULL` — el histórico del acceso se conserva |
| `accesos.turno_id` | `RESTRICT` — no se puede borrar un turno con movimientos |
| `novedades.turno_id` | `CASCADE` — la novedad vive mientras viva el turno |
| `vehiculos → accesos` | `cascade="all, delete-orphan"` en el ORM |

---

## 4. Flujo de una entrada de vehículo

```mermaid
sequenceDiagram
    actor V as Vigilante
    participant API as API Flask
    participant MW as Middleware JWT
    participant S as Servicio
    participant DB as MySQL

    V->>API: POST /api/vigilante/entrada
    API->>MW: ¿token válido y rol VIGILANTE?
    MW-->>API: OK
    API->>S: registrar_entrada(placa, celda, turno)
    S->>DB: ¿existe turno activo?
    DB-->>S: sí
    S->>DB: ¿hay celda libre del tipo?
    DB-->>S: celda EL-04
    S->>DB: INSERT acceso (Entrada)
    S->>DB: UPDATE celda SET ocupada = true
    DB-->>API: acceso creado
    API-->>V: 201 Created + datos del acceso
```

---

## 5. Flujo de trabajo con Git

```mermaid
gitGraph
    commit id: "Back-end inicial"
    branch sara_DEV
    commit id: "pruebas unitarias"
    commit id: "CI + ramas"
    checkout main
    merge sara_DEV
    branch diego_DEV
    commit id: "pruebas de Diego"
    checkout main
    merge diego_DEV tag: "v1.0.0"
```

Cada integrante trabaja en su rama `*_DEV` y solo puede llegar a `main` mediante
un Pull Request que pase el check **`pytest`**.

```mermaid
flowchart LR
    A["rama personal<br/>diego_DEV"] --> B["Push"]
    B --> C["GitHub Actions<br/>pytest"]
    C -->|"verde"| D["PR mergeable"]
    C -->|"rojo"| E["Merge bloqueado"]
    D --> F["main"]
```

---

## 6. Estructura de carpetas

```
parklink-backend/
├── app/
│   ├── __init__.py          Fábrica de la aplicación y registro de blueprints
│   ├── config/              Configuración por entorno
│   ├── controllers/         Lógica de los endpoints
│   ├── database/            Conexión e inicialización
│   ├── middlewares/         Validación de JWT y roles
│   ├── models/              Entidades del dominio
│   ├── routes/              Un blueprint por módulo
│   └── services/            Reglas de negocio
├── docs/                    Esta documentación
├── migrations/              Historial de Alembic
├── tests/
│   ├── conftest.py          Fixtures compartidos
│   └── <persona>/unit/      Pruebas por integrante
├── .github/workflows/       Integración continua
├── pytest.ini               Configuración de pytest
├── run.py                   Punto de entrada
└── seed.py                  Datos de prueba
```
