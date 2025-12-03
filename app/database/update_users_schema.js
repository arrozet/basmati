// ============================================================================
// SCRIPT DE ACTUALIZACIÓN DEL SCHEMA DE USERS PARA SOPORTAR FREQUENCY
// ============================================================================
// 
// Este script actualiza el validador de la colección users para incluir
// el campo 'frequency' en notification_preferences (V2).
//
// Uso: mongosh "connection-string" --file update_users_schema.js
// ============================================================================

const db = db.getSiblingDB("basmati");

// Actualizar el validador de la colección users
db.runCommand({
  collMod: "users",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["external_id", "provider", "email", "display_name", "created_at"],
      additionalProperties: true,
      properties: {
        external_id: { bsonType: "string" },
        provider: { bsonType: "string", enum: ["google", "facebook"] },
        email: { bsonType: "string" },
        display_name: { bsonType: "string" },
        avatar_url: { bsonType: ["string", "null"] },
        notification_preferences: {
          bsonType: "object",
          additionalProperties: false,
          properties: {
            in_app: { bsonType: "bool" },
            email: { bsonType: "bool" },
            email_address: { bsonType: ["string", "null"] },
            frequency: { bsonType: "string", enum: ["instant", "daily"] }
          }
        },
        followed_calendar_ids: { bsonType: "array", items: { bsonType: "objectId" } },
        created_at: { bsonType: "date" },
        last_login: { bsonType: ["date", "null"] }
      }
    }
  },
  validationLevel: "moderate"
});

print("✅ Schema de 'users' actualizado para soportar notification_preferences.frequency");
