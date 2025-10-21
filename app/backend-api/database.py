from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient = None
    
    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB"""
        try:
            cls.client = AsyncIOMotorClient(settings.mongodb_url)
            # Verify connection
            await cls.client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB!")
            logger.info(f"📊 Database: {settings.mongodb_db_name}")
        except Exception as e:
            logger.error(f"❌ Error connecting to MongoDB: {e}")
            raise
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info("🔌 MongoDB connection closed")
    
    @classmethod
    def get_db(cls):
        """Get database instance"""
        if cls.client is None:
            raise Exception("Database not connected. Call connect_db first.")
        return cls.client[settings.mongodb_db_name]


# Dependency for FastAPI endpoints
async def get_database():
    """FastAPI dependency to get database"""
    return Database.get_db()
