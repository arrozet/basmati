// ============================================================================
// SCRIPT DE ACTUALIZACIÓN DE SCHEMA - CALENDARS (COMENTARIOS)
// ============================================================================

const db = db.getSiblingDB("basmati");

print("🚀 Actualizando schema de 'calendars' para permitir comentarios...\n");

db.runCommand({
  collMod: "calendars",
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
        },
        comments: {
          bsonType: "array",
          description: "Comentarios asociados al calendario",
          items: {
            bsonType: "object",
            required: ["_id", "author_external_id", "author_display_name", "text", "created_at"],
            properties: {
              _id: { bsonType: "objectId" },
              author_external_id: { bsonType: "string" },
              author_display_name: { bsonType: "string" },
              text: { bsonType: "string" },
              created_at: { bsonType: "date" }
            },
            additionalProperties: true
          }
        }
      },
      additionalProperties: false
    }
  }
});

print("✅ Schema de 'calendars' actualizado correctamente.");
