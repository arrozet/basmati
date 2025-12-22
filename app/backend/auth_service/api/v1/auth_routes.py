"""
Rutas de autenticación OAuth.
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
import httpx

from ..core.config import settings
from ..core.google_oauth import (
    get_google_auth_url,
    exchange_code_for_tokens,
    get_google_user_info,
    verify_google_id_token,
    GoogleUserInfo
)
from ..core.jwt_handler import create_access_token, verify_token
from ..schemas import (
    GoogleLoginRequest,
    TokenResponse,
    UserInfo,
    VerifyTokenRequest,
    VerifyTokenResponse,
    AuthUrlResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


async def get_or_create_user(google_user: GoogleUserInfo) -> tuple[dict, bool]:
    """
    Obtiene o crea un usuario en el user_service basado en la info de Google.
    
    Args:
        google_user: Información del usuario de Google
    
    Returns:
        tuple: (datos del usuario, es_nuevo)
    """
    external_id = f"google_{google_user.id}"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Intentar obtener usuario existente
        try:
            response = await client.get(
                f"{settings.user_service_url}/v1/users/{external_id}"
            )
            
            if response.status_code == 200:
                # Usuario existe, actualizar last_login
                user_data = response.json()
                return user_data, False
                
        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail="No se pudo conectar con el servicio de usuarios"
            )
        
        # Usuario no existe, crear uno nuevo
        try:
            new_user = {
                "external_id": external_id,
                "provider": "google",
                "email": google_user.email,
                "display_name": google_user.name,
                "avatar_url": google_user.picture,
                "notification_preferences": {
                    "in_app": True,
                    "email": True,
                    "email_address": None,
                    "frequency": "instant"
                }
            }
            
            response = await client.post(
                f"{settings.user_service_url}/v1/users",
                json=new_user
            )
            
            if response.status_code in (200, 201):
                return response.json(), True
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error al crear usuario: {response.text}"
                )
                
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"No se pudo crear el usuario: {str(e)}"
            )


@router.get(
    "/google",
    response_model=AuthUrlResponse,
    summary="Obtener URL de login de Google",
    description="Retorna la URL para iniciar el flujo OAuth con Google"
)
async def get_google_login_url(
    redirect_to: str = Query(default="/dashboard", description="URL a la que redirigir después del login")
):
    """
    Genera la URL de autorización de Google para iniciar el flujo OAuth.
    
    El frontend puede redirigir al usuario a esta URL o usarla en un popup.
    
    Args:
        redirect_to: URL del frontend para redirigir después del login
    
    Returns:
        AuthUrlResponse con la URL de Google
    """
    # Usar redirect_to como state para saber a dónde redirigir después
    auth_url = get_google_auth_url(state=redirect_to)
    return AuthUrlResponse(auth_url=auth_url)


@router.get(
    "/google/callback",
    summary="Callback de Google OAuth",
    description="Endpoint al que Google redirige después de la autorización"
)
async def google_callback(
    code: str = Query(..., description="Código de autorización de Google"),
    state: str = Query(default="/dashboard", description="URL de redirección original")
):
    """
    Procesa el callback de Google OAuth.
    
    Este endpoint es llamado por Google después de que el usuario autoriza.
    Intercambia el código por tokens, obtiene info del usuario, y redirige
    al frontend con el token de sesión.
    
    Args:
        code: Código de autorización de Google
        state: URL del frontend para redirigir
    
    Returns:
        Redirect al frontend con el token en la URL
    """
    try:
        # Intercambiar código por tokens
        tokens = await exchange_code_for_tokens(code)
        access_token = tokens.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="No se recibió access token")
        
        # Obtener información del usuario
        google_user = await get_google_user_info(access_token)
        
        # Obtener o crear usuario en nuestra base de datos
        user_data, is_new = await get_or_create_user(google_user)
        
        # Crear token JWT de sesión
        session_token = create_access_token(
            external_id=user_data["external_id"],
            email=user_data["email"],
            display_name=user_data["display_name"],
            provider="google"
        )
        
        # Redirigir al frontend con el token
        redirect_url = f"{settings.frontend_url}/auth/callback?token={session_token}&new_user={str(is_new).lower()}"
        if state and state != "/dashboard":
            redirect_url += f"&redirect_to={state}"
        
        return RedirectResponse(url=redirect_url)
        
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error al obtener tokens de Google: {e.response.text}"
        )


@router.post(
    "/google/verify",
    response_model=TokenResponse,
    summary="Verificar ID token de Google",
    description="Verifica un ID token de Google y retorna un token de sesión"
)
async def verify_google_token(request: GoogleLoginRequest):
    """
    Verifica un ID token de Google y genera un token de sesión.
    
    Este endpoint se usa cuando el frontend maneja el flujo OAuth
    (por ejemplo, usando Google Sign-In SDK) y envía directamente
    el ID token para verificación.
    
    Args:
        request: ID token de Google
    
    Returns:
        TokenResponse con el token de sesión y datos del usuario
    """
    # Verificar el ID token con Google
    google_user = verify_google_id_token(request.id_token)
    
    if not google_user:
        raise HTTPException(
            status_code=401,
            detail="ID token de Google inválido o expirado"
        )
    
    # Obtener o crear usuario
    user_data, is_new = await get_or_create_user(google_user)
    
    # Crear token de sesión
    from ..core.config import settings as auth_settings
    session_token = create_access_token(
        external_id=user_data["external_id"],
        email=user_data["email"],
        display_name=user_data["display_name"],
        provider="google"
    )
    
    return TokenResponse(
        access_token=session_token,
        token_type="bearer",
        expires_in=auth_settings.jwt_expire_minutes * 60,
        is_new_user=is_new,
        user=UserInfo(
            external_id=user_data["external_id"],
            email=user_data["email"],
            display_name=user_data["display_name"],
            avatar_url=user_data.get("avatar_url"),
            provider="google"
        )
    )


@router.post(
    "/verify",
    response_model=VerifyTokenResponse,
    summary="Verificar token de sesión",
    description="Verifica si un token JWT de sesión es válido"
)
async def verify_session_token(request: VerifyTokenRequest):
    """
    Verifica un token JWT de sesión.
    
    Este endpoint es usado por el API Gateway para validar tokens
    en cada request autenticada.
    
    Args:
        request: Token a verificar
    
    Returns:
        VerifyTokenResponse indicando si es válido y datos del usuario
    """
    token_data = verify_token(request.token)
    
    if not token_data:
        return VerifyTokenResponse(
            valid=False,
            user=None,
            error="Token inválido o expirado"
        )
    
    return VerifyTokenResponse(
        valid=True,
        user=UserInfo(
            external_id=token_data.external_id,
            email=token_data.email,
            display_name=token_data.display_name,
            avatar_url=None,  # No se guarda en el token
            provider=token_data.provider
        ),
        error=None
    )


@router.get(
    "/me",
    response_model=UserInfo,
    summary="Obtener usuario actual",
    description="Retorna los datos del usuario basado en el token de autorización"
)
async def get_current_user(
    authorization: str = Query(None, description="Bearer token (alternativa al header)")
):
    """
    Obtiene la información del usuario actual basado en su token.
    
    Nota: En producción, el token vendrá del header Authorization.
    Este endpoint es para testing con el token como query param.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Token requerido")
    
    # Remover "Bearer " si viene así
    token = authorization.replace("Bearer ", "").replace("bearer ", "")
    
    token_data = verify_token(token)
    
    if not token_data:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    return UserInfo(
        external_id=token_data.external_id,
        email=token_data.email,
        display_name=token_data.display_name,
        avatar_url=None,
        provider=token_data.provider
    )


@router.post(
    "/logout",
    summary="Cerrar sesión",
    description="Invalida el token actual (actualmente solo para uso del frontend)"
)
async def logout():
    """
    Endpoint de logout.
    
    Con tokens JWT sin estado, el logout real se maneja en el frontend
    borrando el token. Este endpoint existe por completitud de la API.
    
    En el futuro se podría implementar una blacklist de tokens.
    """
    return {"message": "Sesión cerrada correctamente"}
