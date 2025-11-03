# Integration Service

Microservicio para importación y sincronización de calendarios externos (Google Calendar, Teamup).

## ⚠️ Estado Actual

**Implementación Parcial:**
- ✅ **Estructura completa** - Todos los endpoints, schemas, models, repositories y services implementados
- ✅ **Queries funcionan** - GET /sources y /sync_status operativos
- ⚠️ **Importación simulada** - POST /google/import y /teamup/import crean registros pero NO conectan a APIs reales
- ⚠️ **Requiere CalendarService** - Para crear calendarios en Basmati (puerto 8002)

Ver [`TEST_GUIDE.md`](TEST_GUIDE.md) para instrucciones de testing.

---

## Puerto

**8006**

## Responsabilidades

1. **Importar calendarios externos** → Convertir calendarios de Google Calendar y Teamup al formato de Basmati
2. **Sincronizar eventos** → Mantener actualizados los datos importados
3. **Gestionar fuentes de integración** → Rastrear el estado de sincronización de cada calendario importado

## Endpoints

### Importación

- `POST /v1/integrations/google/import` - Importar desde Google Calendar
- `POST /v1/integrations/teamup/import` - Importar desde Teamup

### Búsquedas Parametrizadas (Práctica 6.2)

- `GET /v1/integrations/sources?external_id={id}` - Obtener fuentes de un usuario **(parametrized query 1)**
- `GET /v1/integrations/sync_status?source_id={id}` - Obtener estado de sincronización **(parametrized query 2)**

### Otros

- `GET /v1/integrations/sources/{source_id}` - Obtener detalles de una fuente específica
- `GET /health` - Health check del servicio

## Base de Datos

### Colección: `integration_sources`

```javascript
{
    "_id": ObjectId,
    "user_external_id": str,              // usuario propietario
    "source_type": str,                   // "google_calendar" | "teamup"
    "external_source_id": str,            // ID del calendario en el servicio externo
    "basmati_calendar_id": ObjectId,      // calendario creado en Basmati
    "sync_enabled": bool,
    "last_sync": datetime,
    "sync_status": str,                   // "success" | "error" | "pending"
    "sync_error_message": str,
    "created_at": datetime
}
```

## Arquitectura

```
┌─────────────────────────────────────┐
│   IntegrationService (Puerto 8006)  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  API Layer (FastAPI)          │  │
│  │  - Import endpoints           │  │
│  │  - Query endpoints            │  │
│  └───────────────────────────────┘  │
│           ↓                         │
│  ┌───────────────────────────────┐  │
│  │  Service Layer                │  │
│  │  - Import logic               │  │
│  │  - External API calls         │  │
│  └───────────────────────────────┘  │
│           ↓                         │
│  ┌───────────────────────────────┐  │
│  │  Repository Layer             │  │
│  │  - MongoDB operations         │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
         ↓                    ↓
    ┌─────────┐        ┌────────────┐
    │ MongoDB │        │ External   │
    │ Atlas   │        │ APIs       │
    └─────────┘        └────────────┘
         ↓
   ┌──────────────┐   ┌──────────────┐
   │ Calendar     │   │ Event        │
   │ Service:8002 │   │ Service:8003 │
   └──────────────┘   └──────────────┘
```

## Flujo de Importación

### Google Calendar

1. Usuario proporciona `google_access_token` y opcionalmente `calendar_ids`
2. IntegrationService valida credenciales
3. Para cada calendario:
   - Verifica si ya está importado (evita duplicados)
   - Crea fuente de integración en MongoDB
   - Llama a CalendarService para crear calendario en Basmati
   - Vincula calendario de Basmati con la fuente
   - Actualiza estado de sincronización

### Teamup

Similar a Google Calendar, pero usando `teamup_api_key` y `calendar_keys`.

## Tecnologías

- **FastAPI** - Framework web
- **Motor** - Driver asíncrono de MongoDB
- **httpx** - Cliente HTTP para llamar a otros servicios
- **Pydantic v2** - Validación de datos
- **Docker** - Contenedorización

## Variables de Entorno

```env
MONGO_URI=mongodb+srv://...
SERVICE_PORT=8006
DATABASE_NAME=basmati
CALENDAR_SERVICE_URL=http://calendar-service:8002
EVENT_SERVICE_URL=http://event-service:8003
GOOGLE_CALENDAR_API_KEY=       # Opcional por ahora
TEAMUP_API_KEY=                # Opcional por ahora
```

## Estructura de Archivos

```
integration_service/
├── api/
│   └── v1/
│       ├── endpoints/
│       │   ├── __init__.py
│       │   └── integrations.py    # Endpoints de integración
│       └── router.py               # Router principal
├── core/
│   ├── config.py                   # Configuración del servicio
│   └── database.py                 # Conexión a MongoDB
├── models/
│   ├── __init__.py
│   └── integration_source.py      # Modelo MongoDB
├── repositories/
│   ├── __init__.py
│   └── integration_repository.py  # Acceso a datos
├── schemas/
│   ├── __init__.py
│   └── integration.py             # Schemas Pydantic
├── services/
│   ├── __init__.py
│   └── integration_service.py     # Lógica de negocio
├── Dockerfile
├── main.py                        # Punto de entrada
├── requirements.txt
└── README.md
```

## Comandos

### Ejecutar localmente

```bash
cd app/backend/integration_service
uvicorn main:app --reload --port 8006
```

### Ejecutar con Docker

```bash
cd app/backend
docker-compose up integration-service
```

### Ver logs

```bash
docker logs basmati-integration-service -f
```

## Documentación API

Una vez ejecutado, accede a:
- **Swagger UI**: http://localhost:8006/docs
- **ReDoc**: http://localhost:8006/redoc

## Práctica 6.2 - Requisitos Cumplidos

✅ **2 operaciones con búsquedas parametrizadas**:
1. `GET /integrations/sources?external_id={id}` - Buscar fuentes por usuario
2. `GET /integrations/sync_status?source_id={id}` - Buscar estado por fuente

✅ **Operaciones con relaciones entre entidades**:
- Vinculación con CalendarService (crear calendario en Basmati)
- Vinculación con EventService (importar eventos)
- Relación entre `integration_sources` y `calendars` vía `basmati_calendar_id`

✅ **Documentación OpenAPI**:
- Auto-generada por FastAPI con docstrings
- Ejemplos incluidos en schemas Pydantic

✅ **Dockerización**:
- Dockerfile configurado
- Incluido en docker-compose.yml

✅ **Base de datos no relacional**:
- MongoDB con colección `integration_sources`
- Denormalización de datos para performance
