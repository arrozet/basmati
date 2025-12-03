// ============================================================================
// SCRIPT DE CREACIÓN DE BASE DE DATOS MONGODB - BASMATI
// ============================================================================
// 
// Instrucciones de uso:
// 1. Conecta a tu cluster de MongoDB Atlas
// 2. Ejecuta este script en mongosh o MongoDB Compass
// 3. Comando: mongosh "tu-connection-string" --file setup_basmati_db.js
//
// O copia y pega sección por sección en el MongoDB Shell
// ============================================================================

// Seleccionar/crear base de datos
const db = db.getSiblingDB("basmati");

print("🚀 Iniciando configuración de base de datos Basmati...\n");

// ============================================================================
// 1. COLECCIÓN: users
// ============================================================================
print("📦 Creando colección 'users'...");

db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["external_id", "provider", "email", "display_name", "created_at"],
      properties: {
        _id: {
          bsonType: "objectId",
          description: "ID único generado por MongoDB"
        },
        external_id: {
          bsonType: "string",
          description: "ID único del proveedor OAuth (Google ID, Facebook ID, etc.)"
        },
        provider: {
          bsonType: "string",
          enum: ["google", "facebook"],
          description: "Proveedor de autenticación OAuth 2.0"
        },
        email: {
          bsonType: "string",
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
          description: "Email del usuario"
        },
        display_name: {
          bsonType: "string",
          minLength: 1,
          maxLength: 100,
          description: "Nombre público del usuario"
        },
        avatar_url: {
          bsonType: ["string", "null"],
          description: "URL de la foto de perfil del usuario"
        },
        notification_preferences: {
          bsonType: "object",
          properties: {
            in_app: {
              bsonType: "bool",
              description: "Mostrar notificaciones al iniciar sesión"
            },
            email: {
              bsonType: "bool",
              description: "Enviar notificaciones por email"
            },
            email_address: {
              bsonType: ["string", "null"],
              description: "Email alternativo para notificaciones (opcional)"
            },
            frequency: {
              bsonType: "string",
              enum: ["instant", "daily"],
              description: "Frecuencia de notificaciones: instant (inmediato) o daily (resumen diario a las 00:00)"
            }
          },
          additionalProperties: false
        },
        followed_calendar_ids: {
          bsonType: "array",
          items: {
            bsonType: "objectId"
          },
          description: "Array de IDs de calendarios que el usuario sigue (RF11)"
        },
        created_at: {
          bsonType: "date",
          description: "Fecha de creación del usuario"
        },
        last_login: {
          bsonType: ["date", "null"],
          description: "Última fecha de inicio de sesión"
        }
      },
      additionalProperties: false
    }
  }
});

// Índices para users
print("  🔑 Creando índices para 'users'...");
db.users.createIndex(
  { "external_id": 1 }, 
  { unique: true, name: "idx_external_id" }
);
db.users.createIndex(
  { "email": 1 }, 
  { name: "idx_email" }
);
db.users.createIndex(
  { "provider": 1, "external_id": 1 }, 
  { name: "idx_provider_external" }
);

print("  ✅ Colección 'users' creada con éxito\n");

// ============================================================================
// 2. COLECCIÓN: calendars
// ============================================================================
print("📦 Creando colección 'calendars'...");

db.createCollection("calendars", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title", "creator_external_id", "creator_display_name", "created_at"],
      properties: {
        _id: {
          bsonType: "objectId"
        },
        title: {
          bsonType: "string",
          minLength: 1,
          maxLength: 200,
          description: "Título del calendario"
        },
        creator_external_id: {
          bsonType: "string",
          description: "ID externo del usuario creador (FK a users.external_id)"
        },
        creator_display_name: {
          bsonType: "string",
          description: "Nombre del creador (desnormalizado para rendimiento)"
        },
        keywords: {
          bsonType: "array",
          items: {
            bsonType: "string"
          },
          description: "Palabras clave para búsqueda (RF10)"
        },
        color: {
          bsonType: "string",
          pattern: "^#[0-9A-Fa-f]{6}$",
          description: "Color en formato HEX (#RRGGBB)"
        },
        icon: {
          bsonType: ["string", "null"],
          description: "URL o identificador del icono del calendario"
        },
        parent_calendar_id: {
          bsonType: ["objectId", "null"],
          description: "ID del calendario padre (jerarquía, RF4)"
        },
        path: {
          bsonType: "array",
          items: {
            bsonType: "objectId"
          },
          description: "Array de IDs ancestros para consultas jerárquicas eficientes"
        },
        description: {
          bsonType: ["string", "null"],
          maxLength: 5000,
          description: "Descripción detallada del calendario"
        },
        visibility: {
          bsonType: "string",
          enum: ["public", "private", "unlisted"],
          description: "Control de visibilidad del calendario"
        },
        created_at: {
          bsonType: "date"
        },
        updated_at: {
          bsonType: "date"
        },
        subscriber_count: {
          bsonType: "int",
          minimum: 0,
          description: "Contador de suscriptores (desnormalizado)"
        }
      },
      additionalProperties: false
    }
  }
});

// Índices para calendars
print("  🔑 Creando índices para 'calendars'...");
db.calendars.createIndex(
  { "creator_external_id": 1 }, 
  { name: "idx_creator" }
);
db.calendars.createIndex(
  { "keywords": 1 }, 
  { name: "idx_keywords" }
);
db.calendars.createIndex(
  { "title": "text", "description": "text" }, 
  { name: "idx_text_search", default_language: "spanish" }
);
db.calendars.createIndex(
  { "path": 1 }, 
  { name: "idx_path" }
);
db.calendars.createIndex(
  { "parent_calendar_id": 1 }, 
  { name: "idx_parent", sparse: true }
);
db.calendars.createIndex(
  { "visibility": 1, "created_at": -1 }, 
  { name: "idx_visibility_date" }
);

print("  ✅ Colección 'calendars' creada con éxito\n");

// ============================================================================
// 3. COLECCIÓN: events
// ============================================================================
print("📦 Creando colección 'events'...");

db.createCollection("events", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["calendar_id", "creator_external_id", "title", "start_time", "end_time", "created_at"],
      properties: {
        _id: {
          bsonType: "objectId"
        },
        calendar_id: {
          bsonType: "objectId",
          description: "ID del calendario al que pertenece (FK)"
        },
        calendar_title: {
          bsonType: "string",
          description: "Título del calendario (desnormalizado para vistas sin join)"
        },
        creator_external_id: {
          bsonType: "string",
          description: "ID externo del creador del evento"
        },
        title: {
          bsonType: "string",
          minLength: 1,
          maxLength: 300,
          description: "Título del evento"
        },
        description: {
          bsonType: ["string", "null"],
          maxLength: 10000,
          description: "Descripción detallada del evento"
        },
        start_time: {
          bsonType: "date",
          description: "Fecha y hora de inicio del evento"
        },
        end_time: {
          bsonType: "date",
          description: "Fecha y hora de fin del evento"
        },
        location: {
          bsonType: ["object", "null"],
          properties: {
            address: {
              bsonType: "string",
              description: "Dirección textual"
            },
            latitude: {
              bsonType: "double",
              minimum: -90,
              maximum: 90
            },
            longitude: {
              bsonType: "double",
              minimum: -180,
              maximum: 180
            },
            place_name: {
              bsonType: ["string", "null"],
              description: "Nombre del lugar (ej: 'Aula 2.3')"
            },
            map_provider: {
              bsonType: "string",
              enum: ["google_maps", "openstreetmap"],
              description: "Proveedor del mapa"
            }
          },
          additionalProperties: false
        },
        attachments: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["_id", "filename", "url", "uploaded_at"],
            properties: {
              _id: {
                bsonType: "objectId"
              },
              filename: {
                bsonType: "string"
              },
              url: {
                bsonType: "string",
                description: "URL del archivo en Google Cloud Storage"
              },
              size: {
                bsonType: "long",
                minimum: 0,
                description: "Tamaño en bytes"
              },
              mime_type: {
                bsonType: "string"
              },
              uploaded_at: {
                bsonType: "date"
              },
              uploaded_by: {
                bsonType: "string",
                description: "external_id del usuario que subió el archivo"
              },
              is_image: {
                bsonType: "bool"
              },
              thumbnail_url: {
                bsonType: ["string", "null"],
                description: "URL del thumbnail (solo para imágenes)"
              }
            },
            additionalProperties: false
          }
        },
        comments: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["_id", "author_external_id", "author_display_name", "text", "created_at"],
            properties: {
              _id: {
                bsonType: "objectId"
              },
              author_external_id: {
                bsonType: "string"
              },
              author_display_name: {
                bsonType: "string"
              },
              text: {
                bsonType: "string",
                minLength: 1,
                maxLength: 5000
              },
              created_at: {
                bsonType: "date"
              }
            },
            additionalProperties: false
          }
        },
        visibility: {
          bsonType: "string",
          enum: ["public", "private", "inherited"],
          description: "Visibilidad del evento"
        },
        recurrence: {
          bsonType: ["object", "null"],
          properties: {
            pattern: {
              bsonType: "string",
              enum: ["daily", "weekly", "monthly", "yearly"]
            },
            interval: {
              bsonType: "int",
              minimum: 1,
              description: "Cada cuántas unidades (ej: cada 2 semanas)"
            },
            days_of_week: {
              bsonType: ["array", "null"],
              items: {
                bsonType: "int",
                minimum: 0,
                maximum: 6
              },
              description: "Días de la semana (0=domingo, 6=sábado)"
            },
            end_date: {
              bsonType: ["date", "null"],
              description: "Fecha de fin de la recurrencia"
            },
            exceptions: {
              bsonType: "array",
              items: {
                bsonType: "date"
              },
              description: "Fechas específicas donde NO ocurre el evento"
            }
          },
          additionalProperties: false
        },
        created_at: {
          bsonType: "date"
        },
        updated_at: {
          bsonType: "date"
        }
      },
      additionalProperties: false
    }
  }
});

// Índices para events
print("  🔑 Creando índices para 'events'...");
db.events.createIndex(
  { "calendar_id": 1, "start_time": -1 }, 
  { name: "idx_calendar_starttime" }
);
db.events.createIndex(
  { "start_time": 1, "end_time": 1 }, 
  { name: "idx_timerange" }
);
db.events.createIndex(
  { "creator_external_id": 1 }, 
  { name: "idx_creator" }
);
db.events.createIndex(
  { "title": "text", "description": "text" }, 
  { name: "idx_text_search", default_language: "spanish" }
);
// Índice geoespacial para búsquedas por ubicación
db.events.createIndex(
  { "location.latitude": 1, "location.longitude": 1 }, 
  { name: "idx_geolocation", sparse: true }
);

print("  ✅ Colección 'events' creada con éxito\n");

// ============================================================================
// 4. COLECCIÓN: notifications
// ============================================================================
print("📦 Creando colección 'notifications'...");

db.createCollection("notifications", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["recipient_external_id", "type", "title", "message", "created_at"],
      properties: {
        _id: {
          bsonType: "objectId"
        },
        recipient_external_id: {
          bsonType: "string",
          description: "ID externo del usuario destinatario"
        },
        type: {
          bsonType: "string",
          enum: ["NEW_COMMENT", "EVENT_UPDATE", "CALENDAR_INVITE", "EVENT_REMINDER"],
          description: "Tipo de notificación"
        },
        title: {
          bsonType: "string",
          maxLength: 200,
          description: "Título de la notificación"
        },
        message: {
          bsonType: "string",
          maxLength: 1000,
          description: "Mensaje descriptivo"
        },
        is_read: {
          bsonType: "bool",
          description: "Marca si ha sido leída"
        },
        related_event_id: {
          bsonType: ["objectId", "null"],
          description: "ID del evento relacionado (opcional)"
        },
        related_calendar_id: {
          bsonType: ["objectId", "null"],
          description: "ID del calendario relacionado (opcional)"
        },
        created_at: {
          bsonType: "date"
        },
        expires_at: {
          bsonType: ["date", "null"],
          description: "Fecha de expiración (para limpieza automática)"
        }
      },
      additionalProperties: false
    }
  }
});

// Índices para notifications
print("  🔑 Creando índices para 'notifications'...");
db.notifications.createIndex(
  { "recipient_external_id": 1, "is_read": 1, "created_at": -1 }, 
  { name: "idx_recipient_read_date" }
);
// Índice TTL para expiración automática de notificaciones
db.notifications.createIndex(
  { "expires_at": 1 }, 
  { expireAfterSeconds: 0, name: "idx_ttl_expiration" }
);
db.notifications.createIndex(
  { "related_event_id": 1 }, 
  { name: "idx_event", sparse: true }
);

print("  ✅ Colección 'notifications' creada con éxito\n");

// ============================================================================
// 5. COLECCIÓN: geocode_cache
// ============================================================================
print("📦 Creando colección 'geocode_cache'...");

db.createCollection("geocode_cache", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["cache_key", "query_type", "query_params", "response_data", "expires_at", "created_at", "schema_version"],
      properties: {
        _id: {
          bsonType: "objectId",
          description: "ID único generado por MongoDB"
        },
        cache_key: {
          bsonType: "string",
          description: "Clave única de la consulta (hash de parámetros)"
        },
        query_type: {
          bsonType: "string",
          enum: ["geocode", "reverse", "search"],
          description: "Tipo de consulta de geocodificación"
        },
        query_params: {
          bsonType: "object",
          description: "Parámetros originales de la consulta"
        },
        response_data: {
          bsonType: "object",
          description: "Respuesta de la API cacheada"
        },
        created_at: {
          bsonType: "date",
          description: "Fecha de creación del registro"
        },
        expires_at: {
          bsonType: "date",
          description: "Fecha de expiración para TTL automático"
        },
        hit_count: {
          bsonType: "int",
          minimum: 0,
          description: "Número de veces que se ha utilizado este caché"
        },
        last_accessed: {
          bsonType: "date",
          description: "Última vez que se accedió a este registro"
        },
        schema_version: {
          bsonType: "int",
          minimum: 1,
          description: "Versión del esquema del documento"
        }
      },
      additionalProperties: false
    }
  }
});

// Índices para geocode_cache
print("  🔑 Creando índices para 'geocode_cache'...");
// Índice único en cache_key para búsquedas rápidas O(1)
db.geocode_cache.createIndex(
  { "cache_key": 1 }, 
  { unique: true, name: "idx_cache_key_unique" }
);
// Índice TTL para expiración automática (MongoDB elimina documentos expirados)
db.geocode_cache.createIndex(
  { "expires_at": 1 }, 
  { expireAfterSeconds: 0, name: "idx_ttl_expiration" }
);
// Índice en query_type para estadísticas y consultas por tipo
db.geocode_cache.createIndex(
  { "query_type": 1 }, 
  { name: "idx_query_type" }
);

print("  ✅ Colección 'geocode_cache' creada con éxito\n");

// ============================================================================
// 6. DATOS DE EJEMPLO (SEED DATA)
// ============================================================================
print("🌱 Insertando datos de ejemplo...\n");

// Usuario de ejemplo
const exampleUser = {
  external_id: "google_123456789",
  provider: "google",
  email: "usuario@example.com",
  display_name: "Usuario Demo",
  avatar_url: "https://lh3.googleusercontent.com/a/default-user",
  notification_preferences: {
    in_app: true,
    email: true,
    email_address: null
  },
  followed_calendar_ids: [],
  created_at: new Date(),
  last_login: new Date()
};

const userResult = db.users.insertOne(exampleUser);
print(`  👤 Usuario creado: ${userResult.insertedId}`);

// Calendario de ejemplo
const exampleCalendar = {
  title: "Ingeniería Web 2025/26",
  creator_external_id: exampleUser.external_id,
  creator_display_name: exampleUser.display_name,
  keywords: ["universidad", "ingeniería", "web", "programación"],
  color: "#4285F4",
  icon: "school",
  parent_calendar_id: null,
  path: [],
  description: "Calendario de la asignatura Ingeniería Web del curso 2025/26",
  visibility: "public",
  created_at: new Date(),
  updated_at: new Date(),
  subscriber_count: 0
};

const calendarResult = db.calendars.insertOne(exampleCalendar);
print(`  📅 Calendario creado: ${calendarResult.insertedId}`);

// Evento de ejemplo
const exampleEvent = {
  calendar_id: calendarResult.insertedId,
  calendar_title: exampleCalendar.title,
  creator_external_id: exampleUser.external_id,
  title: "Clase de introducción a NoSQL",
  description: "Primera clase sobre bases de datos NoSQL y MongoDB. Cubriremos diseño de esquemas y patrones de modelado.",
  start_time: new Date("2025-02-03T09:00:00Z"),
  end_time: new Date("2025-02-03T11:00:00Z"),
  location: {
    address: "Escuela Técnica Superior de Ingeniería Informática, Málaga",
    latitude: 36.7146,
    longitude: -4.4761,
    place_name: "Aula 2.3",
    map_provider: "google_maps"
  },
  attachments: [],
  comments: [
    {
      _id: new ObjectId(),
      author_external_id: exampleUser.external_id,
      author_display_name: exampleUser.display_name,
      text: "¡No olvidéis traer el portátil para la práctica!",
      created_at: new Date()
    }
  ],
  visibility: "inherited",
  recurrence: {
    pattern: "weekly",
    interval: 1,
    days_of_week: [1, 3], // Lunes y miércoles
    end_date: new Date("2025-06-30T23:59:59Z"),
    exceptions: []
  },
  created_at: new Date(),
  updated_at: new Date()
};

const eventResult = db.events.insertOne(exampleEvent);
print(`  📌 Evento creado: ${eventResult.insertedId}`);

// Notificación de ejemplo
const exampleNotification = {
  recipient_external_id: exampleUser.external_id,
  type: "NEW_COMMENT",
  title: "Nuevo comentario en tu evento",
  message: "Usuario Demo ha comentado en 'Clase de introducción a NoSQL'",
  is_read: false,
  related_event_id: eventResult.insertedId,
  related_calendar_id: calendarResult.insertedId,
  created_at: new Date(),
  expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) // 30 días
};

const notificationResult = db.notifications.insertOne(exampleNotification);
print(`  🔔 Notificación creada: ${notificationResult.insertedId}`);

// ============================================================================
// 7. VERIFICACIÓN FINAL
// ============================================================================
print("\n📊 Verificación de la base de datos:\n");
print(`  👥 Usuarios: ${db.users.countDocuments()}`);
print(`  📅 Calendarios: ${db.calendars.countDocuments()}`);
print(`  📌 Eventos: ${db.events.countDocuments()}`);
print(`  🔔 Notificaciones: ${db.notifications.countDocuments()}`);
print(`  🗺️  Caché de geocodificación: ${db.geocode_cache.countDocuments()}`);

print("\n✅ ¡Base de datos Basmati configurada exitosamente!\n");
print("📝 Colecciones creadas:");
print("   - users (con validación de esquema e índices)");
print("   - calendars (con validación de esquema e índices)");
print("   - events (con validación de esquema e índices)");
print("   - notifications (con validación de esquema, índices y TTL)");
print("   - geocode_cache (con validación de esquema, índices y TTL)");
print("\n💡 Próximos pasos:");
print("   1. Conecta tu aplicación usando la URI de MongoDB Atlas");
print("   2. Implementa los microservicios REST con FastAPI");
print("   3. Prueba las operaciones CRUD con los datos de ejemplo\n");
