// ============================================================================
// SCRIPT DE CREACIÓN DE BASE DE DATOS MONGODB - BASMATI (VERSIÓN SIMPLE)
// ============================================================================
// 
// Esta versión solo crea las colecciones con validadores e índices.
// NO incluye datos de ejemplo.
//
// Uso: mongosh "connection-string" --file setup_basmati_simple.js
// ============================================================================

// Seleccionar/crear base de datos
const db = db.getSiblingDB("basmati");

// ============================================================================
// CREAR COLECCIONES CON VALIDADORES
// ============================================================================

// users
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["external_id", "provider", "email", "display_name", "created_at"],
      properties: {
        external_id: { bsonType: "string" },
        provider: { bsonType: "string", enum: ["google", "facebook"] },
        email: { bsonType: "string" },
        display_name: { bsonType: "string" },
        avatar_url: { bsonType: ["string", "null"] },
        notification_preferences: {
          bsonType: "object",
          properties: {
            in_app: { bsonType: "bool" },
            email: { bsonType: "bool" },
            email_address: { bsonType: ["string", "null"] }
          }
        },
        followed_calendar_ids: { bsonType: "array", items: { bsonType: "objectId" } },
        created_at: { bsonType: "date" },
        last_login: { bsonType: ["date", "null"] }
      }
    }
  }
});

db.users.createIndex({ "external_id": 1 }, { unique: true });
db.users.createIndex({ "email": 1 });
db.users.createIndex({ "provider": 1, "external_id": 1 });

// calendars
db.createCollection("calendars", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title", "creator_external_id", "created_at"],
      properties: {
        title: { bsonType: "string" },
        creator_external_id: { bsonType: "string" },
        creator_display_name: { bsonType: "string" },
        keywords: { bsonType: "array", items: { bsonType: "string" } },
        color: { bsonType: "string" },
        icon: { bsonType: ["string", "null"] },
        parent_calendar_id: { bsonType: ["objectId", "null"] },
        path: { bsonType: "array", items: { bsonType: "objectId" } },
        description: { bsonType: ["string", "null"] },
        visibility: { bsonType: "string", enum: ["public", "private", "unlisted"] },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" },
        subscriber_count: { bsonType: "int", minimum: 0 }
      }
    }
  }
});

db.calendars.createIndex({ "creator_external_id": 1 });
db.calendars.createIndex({ "keywords": 1 });
db.calendars.createIndex({ "title": "text", "description": "text" }, { default_language: "spanish" });
db.calendars.createIndex({ "path": 1 });
db.calendars.createIndex({ "parent_calendar_id": 1 }, { sparse: true });
db.calendars.createIndex({ "visibility": 1, "created_at": -1 });

// events
db.createCollection("events", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["calendar_id", "creator_external_id", "title", "start_time", "end_time", "created_at"],
      properties: {
        calendar_id: { bsonType: "objectId" },
        calendar_title: { bsonType: "string" },
        creator_external_id: { bsonType: "string" },
        title: { bsonType: "string" },
        description: { bsonType: ["string", "null"] },
        start_time: { bsonType: "date" },
        end_time: { bsonType: "date" },
        location: {
          bsonType: ["object", "null"],
          properties: {
            address: { bsonType: "string" },
            latitude: { bsonType: "double", minimum: -90, maximum: 90 },
            longitude: { bsonType: "double", minimum: -180, maximum: 180 },
            place_name: { bsonType: ["string", "null"] },
            map_provider: { bsonType: "string", enum: ["google_maps", "openstreetmap"] }
          }
        },
        attachments: { bsonType: "array" },
        comments: { bsonType: "array" },
        visibility: { bsonType: "string", enum: ["public", "private", "inherited"] },
        recurrence: {
          bsonType: ["object", "null"],
          properties: {
            pattern: { bsonType: "string", enum: ["daily", "weekly", "monthly", "yearly"] },
            interval: { bsonType: "int", minimum: 1 },
            days_of_week: { bsonType: ["array", "null"] },
            end_date: { bsonType: ["date", "null"] },
            exceptions: { bsonType: "array", items: { bsonType: "date" } }
          }
        },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" }
      }
    }
  }
});

db.events.createIndex({ "calendar_id": 1, "start_time": -1 });
db.events.createIndex({ "start_time": 1, "end_time": 1 });
db.events.createIndex({ "creator_external_id": 1 });
db.events.createIndex({ "title": "text", "description": "text" }, { default_language: "spanish" });
db.events.createIndex({ "location.latitude": 1, "location.longitude": 1 }, { sparse: true });

// notifications
db.createCollection("notifications", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["recipient_external_id", "type", "title", "message", "created_at"],
      properties: {
        recipient_external_id: { bsonType: "string" },
        type: { bsonType: "string", enum: ["NEW_COMMENT", "EVENT_UPDATE", "CALENDAR_INVITE", "EVENT_REMINDER"] },
        title: { bsonType: "string" },
        message: { bsonType: "string" },
        is_read: { bsonType: "bool" },
        related_event_id: { bsonType: ["objectId", "null"] },
        related_calendar_id: { bsonType: ["objectId", "null"] },
        created_at: { bsonType: "date" },
        expires_at: { bsonType: ["date", "null"] }
      }
    }
  }
});

db.notifications.createIndex({ "recipient_external_id": 1, "is_read": 1, "created_at": -1 });
db.notifications.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 });
db.notifications.createIndex({ "related_event_id": 1 }, { sparse: true });

print("✅ Base de datos 'basmati' creada con 4 colecciones, validadores e índices");
