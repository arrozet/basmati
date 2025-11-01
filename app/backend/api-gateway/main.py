"""
API Gateway principal para Basmati.
Punto de entrada centralizado para todos los servicios de backend.
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
from core.config import SERVICES

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
        async with httpx.AsyncClient() as client:
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
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=f"No se pudo conectar con {service_name}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Rutas para cada servicio
@app.api_route("/v1/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def users_route(path: str, request: Request):
    """Proxifica peticiones al servicio de usuarios"""
    return await proxy_request("users", f"v1/{path}", request)

@app.api_route("/v1/calendars/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def calendars_route(path: str, request: Request):
    """Proxifica peticiones al servicio de calendarios"""
    return await proxy_request("calendars", f"v1/{path}", request)

@app.api_route("/v1/events/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def events_route(path: str, request: Request):
    """Proxifica peticiones al servicio de eventos"""
    return await proxy_request("events", f"v1/{path}", request)

@app.api_route("/v1/notifications/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def notifications_route(path: str, request: Request):
    """Proxifica peticiones al servicio de notificaciones"""
    return await proxy_request("notifications", f"v1/{path}", request)

@app.api_route("/v1/search/{path:path}", methods=["GET"])
async def search_route(path: str, request: Request):
    """Proxifica peticiones al servicio de búsqueda"""
    return await proxy_request("search", f"v1/{path}", request)

@app.api_route("/v1/integrations/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def integrations_route(path: str, request: Request):
    """Proxifica peticiones al servicio de integraciones"""
    return await proxy_request("integrations", f"v1/{path}", request)
