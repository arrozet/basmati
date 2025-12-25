"""
Utilidades JWT para generar y validar tokens de sesión.
"""
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt, JWTError
from pydantic import BaseModel
from .config import settings


class TokenPayload(BaseModel):
    """Payload del token JWT."""
    sub: str  # external_id del usuario
    email: str
    display_name: str
    provider: str  # "google"
    exp: datetime
    iat: datetime


class TokenData(BaseModel):
    """Datos extraídos de un token validado."""
    external_id: str
    email: str
    display_name: str
    provider: str


def create_access_token(
    external_id: str,
    email: str,
    display_name: str,
    provider: str = "google",
    expires_delta: timedelta | None = None
) -> str:
    """
    Crea un token JWT de sesión para el usuario.
    
    Args:
        external_id: ID único del usuario (Google ID)
        email: Email del usuario
        display_name: Nombre visible del usuario
        provider: Proveedor OAuth ("google")
        expires_delta: Tiempo hasta expiración (opcional)
    
    Returns:
        str: Token JWT codificado
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    
    payload = {
        "sub": external_id,
        "email": email,
        "display_name": display_name,
        "provider": provider,
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> TokenData | None:
    """
    Verifica y decodifica un token JWT.
    
    Args:
        token: Token JWT a verificar
    
    Returns:
        TokenData con la información del usuario si el token es válido,
        None si el token es inválido o ha expirado
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        return TokenData(
            external_id=payload["sub"],
            email=payload["email"],
            display_name=payload["display_name"],
            provider=payload["provider"]
        )
    except JWTError:
        return None


def decode_token_unverified(token: str) -> dict[str, Any] | None:
    """
    Decodifica un token sin verificar la firma (útil para debugging).
    
    Args:
        token: Token JWT a decodificar
    
    Returns:
        dict con el payload o None si no se puede decodificar
    """
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"verify_signature": False}
        )
    except JWTError:
        return None
