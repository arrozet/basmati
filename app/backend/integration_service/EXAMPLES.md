# Ejemplos de Uso - IntegrationService

## ⚠️ Importante

**Estado Actual del Servicio:**
- ✅ Endpoints GET funcionan completamente
- ⚠️ Endpoints POST requieren CalendarService en puerto 8002
- ⚠️ No hay conexión real a Google Calendar o Teamup APIs (simulado)

Ver [`TEST_GUIDE.md`](TEST_GUIDE.md) para guía completa de testing.

## Base URL

```
http://localhost:8006/v1/integrations
```

---

## Endpoints Que Funcionan ✅

### 1. Health Check

**Request:**
```bash
curl http://localhost:8006/health
```

**Response (200):**
```json
{
  "status": "healthy",
  "service": "integration-service",
  "port": 8006
}
```

---

### 2. Obtener fuentes de un usuario (Parametrized Query 1)

**Request:**
```bash
curl "http://localhost:8006/v1/integrations/sources?external_id=test_user_123"
```

**Response (200) - Sin fuentes:**
```json
[]
```

**Response (200) - Con fuentes:**
```json
[
  {
    "id": "673abc123def456789000000",
    "user_external_id": "test_user_123",
    "source_type": "google_calendar",
    "external_source_id": "primary",
    "basmati_calendar_id": "673abc123def456789000001",
    "sync_enabled": true,
    "last_sync": "2024-11-03T12:00:00.000Z",
    "sync_status": "success",
    "sync_error_message": null,
    "created_at": "2024-11-03T11:55:00.000Z"
  }
]
```

---

### 3. Obtener estado de sincronización (Parametrized Query 2)

**Request:**
```bash
curl "http://localhost:8006/v1/integrations/sync_status?source_id=673abc123def456789000000"
```

**Response (200):**
```json
{
  "source_id": "673abc123def456789000000",
  "source_type": "google_calendar",
  "sync_status": "success",
  "last_sync": "2024-11-03T12:00:00.000Z",
  "sync_error_message": null,
  "events_synced": 0
}
```

**Response (404) - Fuente no existe:**
```json
{
  "detail": "Fuente de integración no encontrada"
}
```

---

### 4. Obtener detalles de una fuente

**Request:**
```bash
curl "http://localhost:8006/v1/integrations/sources/673abc123def456789000000"
```

**Response (200):**
```json
{
  "id": "673abc123def456789000000",
  "user_external_id": "test_user_123",
  "source_type": "google_calendar",
  "external_source_id": "primary",
  "basmati_calendar_id": "673abc123def456789000001",
  "sync_enabled": true,
  "last_sync": "2024-11-03T12:00:00.000Z",
  "sync_status": "success",
  "sync_error_message": null,
  "created_at": "2024-11-03T11:55:00.000Z"
}
```

---

## Endpoints Que Requieren CalendarService ⚠️

### 5. Importar desde Google Calendar

**Prerequisito:** CalendarService debe estar corriendo en puerto 8002

**Request:**
```bash
curl -X POST "http://localhost:8006/v1/integrations/google/import" \
  -H "Content-Type: application/json" \
  -d '{
    "user_external_id": "test_user_123",
    "google_access_token": "fake_token_for_testing",
    "calendar_ids": ["primary"]
  }'
```

**Response (201) - CON CalendarService:**
```json
{
  "success": true,
  "message": "Se importaron 1 calendarios correctamente",
  "imported_sources": [
    {
      "id": "673abc123def456789000000",
      "user_external_id": "test_user_123",
      "source_type": "google_calendar",
      "external_source_id": "primary",
      "basmati_calendar_id": "673abc123def456789000001",
      "sync_enabled": true,
      "last_sync": "2024-11-03T12:00:00.000Z",
      "sync_status": "success",
      "sync_error_message": null,
      "created_at": "2024-11-03T12:00:00.000Z"
    }
  ],
  "errors": []
}
```

**Response (201) - SIN CalendarService:**
```json
{
  "success": false,
  "message": "Se importaron 0 calendarios correctamente. 1 errores encontrados",
  "imported_sources": [],
  "errors": [
    "Error al crear calendario de Basmati para 'primary'"
  ]
}
```

---

### 6. Importar desde Teamup

**Prerequisito:** CalendarService debe estar corriendo en puerto 8002

**Request:**
```bash
curl -X POST "http://localhost:8006/v1/integrations/teamup/import" \
  -H "Content-Type: application/json" \
  -d '{
    "user_external_id": "test_user_123",
    "teamup_api_key": "fake_api_key",
    "calendar_keys": ["ks1234567"]
  }'
```

**Response:** Similar al de Google Calendar (éxito o error según CalendarService)

---

## Script de Testing Automático

Ejecuta el script incluido para probar todos los endpoints:

```bash
cd /home/drlk/basmati/app/backend/integration_service
./test_endpoints.sh
```

---

## Testing con Swagger UI

Accede a la documentación interactiva:

```
http://localhost:8006/docs
```

Desde ahí puedes:
- Ver todos los schemas
- Probar endpoints con el botón "Try it out"
- Ver ejemplos de request/response

---

## Insertar Datos de Prueba Manualmente

Si quieres probar sin CalendarService, inserta datos directamente en MongoDB:

```javascript
// Conectar a MongoDB
use basmati

// Insertar fuente de integración
db.integration_sources.insertOne({
  user_external_id: "test_user_456",
  source_type: "google_calendar",
  external_source_id: "test_calendar_1",
  basmati_calendar_id: ObjectId("673abc123def456789001111"),
  sync_enabled: true,
  last_sync: new Date(),
  sync_status: "success",
  sync_error_message: null,
  created_at: new Date()
})
```

Luego consulta:
```bash
curl "http://localhost:8006/v1/integrations/sources?external_id=test_user_456"
```

---

## Errores Comunes y Soluciones

### Error: "Error al crear calendario de Basmati para 'xxx'"

**Causa:** CalendarService no está disponible en puerto 8002

**Solución:**
```bash
# Levantar CalendarService
cd /home/drlk/basmati/app/backend
docker-compose up calendar-service

# Verificar que funciona
curl http://localhost:8002/health
```

### Error: "Connection refused"

**Causa:** IntegrationService no puede alcanzar CalendarService

**Solución:** Verifica que ambos servicios están en la misma red Docker:
```bash
docker network ls
docker network inspect basmati-network
```

### Error: "Fuente de integración no encontrada"

**Causa:** El `source_id` proporcionado no existe en MongoDB

**Solución:** Verifica el ID correcto con:
```bash
curl "http://localhost:8006/v1/integrations/sources?external_id=tu_usuario"
```

---

## Próximos Pasos para Producción

Para que funcione completamente en producción:

1. **Implementar Google Calendar API real**
2. **Implementar Teamup API real**  
3. **Agregar sincronización de eventos** (llamar a EventService)
4. **Implementar sincronización periódica** (cron jobs)
5. **Agregar webhooks** para sincronización en tiempo real

---

## 1. Importar desde Google Calendar

### Endpoint
POST /google/import

### Request Body
```json
{
  "user_external_id": "google_123456789",
  "google_access_token": "ya29.a0AfH6SMBx...",
  "calendar_ids": ["primary", "work_calendar_id"]
}
```

### Response (201 Created)
```json
{
  "success": true,
  "message": "Se importaron 2 calendarios correctamente",
  "imported_sources": [
    {
      "id": "507f1f77bcf86cd799439011",
      "user_external_id": "google_123456789",
      "source_type": "google_calendar",
      "external_source_id": "primary",
      "basmati_calendar_id": "507f1f77bcf86cd799439012",
      "sync_enabled": true,
      "last_sync": "2024-11-03T10:30:00",
      "sync_status": "success",
      "sync_error_message": null,
      "created_at": "2024-11-03T10:25:00"
    }
  ],
  "errors": []
}
```


### Curl Example
```bash
curl -X POST "http://localhost:8006/v1/integrations/google/import" \
  -H "Content-Type: application/json" \
  -d '{
    "user_external_id": "google_123456789",
    "google_access_token": "ya29.a0AfH6SMBx...",
    "calendar_ids": ["primary"]
  }'
```

---

## 2. Importar desde Teamup

### Endpoint
POST /teamup/import

### Request Body
```json
{
  "user_external_id": "google_123456789",
  "teamup_api_key": "tu_api_key_aqui",
  "calendar_keys": ["ks1234567", "ks7654321"]
}
```

### Response (201 Created)
```json
{
  "success": true,
  "message": "Se importaron 2 calendarios correctamente",
  "imported_sources": [
    {
      "id": "507f1f77bcf86cd799439013",
      "user_external_id": "google_123456789",
      "source_type": "teamup",
      "external_source_id": "ks1234567",
      "basmati_calendar_id": "507f1f77bcf86cd799439014",
      "sync_enabled": true,
      "last_sync": "2024-11-03T10:35:00",
      "sync_status": "success",
      "sync_error_message": null,
      "created_at": "2024-11-03T10:30:00"
    }
  ],
  "errors": []
}
```

### Curl Example
```bash
curl -X POST "http://localhost:8006/v1/integrations/teamup/import" \
  -H "Content-Type: application/json" \
  -d '{
    "user_external_id": "google_123456789",
    "teamup_api_key": "tu_api_key",
    "calendar_keys": ["ks1234567"]
  }'
```

---

## 3. Obtener fuentes de un usuario (Parametrized Query 1)

### Endpoint
GET /sources?external_id={user_external_id}

### Query Parameters
- `external_id` (required): External ID del usuario

### Response (200 OK)
```json
[
  {
    "id": "507f1f77bcf86cd799439011",
    "user_external_id": "google_123456789",
    "source_type": "google_calendar",
    "external_source_id": "primary",
    "basmati_calendar_id": "507f1f77bcf86cd799439012",
    "sync_enabled": true,
    "last_sync": "2024-11-03T10:30:00",
    "sync_status": "success",
    "sync_error_message": null,
    "created_at": "2024-11-03T10:25:00"
  },
  {
    "id": "507f1f77bcf86cd799439013",
    "user_external_id": "google_123456789",
    "source_type": "teamup",
    "external_source_id": "ks1234567",
    "basmati_calendar_id": "507f1f77bcf86cd799439014",
    "sync_enabled": true,
    "last_sync": "2024-11-03T10:35:00",
    "sync_status": "success",
    "sync_error_message": null,
    "created_at": "2024-11-03T10:30:00"
  }
]
```

### Curl Example
```bash
curl -X GET "http://localhost:8006/v1/integrations/sources?external_id=google_123456789"
```

---

## 4. Obtener estado de sincronización (Parametrized Query 2)

### Endpoint
`GET /sync_status?source_id={source_id}`

### Query Parameters
- `source_id` (required): ID de la fuente de integración

### Response (200 OK)
```json
{
  "source_id": "507f1f77bcf86cd799439011",
  "source_type": "google_calendar",
  "sync_status": "success",
  "last_sync": "2024-11-03T10:30:00",
  "sync_error_message": null,
  "events_synced": 42
}
```

### Response cuando hay error
```json
{
  "source_id": "507f1f77bcf86cd799439015",
  "source_type": "google_calendar",
  "sync_status": "error",
  "last_sync": "2024-11-03T09:00:00",
  "sync_error_message": "Token de acceso expirado",
  "events_synced": 0
}
```

### Curl Example
```bash
curl -X GET "http://localhost:8006/v1/integrations/sync_status?source_id=507f1f77bcf86cd799439011"
```

---

## 5. Obtener detalles de una fuente específica

### Endpoint
`GET /sources/{source_id}`

### Path Parameters
- `source_id`: ID de la fuente de integración

### Response (200 OK)
```json
{
  "id": "507f1f77bcf86cd799439011",
  "user_external_id": "google_123456789",
  "source_type": "google_calendar",
  "external_source_id": "primary",
  "basmati_calendar_id": "507f1f77bcf86cd799439012",
  "sync_enabled": true,
  "last_sync": "2024-11-03T10:30:00",
  "sync_status": "success",
  "sync_error_message": null,
  "created_at": "2024-11-03T10:25:00"
}
```

### Response cuando no existe (404 Not Found)
```json
{
  "detail": "Fuente de integración no encontrada"
}
```

### Curl Example
```bash
curl -X GET "http://localhost:8006/v1/integrations/sources/507f1f77bcf86cd799439011"
```

---

## 6. Health Check

### Endpoint
`GET /health`

### Response (200 OK)
```json
{
  "status": "healthy",
  "service": "integration-service",
  "port": 8006
}
```

### Curl Example
```bash
curl -X GET "http://localhost:8006/health"
```

---

## Flujo Completo de Ejemplo

### Paso 1: Importar calendario de Google
```bash
curl -X POST "http://localhost:8006/v1/integrations/google/import" \
  -H "Content-Type: application/json" \
  -d '{
    "user_external_id": "google_juan123",
    "google_access_token": "ya29.a0AfH6SMBx...",
    "calendar_ids": ["primary"]
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Se importaron 1 calendarios correctamente",
  "imported_sources": [
    {
      "id": "674750abc123def456789000",
      ...
    }
  ]
}
```

### Paso 2: Verificar el estado de sincronización
```bash
curl -X GET "http://localhost:8006/v1/integrations/sync_status?source_id=674750abc123def456789000"
```

**Respuesta:**
```json
{
  "source_id": "674750abc123def456789000",
  "source_type": "google_calendar",
  "sync_status": "success",
  "last_sync": "2024-11-03T11:00:00",
  "sync_error_message": null,
  "events_synced": 15
}
```

### Paso 3: Listar todas las fuentes del usuario
```bash
curl -X GET "http://localhost:8006/v1/integrations/sources?external_id=google_juan123"
```

**Respuesta:**
```json
[
  {
    "id": "674750abc123def456789000",
    "user_external_id": "google_juan123",
    "source_type": "google_calendar",
    ...
  }
]
```

---

## Errores Comunes

### 400 Bad Request
```json
{
  "detail": "Datos de calendario inválidos: ..."
}
```

### 404 Not Found
```json
{
  "detail": "Fuente de integración no encontrada"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error al importar desde Google Calendar: ..."
}
```

---

## Testing con Swagger UI

Accede a `http://localhost:8006/docs` para probar todos los endpoints interactivamente.

## Próximos Pasos

1. Implementar autenticación OAuth real con Google
2. Implementar API de Teamup real
3. Agregar sincronización automática periódica
4. Implementar webhooks para sincronización en tiempo real
