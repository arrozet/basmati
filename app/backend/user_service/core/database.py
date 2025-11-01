"""Configuración de conexión a MongoDB"""
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings

class Database:
    """Clase para manejar la conexión a MongoDB"""
    client: AsyncIOMotorClient = None
    
    def __init__(self):
        self.client = None
        self.db = None

db = Database()

async def connect_to_mongo():
    """Establece conexión con MongoDB"""
    db.client = AsyncIOMotorClient(settings.mongo_uri)
    db.db = db.client[settings.database_name]

async def close_mongo_connection():
    """Cierra la conexión con MongoDB"""
    if db.client:
        db.client.close()

def get_database():
    """Retorna la instancia de la base de datos"""
    return db.db
