// ============================================================================
// QUERIES DE EJEMPLO - BASE DE DATOS BASMATI
// ============================================================================
//
// Este archivo contiene ejemplos de las operaciones principales que se
// realizarán desde los microservicios FastAPI.
//
// Usa estas queries para:
// - Probar que los índices funcionan correctamente
// - Documentar patrones de consulta en la memoria técnica
// - Base para implementar los endpoints REST
//
// ============================================================================

use basmati;

// ============================================================================
// 1. OPERACIONES SOBRE USERS
// ============================================================================

// --- Crear usuario (desde OAuth) ---
db.users.insertOne({
  external_id: "google_987654321",
  provider: "google",
  email: "nuevo@usuario.com",
  display_name: "Nuevo Usuario",
  avatar_url: "https://lh3.googleusercontent.com/a/user-photo",
  notification_preferences: {
    in_app: true,
    email: false,
    email_address: null
  },
  followed_calendar_ids: [],
  created_at: new Date(),
  last_login: new Date()
});

// --- Buscar usuario por external_id (login) ---
db.users.findOne({ external_id: "google_123456789" });

// --- Actualizar último login ---
db.users.updateOne(
  { external_id: "google_123456789" },
  { $set: { last_login: new Date() } }
);

// --- Actualizar preferencias de notificación (RF16) ---
db.users.updateOne(
  { external_id: "google_123456789" },
  { 
    $set: { 
      "notification_preferences.email": true,
      "notification_preferences.email_address": "notificaciones@email.com"
    } 
  }
);

// --- Seguir un calendario (RF11) ---
db.users.updateOne(
  { external_id: "google_123456789" },
  { $addToSet: { followed_calendar_ids: ObjectId("calendar_id_here") } }
);

// --- Dejar de seguir un calendario ---
db.users.updateOne(
  { external_id: "google_123456789" },
  { $pull: { followed_calendar_ids: ObjectId("calendar_id_here") } }
);

// --- Obtener calendarios seguidos por el usuario (RF11) ---
const user = db.users.findOne({ external_id: "google_123456789" });
db.calendars.find({ _id: { $in: user.followed_calendar_ids } });

// ============================================================================
// 2. OPERACIONES SOBRE CALENDARS
// ============================================================================

// --- Crear calendario (RF1) ---
db.calendars.insertOne({
  title: "Calendario de Deportes",
  creator_external_id: "google_123456789",
  creator_display_name: "Usuario Demo",
  keywords: ["deportes", "ejercicio", "fitness"],
  color: "#FF5722",
  icon: "sports_soccer",
  parent_calendar_id: null,
  path: [],
  description: "Calendario con eventos deportivos y entrenamientos",
  visibility: "public",
  created_at: new Date(),
  updated_at: new Date(),
  subscriber_count: 0
});

// --- Crear subcalendario (jerarquía, RF4) ---
const parentCalendar = db.calendars.findOne({ title: "Ingeniería Web 2025/26" });
db.calendars.insertOne({
  title: "Prácticas de Ingeniería Web",
  creator_external_id: "google_123456789",
  creator_display_name: "Usuario Demo",
  keywords: ["prácticas", "laboratorio", "programación"],
  color: "#4CAF50",
  icon: "code",
  parent_calendar_id: parentCalendar._id,
  path: [parentCalendar._id], // Array de ancestros
  description: "Calendario de prácticas de laboratorio",
  visibility: "public",
  created_at: new Date(),
  updated_at: new Date(),
  subscriber_count: 0
});

// --- Buscar calendarios por palabra clave (RF10) ---
db.calendars.find({ keywords: "universidad" });

// --- Búsqueda de texto completo en título/descripción (RF10) ---
db.calendars.find({ $text: { $search: "ingeniería web" } });

// --- Obtener todos los subcalendarios de un calendario (RF4) ---
db.calendars.find({ path: ObjectId("parent_calendar_id_here") });

// --- Buscar calendarios creados por un usuario ---
db.calendars.find({ creator_external_id: "google_123456789" });

// --- Actualizar calendario (RF2, solo creador) ---
db.calendars.updateOne(
  { 
    _id: ObjectId("calendar_id_here"),
    creator_external_id: "google_123456789" // Verificación de permisos
  },
  { 
    $set: { 
      title: "Nuevo título",
      updated_at: new Date()
    } 
  }
);

// --- Incrementar contador de suscriptores (desnormalizado) ---
db.calendars.updateOne(
  { _id: ObjectId("calendar_id_here") },
  { $inc: { subscriber_count: 1 } }
);

// --- Eliminar calendario (RF3, solo creador) ---
db.calendars.deleteOne({ 
  _id: ObjectId("calendar_id_here"),
  creator_external_id: "google_123456789"
});

// ============================================================================
// 3. OPERACIONES SOBRE EVENTS
// ============================================================================

// --- Crear evento (RF5) ---
db.events.insertOne({
  calendar_id: ObjectId("calendar_id_here"),
  calendar_title: "Ingeniería Web 2025/26",
  creator_external_id: "google_123456789",
  title: "Examen parcial",
  description: "Primer examen parcial de la asignatura",
  start_time: ISODate("2025-03-15T10:00:00Z"),
  end_time: ISODate("2025-03-15T12:00:00Z"),
  location: {
    address: "ETSI Informática, Málaga",
    latitude: 36.7146,
    longitude: -4.4761,
    place_name: "Aula Magna",
    map_provider: "google_maps"
  },
  attachments: [],
  comments: [],
  visibility: "inherited",
  recurrence: null, // Evento único
  created_at: new Date(),
  updated_at: new Date()
});

// --- Obtener eventos de un calendario en un mes específico ---
// (Patrón principal: vista mensual)
db.events.find({
  calendar_id: ObjectId("calendar_id_here"),
  start_time: {
    $gte: ISODate("2025-02-01T00:00:00Z"),
    $lt: ISODate("2025-03-01T00:00:00Z")
  }
}).sort({ start_time: 1 });

// --- Búsqueda de eventos por rango de fechas ---
db.events.find({
  $or: [
    {
      start_time: {
        $gte: ISODate("2025-02-01"),
        $lte: ISODate("2025-02-28")
      }
    },
    {
      end_time: {
        $gte: ISODate("2025-02-01"),
        $lte: ISODate("2025-02-28")
      }
    }
  ]
}).sort({ start_time: 1 });

// --- Búsqueda de texto completo en eventos ---
db.events.find({ $text: { $search: "examen parcial" } });

// --- Añadir comentario a evento (RF14) ---
db.events.updateOne(
  { _id: ObjectId("event_id_here") },
  {
    $push: {
      comments: {
        _id: new ObjectId(),
        author_external_id: "google_123456789",
        author_display_name: "Usuario Demo",
        text: "¿Qué temas entran en el examen?",
        created_at: new Date()
      }
    },
    $set: { updated_at: new Date() }
  }
);

// --- Añadir archivo adjunto (RF8) ---
db.events.updateOne(
  { _id: ObjectId("event_id_here") },
  {
    $push: {
      attachments: {
        _id: new ObjectId(),
        filename: "apuntes.pdf",
        url: "https://storage.googleapis.com/basmati-files/apuntes.pdf",
        size: 1048576, // 1MB
        mime_type: "application/pdf",
        uploaded_at: new Date(),
        uploaded_by: "google_123456789",
        is_image: false,
        thumbnail_url: null
      }
    }
  }
);

// --- Actualizar evento (RF6, solo creador del calendario) ---
db.events.updateOne(
  { 
    _id: ObjectId("event_id_here")
    // Nota: verificar permisos en el microservicio consultando el calendario
  },
  { 
    $set: { 
      title: "Nuevo título del evento",
      start_time: ISODate("2025-03-15T11:00:00Z"),
      updated_at: new Date()
    } 
  }
);

// --- Eliminar evento (RF7) ---
db.events.deleteOne({ _id: ObjectId("event_id_here") });

// --- Consulta avanzada: Eventos con comentarios de un usuario específico ---
db.events.find({
  "comments.author_external_id": "google_123456789"
});

// --- Buscar eventos cerca de una ubicación (geoespacial) ---
db.events.find({
  "location.latitude": { $gte: 36.7, $lte: 36.8 },
  "location.longitude": { $gte: -4.5, $lte: -4.4 }
});

// ============================================================================
// 4. OPERACIONES SOBRE NOTIFICATIONS
// ============================================================================

// --- Crear notificación (RF15) ---
db.notifications.insertOne({
  recipient_external_id: "google_123456789",
  type: "NEW_COMMENT",
  title: "Nuevo comentario en tu evento",
  message: "Alguien ha comentado en 'Examen parcial'",
  is_read: false,
  related_event_id: ObjectId("event_id_here"),
  related_calendar_id: ObjectId("calendar_id_here"),
  created_at: new Date(),
  expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) // 30 días
});

// --- Obtener notificaciones no leídas de un usuario ---
// (Patrón principal: badge de notificaciones)
db.notifications.find({
  recipient_external_id: "google_123456789",
  is_read: false
}).sort({ created_at: -1 });

// --- Contar notificaciones no leídas ---
db.notifications.countDocuments({
  recipient_external_id: "google_123456789",
  is_read: false
});

// --- Marcar notificación como leída ---
db.notifications.updateOne(
  { _id: ObjectId("notification_id_here") },
  { $set: { is_read: true } }
);

// --- Marcar todas las notificaciones como leídas ---
db.notifications.updateMany(
  { 
    recipient_external_id: "google_123456789",
    is_read: false
  },
  { $set: { is_read: true } }
);

// --- Obtener historial de notificaciones (paginado) ---
db.notifications.find({
  recipient_external_id: "google_123456789"
})
.sort({ created_at: -1 })
.limit(20)
.skip(0);

// --- Eliminar notificación ---
db.notifications.deleteOne({ _id: ObjectId("notification_id_here") });

// ============================================================================
// 5. QUERIES COMPLEJAS (AGREGACIÓN)
// ============================================================================

// --- Obtener eventos con información del calendario (lookup) ---
db.events.aggregate([
  {
    $match: {
      start_time: {
        $gte: ISODate("2025-02-01"),
        $lte: ISODate("2025-02-28")
      }
    }
  },
  {
    $lookup: {
      from: "calendars",
      localField: "calendar_id",
      foreignField: "_id",
      as: "calendar_info"
    }
  },
  {
    $unwind: "$calendar_info"
  },
  {
    $project: {
      title: 1,
      start_time: 1,
      end_time: 1,
      "calendar_info.title": 1,
      "calendar_info.color": 1
    }
  }
]);

// --- Contar eventos por calendario ---
db.events.aggregate([
  {
    $group: {
      _id: "$calendar_id",
      event_count: { $sum: 1 },
      calendar_title: { $first: "$calendar_title" }
    }
  },
  {
    $sort: { event_count: -1 }
  }
]);

// --- Obtener estadísticas de comentarios por usuario ---
db.events.aggregate([
  {
    $unwind: "$comments"
  },
  {
    $group: {
      _id: "$comments.author_external_id",
      author_name: { $first: "$comments.author_display_name" },
      total_comments: { $sum: 1 }
    }
  },
  {
    $sort: { total_comments: -1 }
  }
]);

// --- Eventos con más de 5 comentarios ---
db.events.find({
  $expr: { $gte: [{ $size: "$comments" }, 5] }
});

// --- Vista unificada: Eventos de todos los calendarios seguidos ---
const userDoc = db.users.findOne({ external_id: "google_123456789" });
db.events.aggregate([
  {
    $match: {
      calendar_id: { $in: userDoc.followed_calendar_ids },
      start_time: {
        $gte: new Date(),
        $lte: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // Próximos 7 días
      }
    }
  },
  {
    $sort: { start_time: 1 }
  },
  {
    $project: {
      title: 1,
      calendar_title: 1,
      start_time: 1,
      end_time: 1,
      location: 1
    }
  }
]);

// ============================================================================
// 6. QUERIES PARA VERIFICAR ÍNDICES
// ============================================================================

// --- Ver plan de ejecución (debe usar el índice compuesto) ---
db.events.find({
  calendar_id: ObjectId("calendar_id_here"),
  start_time: { $gte: ISODate("2025-02-01") }
}).explain("executionStats");

// --- Verificar que el índice TTL funciona ---
// (Las notificaciones con expires_at en el pasado se borrarán automáticamente)
db.notifications.find({ expires_at: { $lt: new Date() } });

// --- Verificar índice de texto completo ---
db.calendars.find({ $text: { $search: "ingeniería" } }).explain("executionStats");

// ============================================================================
// 7. OPERACIONES DE MANTENIMIENTO
// ============================================================================

// --- Estadísticas de colección ---
db.events.stats();

// --- Ver índices de una colección ---
db.events.getIndexes();

// --- Reconstruir índice (si hay problemas de rendimiento) ---
db.events.reIndex();

// --- Backup de una colección (exportar a JSON) ---
// Ejecutar desde shell:
// mongoexport --uri="connection-string" --collection=events --out=events_backup.json

// --- Restaurar desde backup ---
// mongoimport --uri="connection-string" --collection=events --file=events_backup.json

print("✅ Queries de ejemplo cargadas. Usa estas consultas para probar tu base de datos.");
