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
# Validar que no se use wildcard en producción
cors_origins_str = settings.cors_origins
if cors_origins_str == "*":
    if settings.environment == "production":
        raise ValueError(
            "❌ ERROR DE SEGURIDAD: CORS con wildcard '*' no permitido en producción. "
            "Configure CORS_ORIGINS con los dominios permitidos separados por comas."
        )
    else:
        print("⚠️  ADVERTENCIA: CORS configurado para permitir todos los orígenes. "
              "En producción, configure CORS_ORIGINS con dominios específicos.")
    allowed_origins = ["*"]
else:
    # Parsear lista de orígenes separados por comas
    allowed_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
