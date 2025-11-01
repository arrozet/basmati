# Basmati Backend - Microservices Architecture

Esta es la implementación del backend de Basmati utilizando una arquitectura de microservicios con FastAPI y MongoDB Atlas.

## Estructura del Proyecto

```
backend/
├── api-gateway/          # Puerto 8000 - Punto de entrada único ✅ IMPLEMENTADO
├── user_service/         # Puerto 8001 - Gestión de usuarios ✅ IMPLEMENTADO
├── calendar_service/     # Puerto 8002 - Gestión de calendarios ⚠️ SCAFFOLDING
├── event_service/        # Puerto 8003 - Gestión de eventos ⚠️ SCAFFOLDING
├── notification_service/ # Puerto 8004 - Gestión de notificaciones ⚠️ SCAFFOLDING
├── search_service/       # Puerto 8005 - Búsquedas avanzadas ⚠️ SCAFFOLDING
├── integration_service/  # Puerto 8006 - Integraciones externas ⚠️ SCAFFOLDING
├── docker-compose.yml    # Orquestación de servicios
└── .env.example          # Variables de entorno de ejemplo
```

**Nota:** Los servicios marcados con ⚠️ solo tienen la estructura de directorios (scaffolding) y están pendientes de implementación.

## Estructura de Cada Servicio

Cada microservicio sigue la misma estructura:

```
service_name/
├── main.py                    # Aplicación FastAPI principal
├── Dockerfile                 # Configuración Docker
├── requirements.txt           # Dependencias Python
├── core/
│   ├── __init__.py
│   ├── config.py             # Configuración con pydantic-settings
│   └── database.py           # Conexión a MongoDB
├── models/
│   ├── __init__.py
│   └── *.py                  # Modelos de MongoDB
├── schemas/
│   ├── __init__.py
│   ├── common.py             # Schemas comunes
│   └── *.py                  # Schemas Pydantic para validación
├── services/
│   ├── __init__.py
│   └── *_service.py          # Lógica de negocio
└── api/
    ├── __init__.py
    └── v1/
        ├── __init__.py
        ├── router.py         # Router principal v1
        └── endpoints/
            ├── __init__.py
            └── *.py          # Endpoints de la API
```

## Configuración

1. **Copiar archivo de variables de entorno:**
   ```bash
   cp .env.example .env
   ```

2. **Editar `.env` con tu conexión a MongoDB Atlas:**
   ```
   MONGO_URI=mongodb+srv://tu_usuario:tu_password@tu_cluster.mongodb.net/basmati?retryWrites=true&w=majority
   ```

## Uso con Docker

### Construir y levantar todos los servicios:
```bash
docker-compose up --build
```

### Levantar servicios en segundo plano:
```bash
docker-compose up -d
```

### Ver logs de un servicio específico:
```bash
docker-compose logs -f user-service
```

### Detener todos los servicios:
```bash
docker-compose down
```

### Reconstruir un servicio específico:
```bash
docker-compose up --build user-service
```

## Endpoints

### API Gateway (Puerto 8000)

Punto de entrada único que enruta a todos los servicios:

- **Health Check:** `GET /health`
- **Documentación:** `GET /docs` (Swagger UI)
- **Usuarios:** `/v1/users/*`
- **Calendarios:** `/v1/calendars/*`
- **Eventos:** `/v1/events/*`
- **Notificaciones:** `/v1/notifications/*`
- **Búsqueda:** `/v1/search/*`
- **Integraciones:** `/v1/integrations/*`

### User Service (Puerto 8001)

- `POST /v1/users` - Crear usuario
- `GET /v1/users/{user_id}` - Obtener usuario
- `PUT /v1/users/{user_id}` - Actualizar usuario
- `DELETE /v1/users/{user_id}` - Eliminar usuario
- `GET /v1/users/search/by-email?email={email}` - Buscar por email
- `GET /v1/users/search/by-name?name={name}` - Buscar por nombre

### Calendar Service (Puerto 8002)

- `POST /v1/calendars` - Crear calendario
- `GET /v1/calendars/{calendar_id}` - Obtener calendario
- `PUT /v1/calendars/{calendar_id}` - Actualizar calendario
- `DELETE /v1/calendars/{calendar_id}` - Eliminar calendario
- `GET /v1/calendars/search/by-organizer?organizer_id={id}` - Buscar por organizador
- `GET /v1/calendars/search/by-keywords?keyword={keyword}` - Buscar por keywords
- `GET /v1/calendars/{calendar_id}/children` - Obtener calendarios hijos
- `GET /v1/calendars/{calendar_id}/hierarchy` - Obtener jerarquía completa

### Event Service (Puerto 8003)

- `POST /v1/events` - Crear evento
- `GET /v1/events/{event_id}` - Obtener evento
- `PUT /v1/events/{event_id}` - Actualizar evento
- `DELETE /v1/events/{event_id}` - Eliminar evento
- `POST /v1/events/{event_id}/comments` - Añadir comentario
- `POST /v1/events/{event_id}/attachments` - Añadir adjunto
- `GET /v1/events/search/by-calendar?calendar_id={id}` - Buscar por calendario
- `GET /v1/events/search/by-date-range?start={date}&end={date}` - Buscar por rango de fechas
- `GET /v1/events/{event_id}/comments/users` - Usuarios que comentaron
- `GET /v1/events/users/{user_id}/commented` - Eventos comentados por usuario

### Notification Service (Puerto 8004)

- `POST /v1/notifications` - Crear notificación (interno)
- `GET /v1/notifications/user/{user_id}` - Obtener notificaciones de usuario
- `PUT /v1/notifications/{notification_id}/read` - Marcar como leída
- `GET /v1/notifications/search/unread?user_id={id}` - Notificaciones no leídas
- `GET /v1/notifications/search/by-event?event_id={id}` - Notificaciones por evento

### Search Service (Puerto 8005)

- `GET /v1/search/calendars?q={query}` - Buscar calendarios
- `GET /v1/search/events?q={query}` - Buscar eventos
- `GET /v1/search/combined?q={query}` - Búsqueda combinada
- `GET /v1/search/calendars/by_organizer?organizer_name={name}` - Calendarios por nombre de organizador
- `GET /v1/search/events/by_calendar_title?title={title}` - Eventos por título de calendario

### Integration Service (Puerto 8006)

- `POST /v1/integrations/google/import` - Importar desde Google Calendar
- `POST /v1/integrations/teamup/import` - Importar desde Teamup
- `GET /v1/integrations/sources?user_id={id}` - Fuentes de integración del usuario
- `GET /v1/integrations/sync_status?source_id={id}` - Estado de sincronización

## Acceso a la Documentación

Cada servicio tiene su propia documentación Swagger:

- **API Gateway:** http://localhost:8000/docs
- **User Service:** http://localhost:8001/docs
- **Calendar Service:** http://localhost:8002/docs
- **Event Service:** http://localhost:8003/docs
- **Notification Service:** http://localhost:8004/docs
- **Search Service:** http://localhost:8005/docs
- **Integration Service:** http://localhost:8006/docs

## Estado de Implementación

### ✅ Completamente Implementado

- **API Gateway** (Puerto 8000)
  - Punto de entrada único
  - Routing a todos los servicios
  - Manejo de errores
  - Documentación OpenAPI

- **User Service** (Puerto 8001)
  - CRUD completo de usuarios
  - Búsquedas parametrizadas (email, nombre)
  - Gestión de preferencias
  - Documentación completa

### ⚠️ Scaffolding (Pendiente de Implementación)

Los siguientes servicios tienen **solo la estructura de directorios** creada:

- **Calendar Service** (Puerto 8002) - TODO
- **Event Service** (Puerto 8003) - TODO
- **Notification Service** (Puerto 8004) - TODO
- **Search Service** (Puerto 8005) - TODO
- **Integration Service** (Puerto 8006) - TODO

Cada servicio en scaffolding incluye:
- ✅ Estructura de directorios completa
- ✅ Dockerfile configurado
- ✅ requirements.txt con dependencias
- ✅ main.py con health check básico
- ⚠️ Archivos de implementación marcados con `# TODO: Implementar`

### 🔧 Infraestructura Completa

✅ **Docker Compose**
- Orquestación de todos los servicios
- Networking interno entre contenedores
- Variables de entorno configuradas

✅ **Arquitectura de Microservicios**
- 6 microservicios independientes + API Gateway
- Cada servicio en su propio contenedor Docker
- Puertos asignados (8000-8006)

## Tecnologías Utilizadas

- **FastAPI** - Framework web moderno y rápido
- **MongoDB Atlas** - Base de datos NoSQL en la nube
- **Motor** - Driver async de MongoDB para Python
- **Pydantic** - Validación de datos y settings
- **Docker** - Contenedorización de servicios
- **httpx** - Cliente HTTP async para comunicación inter-servicios

## Desarrollo

### Para servicios ya implementados (API Gateway, User Service):

```bash
cd service_name
pip install -r requirements.txt
uvicorn main:app --reload --port 800X
```

### Para servicios en scaffolding:

Los servicios `calendar_service`, `event_service`, `notification_service`, `search_service` e `integration_service` están listos para ser implementados. Cada uno tiene:

1. **Estructura completa de directorios:**
   - `core/` - Configuración y database
   - `models/` - Modelos MongoDB
   - `schemas/` - Validación Pydantic
   - `services/` - Lógica de negocio
   - `api/v1/endpoints/` - Endpoints REST

2. **Archivos base:**
   - `main.py` - App FastAPI con health check
   - `Dockerfile` - Configuración Docker
   - `requirements.txt` - Dependencias necesarias

3. **Archivos marcados con `# TODO: Implementar`**

Para implementar un servicio, sigue la estructura del **User Service** como referencia.

## Guía de Implementación para Compañeros

📖 **[Ver IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)** - Guía completa paso a paso

📋 **[Ver AGENTS.md](../../../AGENTS.md)** en la raíz del proyecto para:
- Especificaciones detalladas de cada servicio
- Endpoints requeridos
- Schemas de MongoDB
- Ejemplos de implementación
- Queries parametrizadas y relacionales necesarias

🔍 **Referencia de implementación:** El **UserService** está completamente implementado y puede usarse como ejemplo

## Notas

- Los errores de importación en el IDE son normales hasta que se instalen las dependencias en cada servicio
- Las API keys de servicios externos son opcionales para esta fase
- La autenticación/autorización se implementará en una práctica posterior
- **User Service** es un ejemplo completo de implementación para referencia
