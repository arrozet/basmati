# 🔌 Guía de Integración Backend - Página de Configuración de Usuario

## 📋 Resumen

La página de configuración (`/settings`) está **completamente implementada en el frontend** usando datos MOCK. Esta guía te indica exactamente qué debes hacer para conectarla al backend.

---

## 🎯 Estado Actual

✅ **Implementado (Frontend):**
- Interfaz completa de perfil y notificaciones
- Validaciones de formularios
- Feedback visual (loading, éxito, errores)
- Accesibilidad WCAG 2.1 AA
- Arquitectura Clean (Domain, Application, Infrastructure, Presentation)

⏳ **Pendiente (Backend):**
- Conexión a endpoints reales
- Obtención del user_id desde OAuth/JWT
- Persistencia de cambios en la base de datos

---

## 🔧 Archivos Relevantes

### Frontend (Ya Implementado)
```
app/frontend/src/
├── domain/
│   ├── models/user_model.ts                      # Modelos de datos
│   └── repositories/user_repository_interface.ts # Interfaz del repositorio
├── application/user/
│   ├── get_user_profile_use_case.ts             # Caso de uso: Obtener perfil
│   ├── update_user_profile_use_case.ts          # Caso de uso: Actualizar perfil
│   └── update_notification_preferences_use_case.ts # Caso de uso: Notificaciones
├── infrastructure/repositories/
│   └── http_user_repository.ts                  # Implementación HTTP (llamadas al backend)
├── presentation/
│   ├── hooks/use_user_profile.ts               # Hook React con lógica
│   └── pages/Settings_Page.tsx                 # Componente visual
```

### Backend (A Implementar/Verificar)
```
app/backend/user_service/
├── api/v1/endpoints/users.py    # Endpoints REST
├── services/user_service.py     # Lógica de negocio
├── repositories/user_repository.py # Acceso a MongoDB
└── models/user.py               # Modelos de datos
```

---

## 📡 Endpoints Requeridos

### 1. Obtener perfil del usuario
```http
GET /v1/users/{user_id}
```

**Respuesta esperada (200 OK):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "external_id": "google_123456789",
  "provider": "google",
  "email": "usuario@example.com",
  "display_name": "Usuario Demo",
  "avatar_url": "https://...",
  "notification_preferences": {
    "in_app": true,
    "email": true,
    "email_address": null
  },
  "followed_calendar_ids": [],
  "created_at": "2025-11-23T10:00:00Z",
  "last_login": "2025-11-23T15:30:00Z"
}
```

**Errores:**
- `404 Not Found` - Usuario no existe
- `500 Internal Server Error` - Error del servidor

---

### 2. Actualizar perfil del usuario
```http
PUT /v1/users/{user_id}
Content-Type: application/json

{
  "display_name": "Nuevo Nombre",
  "email": "nuevo@email.com"
}
```

**Respuesta esperada (200 OK):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "display_name": "Nuevo Nombre",
  "email": "nuevo@email.com",
  // ... resto de campos
}
```

**Errores:**
- `400 Bad Request` - Datos inválidos (email mal formato, nombre vacío)
- `404 Not Found` - Usuario no existe
- `500 Internal Server Error` - Error del servidor

---

### 3. Actualizar preferencias de notificaciones
```http
PUT /v1/users/{user_id}
Content-Type: application/json

{
  "notification_preferences": {
    "in_app": true,
    "email": false,
    "email_address": null
  }
}
```

**Respuesta esperada (200 OK):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "notification_preferences": {
    "in_app": true,
    "email": false,
    "email_address": null
  },
  // ... resto de campos
}
```

---

## 🔐 Autenticación

### Situación Actual (MOCK)
```typescript
// frontend/src/presentation/hooks/use_user_profile.ts
const get_current_user_id = (): string => {
    return localStorage.getItem('basmati_user_id') || '';
};
```

### Implementación Final (Producción)
1. Usuario se autentica con OAuth (Google/Facebook)
2. Backend devuelve un token JWT con el `user_id`
3. Frontend guarda el token en localStorage
4. En cada request, el frontend envía el token en el header:
   ```http
   Authorization: Bearer <JWT_TOKEN>
   ```
5. Backend extrae el `user_id` del token y lo usa en las operaciones

**TODO Backend:** Implementar middleware de autenticación JWT

---

## ✅ Checklist de Integración

### Paso 1: Verificar Endpoints
```bash
# Probar obtener usuario
curl http://localhost:8000/v1/users/507f1f77bcf86cd799439011

# Probar actualizar perfil
curl -X PUT http://localhost:8000/v1/users/507f1f77bcf86cd799439011 \
  -H "Content-Type: application/json" \
  -d '{"display_name": "Test User"}'
```

### Paso 2: Configurar CORS
```python
# backend/api-gateway/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Paso 3: Activar el Hook en el Frontend
1. Abrir `app/frontend/src/presentation/pages/Settings_Page.tsx`
2. Buscar el comentario `// TODO BACKEND: Descomentar cuando el backend esté listo`
3. Descomentar las líneas marcadas:
   ```typescript
   // Línea ~6: Descomentar import
   import { use_user_profile } from '../hooks/use_user_profile';
   
   // Línea ~49: Descomentar hook y eliminar MOCK_USER_DATA
   const { user, loading, saving, error, update_preferences, update_profile } = use_user_profile();
   
   // Línea ~78: Descomentar función real
   await update_profile({ display_name, email });
   
   // Línea ~98: Descomentar función real
   await update_preferences({ ... });
   
   // Línea ~114: Descomentar estados de loading/error
   if (loading) { ... }
   if (error && !user) { ... }
   ```

### Paso 4: Probar
1. Crear un usuario en MongoDB (o usar el de `setup_basmati_db.js`)
2. Obtener su ObjectId:
   ```bash
   docker exec -it basmati-mongodb mongosh basmati --eval "db.users.findOne({email: 'usuario@example.com'})._id"
   ```
3. Guardar el ID en localStorage del navegador:
   ```javascript
   localStorage.setItem('basmati_user_id', '507f1f77bcf86cd799439011');
   ```
4. Acceder a `http://localhost:5173/settings`
5. Modificar datos y verificar que se guardan en MongoDB

---

## 🚨 Validaciones Backend Requeridas

### Perfil
```python
# Validar display_name
if not display_name or len(display_name.strip()) == 0:
    raise ValueError("El nombre no puede estar vacío")

# Validar email
import re
email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
if not re.match(email_regex, email):
    raise ValueError("Formato de email inválido")
```

### Notificaciones
```python
# Validar estructura
if "notification_preferences" in update_data:
    prefs = update_data["notification_preferences"]
    if not isinstance(prefs.get("in_app"), bool):
        raise ValueError("in_app debe ser booleano")
    if not isinstance(prefs.get("email"), bool):
        raise ValueError("email debe ser booleano")
```

---

## 📊 Formato de Datos MongoDB

```javascript
// Colección: users
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "external_id": "google_123456789",
  "provider": "google",
  "email": "usuario@example.com",
  "display_name": "Usuario Demo",
  "avatar_url": "https://lh3.googleusercontent.com/...",
  "notification_preferences": {
    "in_app": true,
    "email": true,
    "email_address": null
  },
  "followed_calendar_ids": [],
  "created_at": ISODate("2025-11-23T10:00:00Z"),
  "last_login": ISODate("2025-11-23T15:30:00Z")
}
```

---

## 🐛 Debugging

### Ver requests del frontend
Abre la consola del navegador (F12) y busca logs:
```
📝 [MOCK] Guardando perfil: { display_name: "...", email: "..." }
🔔 [MOCK] Guardando preferencias: { ... }
```

Cuando actives el backend, verás:
```
Error loading user profile: Request failed with status code 404
Error updating profile: ...
```

### Ver logs del backend
```bash
docker logs -f basmati-user-service
```

---

## 📚 Recursos Adicionales

- **Esquema de Usuario:** `app/backend/user_service/models/user.py`
- **Schemas Pydantic:** `app/backend/user_service/schemas/user.py`
- **Documentación API:** http://localhost:8001/docs (Swagger)
- **Frontend AGENTS.md:** `app/frontend/AGENTS.md` (estándares de código)

---

## 🎉 Resultado Final

Cuando todo esté conectado:
1. Usuario navega a `/settings`
2. Ve sus datos reales del backend
3. Modifica nombre/email o preferencias
4. Hace clic en "Guardar"
5. Cambios se persisten en MongoDB
6. Ve mensaje de éxito ✅
7. Los cambios se reflejan inmediatamente en la interfaz

---

## 💬 ¿Necesitas Ayuda?

- El código del frontend está completamente documentado en español
- Cada función tiene JSDoc con explicaciones
- Los comentarios `TODO BACKEND` marcan exactamente qué descomentar
- La arquitectura está separada en capas (fácil de seguir)

**¡Todo está listo para conectar! Solo necesitas descomentar unas líneas.** 🚀
