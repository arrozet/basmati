"""
Cliente OAuth de Google para autenticación.
"""
import httpx
from google.oauth2 import id_token
from google.auth.transport import requests
from pydantic import BaseModel
from .config import settings


class GoogleUserInfo(BaseModel):
    """Información del usuario obtenida de Google."""
    id: str  # Google user ID
    email: str
    name: str
    picture: str | None = None
    verified_email: bool = True


# URL para la página de autorización de Google
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# Scopes de Google OAuth
# - openid, email, profile: básicos para autenticación
# - calendar.readonly: para importar calendarios de Google Calendar
# GOOGLE_SCOPES = "openid email profile"
GOOGLE_SCOPES = "openid email profile https://www.googleapis.com/auth/calendar.readonly"



def get_google_auth_url(state: str | None = None) -> str:
    """
    Genera la URL de autorización de Google OAuth.
    
    Args:
        state: Token CSRF opcional para validar la respuesta
    
    Returns:
        URL completa para redirigir al usuario a Google
    """
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": GOOGLE_SCOPES,
        "access_type": "offline",
        "prompt": "consent"
    }
    
    if state:
        params["state"] = state
    
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GOOGLE_AUTH_URL}?{query}"


async def exchange_code_for_tokens(code: str) -> dict:
    """
    Intercambia el código de autorización por tokens de acceso.
    
    Args:
        code: Código de autorización recibido de Google
    
    Returns:
        dict con access_token, refresh_token, id_token, etc.
    
    Raises:
        httpx.HTTPStatusError: Si Google rechaza el código
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.google_redirect_uri
            }
        )
        response.raise_for_status()
        return response.json()


async def get_google_user_info(access_token: str) -> GoogleUserInfo:
    """
    Obtiene la información del usuario de Google usando el access token.
    
    Args:
        access_token: Token de acceso de Google
    
    Returns:
        GoogleUserInfo con los datos del usuario
    
    Raises:
        httpx.HTTPStatusError: Si el token es inválido
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        data = response.json()
        
        return GoogleUserInfo(
            id=data["id"],
            email=data["email"],
            name=data.get("name", data["email"]),
            picture=data.get("picture"),
            verified_email=data.get("verified_email", True)
        )


def verify_google_id_token(token: str) -> GoogleUserInfo | None:
    """
    Verifica un ID token de Google (útil para login desde frontend).
    
    Este método se usa cuando el frontend hace el flujo OAuth y envía
    directamente el ID token para verificación.
    
    Args:
        token: ID token de Google
    
    Returns:
        GoogleUserInfo si el token es válido, None si no
    """
    try:
        # Verificar el ID token con Google
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.google_client_id
        )
        
        # Verificar que sea un token de Google
        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            return None
        
        return GoogleUserInfo(
            id=idinfo["sub"],
            email=idinfo["email"],
            name=idinfo.get("name", idinfo["email"]),
            picture=idinfo.get("picture"),
            verified_email=idinfo.get("email_verified", True)
        )
    except ValueError:
        # Token inválido
        return None
