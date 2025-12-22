// ============================================================================
// SCRIPT DE ACTUALIZACIÓN DEL SCHEMA DE USERS PARA SOPORTAR FREQUENCY
// ============================================================================
// 
// Este script actualiza SOLO el validador de la colección users para permitir
// el campo 'frequency' en notification_preferences.
// NO modifica documentos existentes.
//
// Uso: 
// mongosh "mongodb+srv://..." --file update_users_schema_frequency.js
// ============================================================================

// Conectar a la base de datos
const db = db.getSiblingDB("basmati");

print("🔧 Actualizando schema de validación de la colección 'users'...\n");

// Obtener el validador actual
const currentValidator = db.getCollectionInfos({name: "users"})[0].options.validator;

// Actualizar solo la parte de notification_preferences
currentValidator.$jsonSchema.properties.notification_preferences = {
  bsonType: "object",
  properties: {
    in_app: { bsonType: "bool" },
    email: { bsonType: "bool" },
    email_address: { bsonType: ["string", "null"] },
    frequency: { bsonType: "string", enum: ["instant", "daily"] }
  },
  additionalProperties: false
};

// Aplicar el nuevo validador con validationLevel: "moderate"
// Esto permite que los documentos existentes no sean validados hasta que se actualicen
db.runCommand({
  collMod: "users",
  validator: currentValidator,
  validationLevel: "moderate"  // Permite docs existentes sin el campo frequency
});

print("✅ Schema actualizado exitosamente!");
print("   - Campo 'frequency' ahora permitido en notification_preferences");
print("   - Documentos existentes NO son afectados");
print("   - Nuevos documentos y actualizaciones incluirán el campo frequency\n");



