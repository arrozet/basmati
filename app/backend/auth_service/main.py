"""
AuthService - Servicio de autenticación OAuth.
Puerto: 8005
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.auth_routes import router as auth_router
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor del ciclo de vida de la aplicación.
    
    Startup: Inicializa el servicio
    Shutdown: Limpieza de recursos
    """
    # Startup
    print(f"🔐 Auth Service iniciado en puerto {settings.service_port}")
    print(f"   Google OAuth configurado: {'✅' if settings.google_client_id else '❌'}")
    yield
    # Shutdown
    print("🔐 Auth Service detenido")


app = FastAPI(
    title="Basmati Auth Service",
    description="Servicio de autenticación OAuth para Basmati",
    version="1.0.0",
    lifespan=lifespan
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, limitar a dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(auth_router, prefix="/v1")


@app.get("/health")
async def health_check():
    """
    Verifica el estado del servicio de autenticación.
    
    Returns:
        dict: Estado del servicio y configuración OAuth
    """
    return {
        "status": "healthy",
        "service": "auth-service",
        "port": settings.service_port,
        "google_oauth_configured": bool(settings.google_client_id)
    }
