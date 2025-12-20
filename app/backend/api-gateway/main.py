"""
API Gateway principal para Basmati.
Punto de entrada centralizado para todos los servicios de backend.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from core.config import SERVICES
from core.openapi_aggregator import aggregate_openapi_specs

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
    lifespan=lifespan
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes en desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    """
    Sobrescribe la generación de OpenAPI para usar nuestro schema agregado.

    Esto hace que la documentación de FastAPI (/docs) muestre todos los
    endpoints de los servicios backend con sus request bodies y schemas.
    """
    global _custom_openapi_schema

    if _custom_openapi_schema is not None:
        return _custom_openapi_schema

    # Fallback al schema por defecto si aún no se ha cargado
    return app.openapi_schema or {}

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
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=full_url,
                headers=dict(request.headers),
                content=await request.body()
            )
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
        
        async with httpx.AsyncClient(timeout=60.0) as client:
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