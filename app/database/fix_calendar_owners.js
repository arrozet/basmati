// ============================================================================
// SCRIPT PARA CORREGIR OWNERS DE CALENDARIOS - BASMATI
// ============================================================================
// 
// Este script te permite corregir el owner (creator_external_id) de un
// calendario específico que fue asignado incorrectamente.
//
// Uso: mongosh "connection-string" --file fix_calendar_owners.js
// ============================================================================

const db = db.getSiblingDB("basmati");

print("🔧 Script de corrección de owners de calendarios\n");

// ============================================================================
// CONFIGURACIÓN - MODIFICA ESTOS VALORES SEGÚN TU CASO
// ============================================================================

// ID del calendario a corregir (puedes obtenerlo con check_calendar_owner.js)
const CALENDAR_ID_TO_FIX = "PEGA_AQUI_EL_ID_DEL_CALENDARIO";

// Nuevo owner correcto (tu external_id)
const NEW_OWNER_EXTERNAL_ID = "PEGA_AQUI_TU_EXTERNAL_ID";

// ============================================================================
// VALIDACIÓN Y CORRECCIÓN
// ============================================================================

if (CALENDAR_ID_TO_FIX === "PEGA_AQUI_EL_ID_DEL_CALENDARIO" || 
    NEW_OWNER_EXTERNAL_ID === "PEGA_AQUI_TU_EXTERNAL_ID") {
    print("❌ ERROR: Debes configurar los valores en el script antes de ejecutarlo.");
    print("");
    print("Pasos:");
    print("1. Ejecuta check_calendar_owner.js para ver los calendarios");
    print("2. Copia el ID (_id) del calendario que quieres corregir");
    print("3. Pega el ID en la variable CALENDAR_ID_TO_FIX");
    print("4. Pega tu external_id en la variable NEW_OWNER_EXTERNAL_ID");
    print("5. Ejecuta este script nuevamente");
    print("");
    quit(1);
}

// Convertir el string del ID a ObjectId
let calendar_object_id;
try {
    calendar_object_id = ObjectId(CALENDAR_ID_TO_FIX);
} catch (e) {
    print(`❌ ERROR: El ID del calendario no es válido: ${CALENDAR_ID_TO_FIX}`);
    quit(1);
}

// Buscar el calendario
const calendar = db.calendars.findOne({ _id: calendar_object_id });

if (!calendar) {
    print(`❌ ERROR: No se encontró el calendario con ID ${CALENDAR_ID_TO_FIX}`);
    quit(1);
}

print(`📅 Calendario encontrado: ${calendar.title || 'Sin título'}`);
print(`   Owner actual: ${calendar.creator_external_id}`);
print(`   Nuevo owner: ${NEW_OWNER_EXTERNAL_ID}`);
print("");

// Verificar que el nuevo owner existe
const new_owner = db.users.findOne({ external_id: NEW_OWNER_EXTERNAL_ID });
if (!new_owner) {
    print(`❌ ERROR: No existe un usuario con external_id: ${NEW_OWNER_EXTERNAL_ID}`);
    print("   Verifica que el usuario esté creado en la base de datos.");
    quit(1);
}

// Actualizar el owner del calendario
const result = db.calendars.updateOne(
    { _id: calendar_object_id },
    { $set: { creator_external_id: NEW_OWNER_EXTERNAL_ID } }
);

if (result.modifiedCount > 0) {
    print(`✅ Calendario actualizado exitosamente!`);
    print("");
    print(`📊 Detalles:`);
    print(`   - Calendarios actualizados: ${result.modifiedCount}`);
    print("");
} else {
    print(`⚠️  El calendario ya tenía el owner correcto o no se pudo actualizar.`);
}

// ============================================================================
// OPCIONAL: CORREGIR TAMBIÉN LOS EVENTOS DE ESE CALENDARIO
// ============================================================================

print("🔍 Verificando eventos del calendario...");

const events_to_update = db.events.find({ calendar_id: CALENDAR_ID_TO_FIX }).toArray();

if (events_to_update.length > 0) {
    print(`   Se encontraron ${events_to_update.length} eventos en este calendario.`);
    print("");
    print("   ¿Quieres actualizar también el creator_external_id de estos eventos?");
    print("   (Descomenta las líneas siguientes si quieres hacerlo)");
    print("");
    
    // DESCOMENTA ESTAS LÍNEAS SI QUIERES ACTUALIZAR LOS EVENTOS TAMBIÉN:
    /*
    const events_result = db.events.updateMany(
        { calendar_id: CALENDAR_ID_TO_FIX },
        { $set: { creator_external_id: NEW_OWNER_EXTERNAL_ID } }
    );
    
    print(`✅ Se actualizaron ${events_result.modifiedCount} eventos.`);
    */
} else {
    print("   No se encontraron eventos en este calendario.");
}

print("");
print("✅ Proceso completado!");

