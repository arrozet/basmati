"""
Middleware de autenticación para el API Gateway.

Valida tokens JWT en las peticiones y rechaza las no autenticadas
para rutas protegidas.
"""
import httpx
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from .config import settings


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware que valida tokens de autenticación en cada request.
    
    Las rutas públicas definidas en settings.public_routes no requieren
    autenticación. El resto de rutas necesitan un token Bearer válido.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Procesa cada request y valida la autenticación si es necesario.
        
        Args:
            request: La petición HTTP entrante
            call_next: Función para pasar al siguiente middleware/handler
        
        Returns:
            Response: La respuesta del handler o un error 401/403
        """
        path = request.url.path
        
        # Verificar si es una ruta pública
        if self._is_public_route(path):
            return await call_next(request)
        
        # Obtener token del header Authorization
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "unauthorized",
                    "message": "Token de autenticación requerido"
                }
            )
        
        # Extraer el token (formato: "Bearer <token>")
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Esquema de autenticación inválido")
        except ValueError:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "invalid_token_format",
                    "message": "Formato de token inválido. Use: Bearer <token>"
                }
            )
        
        # Validar token con el auth service
        is_valid, user_info = await self._validate_token(token)
        
        if not is_valid:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "invalid_token",
                    "message": "Token inválido o expirado"
                }
            )
        
        # Agregar información del usuario al request state
        request.state.user = user_info
        request.state.token = token
        
        # Continuar con la petición
        return await call_next(request)
    
    def _is_public_route(self, path: str) -> bool:
        """
        Verifica si una ruta es pública (no requiere autenticación).
        
        Args:
            path: Ruta de la petición
        
        Returns:
            bool: True si la ruta es pública
        """
        for public_route in settings.public_routes:
            if path.startswith(public_route) or path == public_route.rstrip("/"):
                return True
        return False
    
    async def _validate_token(self, token: str) -> tuple[bool, dict | None]:
        """
        Valida un token con el auth service.
        
        Args:
            token: Token JWT a validar
        
        Returns:
            tuple: (es_válido, info_usuario o None)
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{settings.auth_service_url}/v1/auth/verify",
                    json={"token": token}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("valid"):
                        return True, data.get("user")
                
                return False, None
                
        except httpx.RequestError:
            # Si el auth service no está disponible, rechazar por seguridad
            return False, None
