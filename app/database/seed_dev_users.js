// ============================================================================
// SCRIPT DE SEED DE USUARIOS DE DESARROLLO - BASMATI
// ============================================================================
// 
// Crea los usuarios de desarrollo necesarios para probar el sistema:
// - user_dev_1: Usuario principal con email matemes897@badfist.com
// - user_dev_2: Usuario secundario con email mbduz@comfythings.com
//
// Uso: mongosh "connection-string" --file seed_dev_users.js
// ============================================================================

const db = db.getSiblingDB("basmati");

print("🌱 Creando usuarios de desarrollo...\n");

// ============================================================================
// Usuario de desarrollo 1 (Principal)
// ============================================================================
const user_dev_1 = {
    external_id: "user_dev_1",
    provider: "google",
    email: "matemes897@badfist.com",
    display_name: "Usuario Desarrollo 1",
    avatar_url: null,
    notification_preferences: {
        in_app: true,
        email: true,
        email_address: null,
        frequency: "instant"  // Nueva propiedad V2
    },
    followed_calendar_ids: [],
    created_at: new Date(),
    last_login: new Date(),
    schema_version: 2
};

// Upsert: actualizar si existe, insertar si no
const result1 = db.users.updateOne(
    { external_id: "user_dev_1" },
    { $set: user_dev_1 },
    { upsert: true }
);

if (result1.upsertedId) {
    print(`  ✅ Usuario user_dev_1 creado: ${result1.upsertedId}`);
} else {
    print(`  🔄 Usuario user_dev_1 actualizado`);
}

// ============================================================================
// Usuario de desarrollo 2 (Secundario para pruebas de notificaciones)
// ============================================================================
const user_dev_2 = {
    external_id: "user_dev_2",
    provider: "google",
    email: "mbduz@comfythings.com",
    display_name: "Usuario Desarrollo 2",
    avatar_url: null,
    notification_preferences: {
        in_app: true,
        email: true,
        email_address: null,
        frequency: "instant"  // Nueva propiedad V2
    },
    followed_calendar_ids: [],
    created_at: new Date(),
    last_login: new Date(),
    schema_version: 2
};

const result2 = db.users.updateOne(
    { external_id: "user_dev_2" },
    { $set: user_dev_2 },
    { upsert: true }
);

if (result2.upsertedId) {
    print(`  ✅ Usuario user_dev_2 creado: ${result2.upsertedId}`);
} else {
    print(`  🔄 Usuario user_dev_2 actualizado`);
}

// ============================================================================
// Usuario de desarrollo 3 (Con frecuencia diaria para probar digest)
// ============================================================================
const user_dev_3 = {
    external_id: "user_dev_3",
    provider: "google",
    email: "daily_digest_test@example.com",
    display_name: "Usuario Resumen Diario",
    avatar_url: null,
    notification_preferences: {
        in_app: true,
        email: true,
        email_address: null,
        frequency: "daily"  // Frecuencia diaria para pruebas
    },
    followed_calendar_ids: [],
    created_at: new Date(),
    last_login: new Date(),
    schema_version: 2
};

const result3 = db.users.updateOne(
    { external_id: "user_dev_3" },
    { $set: user_dev_3 },
    { upsert: true }
);

if (result3.upsertedId) {
    print(`  ✅ Usuario user_dev_3 creado: ${result3.upsertedId}`);
} else {
    print(`  🔄 Usuario user_dev_3 actualizado`);
}

// ============================================================================
// Verificación
// ============================================================================
print("\n📊 Usuarios de desarrollo en el sistema:\n");

const devUsers = db.users.find({ external_id: { $regex: /^user_dev_/ } }).toArray();
devUsers.forEach(user => {
    print(`  👤 ${user.external_id}`);
    print(`     Email: ${user.email}`);
    print(`     Display: ${user.display_name}`);
    print(`     Frecuencia: ${user.notification_preferences?.frequency || 'instant'}`);
    print("");
});

print("✅ Seed de usuarios de desarrollo completado\n");
print("📝 Notas:");
print("   - user_dev_1: Usuario principal para pruebas normales");
print("   - user_dev_2: Usuario secundario para probar comentarios/notificaciones");
print("   - user_dev_3: Usuario con frecuencia 'daily' para probar resumen diario");
print("\n💡 Para cambiar de usuario en el frontend:");
print("   localStorage.setItem('basmati_current_user', 'user_dev_2')");
print("   // Luego recargar la página\n");
