from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Core imports
from core.database import Database
from core.config import settings

# API routers
from api.v1.router import api_router as api_v1_router

# Schemas
from schemas.common import HealthResponse

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
    logger.info("Starting Basmati Backend API v%s...", settings.environment)
    await Database.connect_db()
    yield
    # Shutdown
    logger.info("Shutting down Basmati Backend API...")
    await Database.close_db()


# Create FastAPI app
app = FastAPI(
    title="Basmati Backend API",
    description="""
    ## API REST para la plataforma Basmati
    
    ### Características
    
    - **Versionado**: API versionada con prefijo `/api/v1/`
    - **Async**: Todos los endpoints son asíncronos
    - **Validación**: Validación automática con Pydantic
    - **Documentación**: Documentación interactiva automática
    
    ### Versiones disponibles
    
    - **v1**: Versión actual de la API
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(
    api_v1_router,
    prefix="/api/v1",
    responses={
        404: {"description": "Recurso no encontrado"},
        422: {"description": "Error de validación"},
        500: {"description": "Error interno del servidor"}
    }
)


# Root endpoints (no versionados)
@app.get(
    "/",
    tags=["Root"],
    summary="API Info",
    description="Información general de la API"
)
async def root():
    """Root endpoint - API status and info"""
    return {
        "name": "Basmati Backend API",
        "version": "1.0.0",
        "status": "online",
        "environment": settings.environment,
        "docs": "/docs",
        "api_v1": "/api/v1"
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Root"],
    summary="Health Check",
    description="Verificar el estado del servicio y la base de datos"
)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected" if Database.client else "disconnected",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
