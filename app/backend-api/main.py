from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import Database, get_database
from config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application"""
    # Startup
    logger.info("🚀 Starting Basmati Backend API...")
    await Database.connect_db()
    yield
    # Shutdown
    logger.info("👋 Shutting down Basmati Backend API...")
    await Database.close_db()


# Create FastAPI app
app = FastAPI(
    title="Basmati Backend API",
    description="API Backend for Basmati platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "status": "online",
        "message": "Welcome to Basmati Backend API",
        "version": "1.0.0",
        "environment": settings.environment
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected" if Database.client else "disconnected"
    }


@app.get("/api/test-db")
async def test_database(db=Depends(get_database)):
    """Test database connection and list collections"""
    try:
        # List all collections
        collections = await db.list_collection_names()
        
        # Get database stats
        stats = await db.command("dbstats")
        
        return {
            "status": "success",
            "message": "Database connection is working",
            "database": settings.mongodb_db_name,
            "collections": collections,
            "stats": {
                "collections_count": stats.get("collections", 0),
                "data_size": stats.get("dataSize", 0),
                "storage_size": stats.get("storageSize", 0)
            }
        }
    except Exception as e:
        logger.error(f"Database test error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


# Example endpoint with database operation
@app.get("/api/example")
async def example_endpoint(db=Depends(get_database)):
    """Example endpoint that interacts with database"""
    try:
        # Example: Insert a test document
        collection = db["test_collection"]
        result = await collection.insert_one({"message": "Hello from Basmati API!", "timestamp": "2025-10-21"})
        
        # Retrieve the document
        document = await collection.find_one({"_id": result.inserted_id})
        
        # Convert ObjectId to string for JSON serialization
        if document:
            document["_id"] = str(document["_id"])
        
        return {
            "status": "success",
            "data": document
        }
    except Exception as e:
        logger.error(f"Example endpoint error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
