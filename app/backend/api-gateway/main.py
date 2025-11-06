"""
API Gateway principal para Basmati.
Punto de entrada centralizado para todos los servicios de backend.
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
from core.config import SERVICES
from core.openapi_aggregator import aggregate_openapi_specs

app = FastAPI(
    title="Basmati API Gateway",
    description="Punto de entrada centralizado para todos los servicios de Basmati",
    version="1.0.0"
)

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
    Endpoint personalizado para servir la especificación OpenAPI combinada.

    Returns:
        dict: Especificación OpenAPI agregada de todos los servicios
    """
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

# Ruta dinámica genérica para todos los servicios
@app.api_route("/v1/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def dynamic_service_route(service_name: str, path: str, request: Request):
    """
    Proxy dinámico para todos los servicios backend.

    Esta ruta captura todas las peticiones con el formato /v1/{service}/{path}
    y las enruta automáticamente al servicio correspondiente.

    Args:
        service_name: Nombre del servicio (users, calendars, events, etc.)
        path: Ruta dentro del servicio
        request: Petición HTTP original

    Returns:
        JSONResponse: Respuesta del servicio backend

    Raises:
        HTTPException 404: Si el servicio no existe
        HTTPException 503: Si no se puede conectar con el servicio
        HTTPException 504: Si el servicio tarda demasiado en responder
    """
    return await proxy_request(service_name, f"v1/{path}", request)
