"""
API Gateway principal para Basmati.
Punto de entrada centralizado para todos los servicios de backend.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
import httpx
from core.config import SERVICES, settings
from core.openapi_aggregator import aggregate_openapi_specs
from core.auth_middleware import AuthMiddleware

# Variable para cachear el schema OpenAPI customizado
_custom_openapi_schema = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor del ciclo de vida de la aplicación.

    Startup: Carga el schema OpenAPI agregado de todos los servicios
    Shutdown: Limpieza si fuera necesaria
    """
    global _custom_openapi_schema

    # Startup: Cargar schema OpenAPI de todos los servicios
    print("🔄 Cargando especificaciones OpenAPI de los servicios backend...")
    try:
        _custom_openapi_schema = await aggregate_openapi_specs(force_refresh=True)
        num_paths = len(_custom_openapi_schema.get('paths', {}))
        num_schemas = len(_custom_openapi_schema.get('components', {}).get('schemas', {}))
        print(f"✅ Schema OpenAPI cargado: {num_paths} rutas, {num_schemas} schemas")

        # Contar request bodies
        request_bodies_count = 0
        for path, path_item in _custom_openapi_schema.get('paths', {}).items():
            for method, operation in path_item.items():
                if isinstance(operation, dict) and 'requestBody' in operation:
                    request_bodies_count += 1

        print(f"   📝 {request_bodies_count} operaciones con requestBody")
    except Exception as e:
        print(f"⚠️  Error cargando OpenAPI specs: {e}")
        # Continuar sin el schema customizado
        _custom_openapi_schema = None

    yield

    # Shutdown
    _custom_openapi_schema = None

app = FastAPI(
    title="Basmati API Gateway",
    description="Punto de entrada centralizado para todos los servicios de Basmati",
    version="1.0.0",
    lifespan=lifespan,
    root_path="/api"  # Prefix para proxy Nginx
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

# Middleware de autenticación
# NOTA: Desactivado por defecto para desarrollo. Activar en producción.
if settings.enable_auth_middleware:
    app.add_middleware(AuthMiddleware)

def custom_openapi():
    """
    Sobrescribe la generación de OpenAPI para usar nuestro schema agregado.

    Esto hace que la documentación de FastAPI (/docs) muestre todos los
    endpoints de los servicios backend con sus request bodies y schemas.
    """
    global _custom_openapi_schema

    if _custom_openapi_schema is not None:
        return _custom_openapi_schema

    # Fallback: generar schema básico de FastAPI si aún no se ha cargado
    if app.openapi_schema:
        return app.openapi_schema
    
    # Generar schema por defecto con la estructura mínima válida
    from fastapi.openapi.utils import get_openapi
    schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = schema
    return schema

# Sobrescribir el método openapi de FastAPI
app.openapi = custom_openapi

@app.get("/health")
async def health_check():
    """
    Verifica el estado del API Gateway y sus servicios.

    Returns:
        dict: Estado del gateway y disponibilidad de servicios
    """
    return {"status": "healthy", "service": "api-gateway"}

@app.get("/openapi.json", include_in_schema=False)
async def get_openapi():
    """
    Endpoint explícito para servir la especificación OpenAPI combinada.

    Returns:
        dict: Especificación OpenAPI agregada de todos los servicios
    """
    global _custom_openapi_schema

    # Usar el schema cacheado si está disponible
    if _custom_openapi_schema is not None:
        return _custom_openapi_schema

    # Si no está cacheado, generarlo (útil para testing)
    return await aggregate_openapi_specs()

async def proxy_request(service_name: str, path: str, request: Request):
    """
    Proxifica una petición al servicio backend correspondiente.
    
    Args:
        service_name: Nombre del servicio destino
        path: Ruta dentro del servicio
        request: Petición original del cliente
        
    Returns:
        JSONResponse: Respuesta del servicio backend
    """
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Servicio {service_name} no encontrado")
    
    service_url = SERVICES[service_name]
    full_url = f"{service_url}/{path}"
    
    # Agregar query parameters si existen
    if request.url.query:
        full_url = f"{full_url}?{request.url.query}"
    
    try:
        async with httpx.AsyncClient(timeout=180.0, follow_redirects=False) as client:
            response = await client.request(
                method=request.method,
                url=full_url,
                headers=dict(request.headers),
                content=await request.body()
            )
            
            # Si es un redirect, pasarlo directamente al cliente
            if response.status_code in (301, 302, 303, 307, 308):
                location = response.headers.get("location")
                if location:
                    return RedirectResponse(url=location, status_code=response.status_code)
            
            return JSONResponse(
                status_code=response.status_code,
                content=response.json() if response.text else {}
            )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail=f"Timeout al conectar con {service_name}"
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=f"No se pudo conectar con {service_name}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Rutas específicas para cada servicio (elimina duplicación)
@app.api_route("/v1/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def users_route(path: str, request: Request):
    """
    Proxy para el User Service.
    
    Ejemplos:
        GET /v1/users → http://user-service:8001/v1/users
        GET /v1/users/123 → http://user-service:8001/v1/users/123
        GET /v1/users/search/by-email?email=test@example.com → http://user-service:8001/v1/users/search/by-email?email=test@example.com
    """
    full_path = f"v1/users/{path}" if path else "v1/users"
    return await proxy_request("users", full_path, request)

@app.api_route("/v1/calendars/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def calendars_route(path: str, request: Request):
    """
    Proxy para el Calendar Service.
    
    Ejemplos:
        GET /v1/calendars → http://calendar-service:8002/v1/calendars
        GET /v1/calendars/abc123 → http://calendar-service:8002/v1/calendars/abc123
    """
    full_path = f"v1/calendars/{path}" if path else "v1/calendars"
    return await proxy_request("calendars", full_path, request)

@app.api_route("/v1/events/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def events_route(path: str, request: Request):
    """
    Proxy para el Event Service.
    
    Ejemplos:
        GET /v1/events → http://event-service:8003/v1/events
        POST /v1/events → http://event-service:8003/v1/events
    """
    full_path = f"v1/events/{path}" if path else "v1/events"
    return await proxy_request("events", full_path, request)

@app.api_route("/v1/notifications/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def notifications_route(path: str, request: Request):
    """
    Proxy para el Notification Service.
    
    Ejemplos:
        GET /v1/notifications/user/google_123 → http://notification-service:8004/v1/notifications/user/google_123
    """
    full_path = f"v1/notifications/{path}" if path else "v1/notifications"
    return await proxy_request("notifications", full_path, request)

@app.api_route("/v1/integrations/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def integrations_route(path: str, request: Request):
    """
    Proxy para el Integration Service.
    
    Ejemplos:
        POST /v1/integrations/google/import → http://integration-service:8006/v1/integrations/google/import
    """
    full_path = f"v1/integrations/{path}" if path else "v1/integrations"
    return await proxy_request("integrations", full_path, request)

@app.api_route("/v1/auth/{path:path}", methods=["GET", "POST"])
async def auth_route(path: str, request: Request):
    """
    Proxy para el Auth Service.
    
    Ejemplos:
        GET /v1/auth/google → http://auth-service:8005/v1/auth/google
        GET /v1/auth/google/callback → http://auth-service:8005/v1/auth/google/callback
        POST /v1/auth/google/verify → http://auth-service:8005/v1/auth/google/verify
        POST /v1/auth/verify → http://auth-service:8005/v1/auth/verify
    """
    full_path = f"v1/auth/{path}" if path else "v1/auth"
    return await proxy_request("auth", full_path, request)

@app.api_route("/v2/events/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def events_v2_route(path: str, request: Request):
    """
    Proxy para el Event Service V2.
    """
    full_path = f"v2/events/{path}" if path else "v2/events"
    return await proxy_request("events", full_path, request)

@app.api_route("/v2/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def users_v2_route(path: str, request: Request):
    """
    Proxy para el User Service V2.
    
    Incluye endpoints como:
        GET /v2/users/{id} → Obtener usuario con preferencias V2
        GET /v2/users/by-external-id/{external_id} → Buscar por external_id
        PUT /v2/users/{id} → Actualizar usuario con frecuencia
        POST /v2/users/seed-dev-users → Crear usuarios de desarrollo
    """
    full_path = f"v2/users/{path}" if path else "v2/users"
    return await proxy_request("users", full_path, request)

@app.api_route("/v2/calendars/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def calendars_v2_route(path: str, request: Request):
    """
    Proxy para el Calendar Service V2.
    """
    full_path = f"v2/calendars/{path}" if path else "v2/calendars"
    return await proxy_request("calendars", full_path, request)

@app.api_route("/v2/integrations/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def integrations_v2_route(path: str, request: Request):
    """
    Proxy para el Integration Service V2.
    
    Ejemplos:
        POST /v2/integrations/google/import
        GET /v2/integrations/osm/geocode
        POST /v2/integrations/s3/upload-direct
    """
    full_path = f"v2/integrations/{path}" if path else "v2/integrations"
    
    # Manejar multipart específicamente para S3 si es necesario
    if "s3/" in full_path and request.method == "POST":
        return await proxy_request_multipart("integrations", full_path, request)
        
    return await proxy_request("integrations", full_path, request)


@app.api_route("/v3/integrations/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def integrations_v3_route(path: str, request: Request):
    """
    Proxy para el Integration Service V3 (Abstract Factory Pattern).
    
    Ejemplos:
        GET /v3/integrations/imports/providers
        POST /v3/integrations/imports/google
        POST /v3/integrations/imports/teamup
    """
    full_path = f"v3/integrations/{path}" if path else "v3/integrations"
    return await proxy_request("integrations", full_path, request)


@app.api_route("/v2/events/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])


async def proxy_request_multipart(service_name: str, path: str, request: Request):
    """
    Proxifica una petición multipart/form-data al servicio backend.
    
    Necesario para subir archivos ya que el proxy normal no maneja
    correctamente el content-type multipart.
    
    Args:
        service_name: Nombre del servicio destino
        path: Ruta dentro del servicio
        request: Petición original del cliente
        
    Returns:
        JSONResponse: Respuesta del servicio backend
    """
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Servicio {service_name} no encontrado")
    
    service_url = SERVICES[service_name]
    full_url = f"{service_url}/{path}"
    
    # Agregar query parameters si existen
    if request.url.query:
        full_url = f"{full_url}?{request.url.query}"
    
    try:
        # Filtrar headers problemáticos para el proxy
        headers = {}
        for key, value in request.headers.items():
            # Excluir headers que pueden causar problemas
            if key.lower() not in ['host', 'content-length']:
                headers[key] = value
        
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.request(
                method=request.method,
                url=full_url,
                headers=headers,
                content=await request.body()
            )
            
            # Intentar parsear como JSON, si falla devolver texto
            try:
                content = response.json() if response.text else {}
            except Exception:
                content = {"raw": response.text}
            
            return JSONResponse(
                status_code=response.status_code,
                content=content
            )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail=f"Timeout al conectar con {service_name}"
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=f"No se pudo conectar con {service_name}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))