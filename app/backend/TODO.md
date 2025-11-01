# TODO - Servicios Pendientes de Implementación

Este archivo lista exactamente qué archivos necesitan ser implementados en cada servicio.

## Estado General

- ✅ **API Gateway** - COMPLETADO
- ✅ **UserService** - COMPLETADO (Usar como referencia)
- ⚠️ **CalendarService** - SCAFFOLDING
- ⚠️ **EventService** - SCAFFOLDING
- ⚠️ **NotificationService** - SCAFFOLDING
- ⚠️ **SearchService** - SCAFFOLDING
- ⚠️ **IntegrationService** - SCAFFOLDING

---

## CalendarService (Puerto 8002)

### Archivos a Implementar:

- [ ] `core/config.py` - Configuración del servicio
- [ ] `core/database.py` - Conexión a MongoDB
- [ ] `models/calendar.py` - Modelo de calendario
- [ ] `schemas/calendar.py` - Schemas (CalendarCreate, CalendarUpdate, CalendarResponse, CalendarHierarchy)
- [ ] `services/calendar_service.py` - Lógica de negocio
- [ ] `api/v1/router.py` - Router principal
- [ ] `api/v1/endpoints/calendars.py` - Endpoints REST

### Endpoints Requeridos:

- [ ] `POST /v1/calendars` - Crear calendario
- [ ] `GET /v1/calendars/{calendar_id}` - Obtener calendario
- [ ] `PUT /v1/calendars/{calendar_id}` - Actualizar calendario
- [ ] `DELETE /v1/calendars/{calendar_id}` - Eliminar calendario
- [ ] `GET /v1/calendars/search/by-organizer?organizer_id={id}` - Buscar por organizador (parametrized 1)
- [ ] `GET /v1/calendars/search/by-keywords?keyword={keyword}` - Buscar por keywords (parametrized 2)
- [ ] `GET /v1/calendars/{calendar_id}/children` - Obtener calendarios hijos (relationship 1)
- [ ] `GET /v1/calendars/{calendar_id}/hierarchy` - Obtener jerarquía completa (relationship 2)

### Variables de Entorno:

```
MONGO_URI
SERVICE_PORT=8002
USER_SERVICE_URL=http://user-service:8001
```

---

## EventService (Puerto 8003)

### Archivos a Implementar:

- [ ] `core/config.py` - Configuración del servicio
- [ ] `core/database.py` - Conexión a MongoDB
- [ ] `models/event.py` - Modelo de evento
- [ ] `schemas/event.py` - Schemas (EventCreate, EventUpdate, EventResponse, CommentCreate, AttachmentCreate)
- [ ] `services/event_service.py` - Lógica de negocio
- [ ] `api/v1/router.py` - Router principal
- [ ] `api/v1/endpoints/events.py` - Endpoints REST

### Endpoints Requeridos:

- [ ] `POST /v1/events` - Crear evento
- [ ] `GET /v1/events/{event_id}` - Obtener evento
- [ ] `PUT /v1/events/{event_id}` - Actualizar evento
- [ ] `DELETE /v1/events/{event_id}` - Eliminar evento
- [ ] `POST /v1/events/{event_id}/comments` - Añadir comentario (dispara notificación)
- [ ] `POST /v1/events/{event_id}/attachments` - Añadir adjunto
- [ ] `GET /v1/events/search/by-calendar?calendar_id={id}` - Buscar por calendario (parametrized 1)
- [ ] `GET /v1/events/search/by-date-range?start={date}&end={date}` - Buscar por rango (parametrized 2)
- [ ] `GET /v1/events/{event_id}/comments/users` - Usuarios que comentaron (relationship 1)
- [ ] `GET /v1/events/users/{user_id}/commented` - Eventos comentados por usuario (relationship 2)

### Variables de Entorno:

```
MONGO_URI
SERVICE_PORT=8003
NOTIFICATION_SERVICE_URL=http://notification-service:8004
CALENDAR_SERVICE_URL=http://calendar-service:8002
```

### Comunicación Inter-Servicios:

- Al añadir un comentario, debe llamar a NotificationService para crear notificación

---

## NotificationService (Puerto 8004)

### Archivos a Implementar:

- [ ] `core/config.py` - Configuración del servicio
- [ ] `core/database.py` - Conexión a MongoDB
- [ ] `models/notification.py` - Modelo de notificación
- [ ] `schemas/notification.py` - Schemas (NotificationCreate, NotificationResponse)
- [ ] `services/notification_service.py` - Lógica de negocio
- [ ] `api/v1/router.py` - Router principal
- [ ] `api/v1/endpoints/notifications.py` - Endpoints REST

### Endpoints Requeridos:

- [ ] `POST /v1/notifications` - Crear notificación (llamado por EventService)
- [ ] `GET /v1/notifications/user/{user_id}` - Obtener notificaciones de usuario
- [ ] `PUT /v1/notifications/{notification_id}/read` - Marcar como leída
- [ ] `GET /v1/notifications/search/unread?user_id={id}` - Notificaciones no leídas (parametrized 1)
- [ ] `GET /v1/notifications/search/by-event?event_id={id}` - Por evento (parametrized 2)

### Variables de Entorno:

```
MONGO_URI
SERVICE_PORT=8004
USER_SERVICE_URL=http://user-service:8001
EMAIL_SERVICE_API_KEY=  # Opcional
```

---

## SearchService (Puerto 8005)

### Archivos a Implementar:

- [ ] `core/config.py` - Configuración del servicio
- [ ] `core/database.py` - Conexión a MongoDB
- [ ] `schemas/search.py` - Schemas (SearchResult, CombinedSearchResult)
- [ ] `services/search_service.py` - Lógica de negocio
- [ ] `api/v1/router.py` - Router principal
- [ ] `api/v1/endpoints/search.py` - Endpoints REST

### Endpoints Requeridos:

- [ ] `GET /v1/search/calendars?q={query}` - Full-text search calendarios (parametrized 1)
- [ ] `GET /v1/search/events?q={query}` - Full-text search eventos (parametrized 2)
- [ ] `GET /v1/search/combined?q={query}` - Búsqueda combinada
- [ ] `GET /v1/search/calendars/by_organizer?organizer_name={name}` - Por nombre organizador (relationship 1)
- [ ] `GET /v1/search/events/by_calendar_title?title={title}` - Por título calendario (relationship 2)

### Variables de Entorno:

```
MONGO_URI
SERVICE_PORT=8005
CALENDAR_SERVICE_URL=http://calendar-service:8002
EVENT_SERVICE_URL=http://event-service:8003
```

### Nota Especial:

Este servicio hace queries agregadas y búsquedas de texto completo en múltiples colecciones.

---

## IntegrationService (Puerto 8006)

### Archivos a Implementar:

- [ ] `core/config.py` - Configuración del servicio
- [ ] `core/database.py` - Conexión a MongoDB
- [ ] `schemas/integration.py` - Schemas (ImportRequest, IntegrationSource, SyncStatus)
- [ ] `services/integration_service.py` - Lógica de negocio
- [ ] `api/v1/router.py` - Router principal
- [ ] `api/v1/endpoints/integrations.py` - Endpoints REST

### Endpoints Requeridos:

- [ ] `POST /v1/integrations/google/import` - Importar desde Google Calendar
- [ ] `POST /v1/integrations/teamup/import` - Importar desde Teamup
- [ ] `GET /v1/integrations/sources?user_id={id}` - Fuentes del usuario (parametrized 1)
- [ ] `GET /v1/integrations/sync_status?source_id={id}` - Estado de sync (parametrized 2)

### Variables de Entorno:

```
MONGO_URI
SERVICE_PORT=8006
CALENDAR_SERVICE_URL=http://calendar-service:8002
EVENT_SERVICE_URL=http://event-service:8003
GOOGLE_CALENDAR_API_KEY=  # Opcional
TEAMUP_API_KEY=  # Opcional
```

### Nota Especial:

Las integraciones con APIs externas son opcionales para esta fase. Se puede implementar como placeholders.

---

## Prioridad de Implementación

Se recomienda implementar en este orden:

1. **CalendarService** - Es independiente y necesario para otros servicios
2. **EventService** - Depende de CalendarService
3. **NotificationService** - Es llamado por EventService
4. **SearchService** - Agrega funcionalidad sobre Calendar y Event
5. **IntegrationService** - Opcional, puede implementarse al final

---

## Checklist General por Servicio

Para marcar un servicio como completo:

- [ ] Todos los archivos implementados
- [ ] Todos los endpoints funcionando
- [ ] Al menos 2 queries parametrizadas
- [ ] Queries relacionales implementadas (si aplica)
- [ ] Docstrings en español en todos los métodos
- [ ] Ejemplos en docstrings para Swagger
- [ ] Manejo de errores apropiado
- [ ] Probado individualmente con `uvicorn`
- [ ] Probado con Docker
- [ ] Probado en docker-compose con otros servicios

---

## Recursos

- **Referencia completa:** `user_service/` (completamente implementado)
- **Especificaciones:** `AGENTS.md` en raíz del proyecto
- **Guía paso a paso:** `IMPLEMENTATION_GUIDE.md`
- **Schemas MongoDB:** Ver `AGENTS.md` sección "Database Schema"

---

## Actualizar este archivo

A medida que se completen tareas, marcar con ✅:

```markdown
- [x] `core/config.py` - ✅ Implementado por [Nombre]
```

Esto ayuda a coordinar el trabajo entre compañeros y evitar duplicar esfuerzos.
