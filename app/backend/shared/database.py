"""
Gestión centralizada de conexión a MongoDB.

Proporciona una conexión reutilizable a la base de datos MongoDB Atlas
para todos los microservicios. Utiliza motor (async driver para MongoDB).
"""
from typing import Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient
from shared.config import settings

class Database:
    """
    Clase para manejar la conexión a MongoDB.
    
    Se instancia una sola vez por microservicio y se reutiliza en todas las requests.
    Proporciona métodos para conectar y desconectar de la base de datos.
    """
    client: Any = None
    db: Optional[object] = None
    
    def __init__(self):
        """Inicializa la instancia de base de datos"""
        self.client = None
        self.db = None

# Instancia global del gestor de base de datos
db = Database()

async def connect_to_mongo():
    """
    Establece conexión con MongoDB Atlas.
    
    Se debe llamar en el evento startup de FastAPI.
    Crea la conexión usando la URI desde las variables de entorno.
    """
    db.client = AsyncIOMotorClient(settings.mongo_uri)
    db.db = db.client[settings.database_name]
    print(f"✅ Conectado a MongoDB: {settings.database_name}")

async def close_mongo_connection():
    """
    Cierra la conexión con MongoDB.
    
    Se debe llamar en el evento shutdown de FastAPI.
    Limpia los recursos utilizados por la conexión.
    """
    if db.client:
        db.client.close()
        print("✅ Desconectado de MongoDB")

def get_database():
    """
    Retorna la instancia de la base de datos.
    
    Returns:
        La conexión a la base de datos para operaciones async
        
    Nota:
        Esta función se utiliza con FastAPI's Depends() para inyectar
        la conexión en los endpoints.
    """
    return db.db
