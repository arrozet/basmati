# Guía de Uso - API de Imágenes S3 (V2)

## Descripción General

El servicio de integración incluye un sistema completo de gestión de imágenes con AWS S3 que incluye **compresión automática** para optimizar el almacenamiento.

## Configuración Docker

El servicio está completamente dockerizado. Las variables de entorno necesarias están en `.env`:

```env
AWS_ACCESS_KEY_ID=AKIA2TKZWWBY4UWIC7QW
AWS_SECRET_ACCESS_KEY=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
AWS_REGION=us-east-1
AWS_S3_BUCKET_NAME=basmati-s3
```

Estas variables se cargan automáticamente en `docker-compose.yml` al servicio `integration-service`.

## Endpoints Disponibles

Todos los endpoints están bajo `/v2/s3/` en el integration-service (puerto 8006).

### 1. Subida Directa con Compresión ⭐ (RECOMENDADO)

**Endpoint:** `POST /v2/s3/upload-direct`

**Ventajas:**
- ✅ Compresión automática de imágenes
- ✅ Redimensiona imágenes grandes (máx 1920x1080)
- ✅ Optimiza JPEG/PNG para web
- ✅ Reduce costos de almacenamiento y ancho de banda

**Ejemplo con curl:**

```bash
curl -X POST "http://localhost:8006/v2/s3/upload-direct?folder=events&compress=true" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/imagen.jpg"
```

**Respuesta:**

```json
{
  "key": "events/abc123_imagen.jpg",
  "filename": "imagen.jpg",
  "url": "https://basmati-s3.s3.us-east-1.amazonaws.com/events/abc123_imagen.jpg",
  "size": 125678,
  "content_type": "image/jpeg",
  "last_modified": "2025-12-03T10:30:00Z"
}
```

**Ejemplo con Python:**

```python
import requests

url = "http://localhost:8006/v2/s3/upload-direct"
params = {"folder": "events", "compress": True}

with open("imagen.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(url, params=params, files=files)
    
print(response.json())
```

**Ejemplo con JavaScript (Frontend):**

```javascript
async function uploadImage(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(
    'http://localhost:8006/v2/s3/upload-direct?folder=events&compress=true',
    {
      method: 'POST',
      body: formData
    }
  );
  
  const data = await response.json();
  console.log('Imagen subida:', data.url);
  return data;
}
```

---

### 2. Subida con URL Presigned (Sin compresión)

**Endpoint:** `POST /v2/s3/upload`

Este método genera una URL temporal para que el cliente suba directamente a S3 sin pasar por el backend.

⚠️ **Nota:** No incluye compresión. Útil solo si el cliente ya comprimió la imagen.

**Solicitud:**

```bash
curl -X POST "http://localhost:8006/v2/s3/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "evento.jpg",
    "content_type": "image/jpeg",
    "folder": "events"
  }'
```

**Respuesta:**

```json
{
  "upload_url": "https://basmati-s3.s3.us-east-1.amazonaws.com/events/abc123.jpg?X-Amz-...",
  "image_key": "events/abc123.jpg",
  "public_url": "https://basmati-s3.s3.us-east-1.amazonaws.com/events/abc123.jpg",
  "expires_in": 3600
}
```

**Luego, subir con PUT:**

```bash
curl -X PUT "<upload_url>" \
  -H "Content-Type: image/jpeg" \
  --data-binary "@imagen.jpg"
```

---

### 3. Listar Imágenes

**Endpoint:** `GET /v2/s3/images`

**Parámetros:**
- `prefix` (opcional): Filtrar por carpeta (ej: `events`, `avatars`)
- `max_results` (opcional): Número máximo de resultados (1-1000)

**Ejemplo:**

```bash
curl "http://localhost:8006/v2/s3/images?prefix=events&max_results=50"
```

**Respuesta:**

```json
{
  "images": [
    {
      "key": "events/abc123.jpg",
      "filename": "evento.jpg",
      "url": "https://basmati-s3.s3.us-east-1.amazonaws.com/events/abc123.jpg",
      "size": 125678,
      "content_type": "image/jpeg",
      "last_modified": "2025-12-03T10:30:00Z"
    }
  ],
  "total": 1,
  "prefix": "events"
}
```

---

### 4. Obtener Metadatos de Imagen

**Endpoint:** `GET /v2/s3/images/{image_key}`

```bash
curl "http://localhost:8006/v2/s3/images/events/abc123.jpg"
```

---

### 5. Eliminar Imagen

**Endpoint:** `DELETE /v2/s3/images/{image_key}`

```bash
curl -X DELETE "http://localhost:8006/v2/s3/images/events/abc123.jpg"
```

**Respuesta:**

```json
{
  "success": true,
  "message": "Imagen eliminada correctamente",
  "deleted_key": "events/abc123.jpg"
}
```

---

### 6. Eliminar Múltiples Imágenes

**Endpoint:** `POST /v2/s3/images/bulk-delete`

```bash
curl -X POST "http://localhost:8006/v2/s3/images/bulk-delete" \
  -H "Content-Type: application/json" \
  -d '{
    "keys": [
      "events/abc123.jpg",
      "events/def456.png",
      "avatars/user1.jpg"
    ]
  }'
```

**Respuesta:**

```json
{
  "success": true,
  "deleted_count": 3,
  "errors": []
}
```

---

### 7. Obtener URL de Descarga

**Endpoint:** `GET /v2/s3/download/{image_key}`

Genera una URL temporal para descargar la imagen (útil para imágenes privadas).

```bash
curl "http://localhost:8006/v2/s3/download/events/abc123.jpg?expiration=1800"
```

---

### 8. Verificar si Imagen Existe

**Endpoint:** `GET /v2/s3/images/{image_key}/exists`

```bash
curl "http://localhost:8006/v2/s3/images/events/abc123.jpg/exists"
```

**Respuesta:**

```json
{
  "exists": true,
  "key": "events/abc123.jpg"
}
```

---

## Carpetas Organizativas

Se recomienda usar estas carpetas para organizar las imágenes:

- `events/` - Imágenes de eventos
- `avatars/` - Fotos de perfil de usuarios
- `calendars/` - Imágenes de calendarios
- `attachments/` - Archivos adjuntos generales

---

## Compresión Automática

Cuando se usa `/upload-direct` con `compress=true`, se aplican estas optimizaciones:

### JPEG
- Calidad: 85%
- Redimensiona si excede 1920x1080
- Optimización activada

### PNG
- Nivel de compresión: 6
- Optimización activada
- Se convierte a JPEG si no hay transparencia

### GIF/BMP
- Se convierte a JPEG (más eficiente)
- Solo se mantiene como PNG si hay transparencia

### WebP
- Calidad: 85%
- Método de compresión: 6

### SVG
- No se modifica (ya es vectorial)

### Ejemplo de Reducción

```
Original:  2.5 MB (3840x2160, JPEG 100%)
Comprimido: 345 KB (1920x1080, JPEG 85%)
Reducción: 86%
```

---

## Integración con Frontend (React/Vue)

```typescript
// Componente de subida de imagen
async function handleImageUpload(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await fetch(
      '/v2/s3/upload-direct?folder=events&compress=true',
      {
        method: 'POST',
        body: formData
      }
    );
    
    const data = await response.json();
    
    // Guardar URL en el evento/calendario
    const imageUrl = data.url;
    console.log('Imagen disponible en:', imageUrl);
    
    return imageUrl;
  } catch (error) {
    console.error('Error al subir imagen:', error);
  }
}
```

---

## Límites y Recomendaciones

- **Tamaño máximo:** 10 MB por archivo
- **Formatos permitidos:** JPEG, PNG, GIF, WebP, SVG, BMP
- **URLs presigned:** Válidas por 1 hora
- **Eliminación masiva:** Máximo 1000 archivos por petición
- **Usar compresión:** Siempre que sea posible para ahorrar costos

---

## Ejecutar con Docker

```bash
# Construir y levantar servicios
cd app
docker-compose up --build integration-service

# Ver logs
docker-compose logs -f integration-service

# Probar endpoint
curl http://localhost:8006/health
```

---

## Documentación Interactiva

Una vez el servicio esté corriendo, accede a:

```
http://localhost:8006/v2/docs
```

Allí encontrarás la documentación OpenAPI completa con ejemplos interactivos.
