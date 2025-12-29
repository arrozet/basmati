"""
Rutas de autenticación OAuth.

Implementa el flujo OAuth con Google usando códigos de autorización temporales:
1. GET /auth/google → Redirige a Google para autenticación
2. GET /auth/google/callback → Recibe código de Google, genera auth_code temporal y redirige al frontend
3. GET /auth/token?code=XXX → Valida el código temporal y devuelve el token JWT
4. POST /auth/logout → Endpoint informativo (el logout real es en el frontend)

Los códigos temporales se almacenan en memoria y son de un solo uso con expiración de 60 segundos.
"""
import uuid
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
import httpx

from core.config import settings
from core.google_oauth import (
    get_google_auth_url,
    exchange_code_for_tokens,
    get_google_user_info,
    verify_google_id_token,
    GoogleUserInfo
)
from core.jwt_handler import create_access_token, verify_token
from schemas import (
    GoogleLoginRequest,
    TokenResponse,
    UserInfo,
    VerifyTokenRequest,
    VerifyTokenResponse,
    AuthUrlResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# =============================================================================
# ALMACÉN DE CÓDIGOS DE AUTORIZACIÓN TEMPORALES (EN MEMORIA)
# =============================================================================

# Diccionario para almacenar códigos de autorización temporales
# Key: código UUID
# Value: {"user_data": dict, "access_token": str, "google_access_token": str, "expires_at": datetime, "used": bool, "is_new_user": bool}
_authorization_codes: dict[str, dict] = {}

# Tiempo de expiración de los códigos (60 segundos)
AUTH_CODE_EXPIRATION_SECONDS = 60


def _generate_auth_code(
    user_data: dict,
    access_token: str,
    is_new_user: bool,
    google_access_token: str | None = None
) -> str:
    """
    Genera un código de autorización temporal y lo almacena en memoria.
    
    Args:
        user_data: Datos del usuario (external_id, email, display_name, etc.)
        access_token: Token JWT generado para el usuario
        is_new_user: Si es un usuario nuevo
        google_access_token: Token de acceso de Google (para importar calendarios)
    
    Returns:
        str: Código UUID único
    """
    # Limpiar códigos expirados antes de generar uno nuevo
    _cleanup_expired_codes()
    
    auth_code = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=AUTH_CODE_EXPIRATION_SECONDS)
    
    _authorization_codes[auth_code] = {
        "user_data": user_data,
        "access_token": access_token,
        "google_access_token": google_access_token,
        "expires_at": expires_at,
        "used": False,
        "is_new_user": is_new_user
    }
    
    return auth_code


def _validate_and_consume_auth_code(auth_code: str) -> dict | None:
    """
    Valida un código de autorización y lo marca como usado.
    
    Args:
        auth_code: Código a validar
    
    Returns:
        dict con los datos si es válido, None si no existe, expiró o ya fue usado
    """
    if auth_code not in _authorization_codes:
        return None
    
    code_data = _authorization_codes[auth_code]
    
    # Verificar si ya fue usado
    if code_data["used"]:
        return None
    
    # Verificar si expiró
    if datetime.now(timezone.utc) > code_data["expires_at"]:
        # Eliminar código expirado
        del _authorization_codes[auth_code]
        return None
    
    # Marcar como usado (un solo uso)
    code_data["used"] = True
    
    return code_data


def _cleanup_expired_codes() -> None:
    """
    Elimina códigos expirados del diccionario.
    Se llama automáticamente al generar nuevos códigos.
    """
    now = datetime.now(timezone.utc)
    expired_codes = [
        code for code, data in _authorization_codes.items()
        if now > data["expires_at"]
    ]
    for code in expired_codes:
        del _authorization_codes[code]


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
        # Intentar obtener usuario existente por external_id
        try:
            response = await client.get(
                f"{settings.user_service_url}/v2/users/by-external-id/{external_id}"
            )
            
            if response.status_code == 200:
                # Usuario existe, verificar si necesita actualización
                user_data = response.json()
                user_id = user_data.get("_id") or user_data.get("id")
                
                # Verificar si cambió la información de Google
                needs_update = (
                    user_data.get("email") != google_user.email or
                    user_data.get("display_name") != google_user.name or
                    user_data.get("avatar_url") != google_user.picture
                )
                
                if needs_update:
                    # Actualizar solo si cambió algo
                    update_data = {
                        "email": google_user.email,
                        "display_name": google_user.name,
                        "avatar_url": google_user.picture
                    }
                    
                    update_response = await client.put(
                        f"{settings.user_service_url}/v1/users/{user_id}",
                        json=update_data
                    )
                    
                    if update_response.status_code == 200:
                        return update_response.json(), False
                    else:
                        # Si falla la actualización, devolver usuario sin actualizar
                        return user_data, False
                else:
                    # No hay cambios, devolver usuario tal cual
                    return user_data, False
                
        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail="No se pudo conectar con el servicio de usuarios"
            )
        
        # Usuario no existe (404), crear uno nuevo
        if response.status_code == 404:
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
                
                create_response = await client.post(
                    f"{settings.user_service_url}/v1/users",
                    json=new_user
                )
                
                if create_response.status_code in (200, 201):
                    return create_response.json(), True
                elif create_response.status_code == 400 or create_response.status_code == 409:
                    # Usuario ya existe (race condition), intentar obtenerlo de nuevo
                    get_response = await client.get(
                        f"{settings.user_service_url}/v2/users/by-external-id/{external_id}"
                    )
                    if get_response.status_code == 200:
                        return get_response.json(), False
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Error al obtener usuario después de conflicto: {get_response.text}"
                        )
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error al crear usuario: {create_response.text}"
                    )
                    
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=503,
                    detail=f"No se pudo crear el usuario: {str(e)}"
                )
        else:
            # Otro error del user service
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error del servicio de usuarios: {response.text}"
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
    description="Endpoint al que Google redirige después de la autorización. Genera un código temporal para obtener el token."
)
async def google_callback(
    code: str = Query(..., description="Código de autorización de Google"),
    state: str = Query(default="/dashboard", description="URL de redirección original")
):
    """
    Procesa el callback de Google OAuth.
    
    Este endpoint es llamado por Google después de que el usuario autoriza.
    Intercambia el código por tokens, obtiene info del usuario, genera un
    código de autorización temporal, y redirige al frontend.
    
    El frontend recibe un auth_code temporal (no el token JWT directamente).
    Para obtener el token, el frontend debe llamar a GET /auth/token?code=XXX
    
    Args:
        code: Código de autorización de Google
        state: URL del frontend para redirigir
    
    Returns:
        Redirect al frontend con auth_code en la URL
    """
    try:
        # Intercambiar código por tokens
        tokens = await exchange_code_for_tokens(code)
        google_access_token = tokens.get("access_token")
        
        if not google_access_token:
            raise HTTPException(status_code=400, detail="No se recibió access token")
        
        # Obtener información del usuario
        google_user = await get_google_user_info(google_access_token)
        
        # Obtener o crear usuario en nuestra base de datos
        user_data, is_new = await get_or_create_user(google_user)
        
        # Crear token JWT de sesión
        session_token = create_access_token(
            external_id=user_data["external_id"],
            email=user_data["email"],
            display_name=user_data["display_name"],
            provider="google"
        )
        
        # Generar código de autorización temporal (expira en 60 segundos, un solo uso)
        # Incluimos el google_access_token para que el frontend pueda usarlo en importaciones
        auth_code = _generate_auth_code(
            user_data=user_data,
            access_token=session_token,
            is_new_user=is_new,
            google_access_token=google_access_token
        )
        
        # Construir URL de redirección con el código temporal
        redirect_url = f"{settings.frontend_url}/auth/callback?auth_code={auth_code}"
        if state and state != "/dashboard":
            redirect_url += f"&redirect_to={state}"
        redirect_url += f"&new_user={str(is_new).lower()}"
        
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
    
    # Crear token de sesión (settings ya está importado al inicio del archivo)
    session_token = create_access_token(
        external_id=user_data["external_id"],
        email=user_data["email"],
        display_name=user_data["display_name"],
        provider="google"
    )
    
    return TokenResponse(
        access_token=session_token,
        token_type="bearer",
        expires_in=settings.jwt_expire_minutes * 60,
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


@router.get(
    "/token",
    response_model=TokenResponse,
    summary="Obtener token del usuario identificado",
    description="""
    Devuelve el token JWT del usuario autenticado para usar en la API.
    
    Este endpoint recibe el código de autorización temporal generado
    en el callback de Google y devuelve el token JWT.
    
    Flujo típico:
    1. Usuario hace login: GET /auth/google → redirige a Google
    2. Google callback: GET /auth/google/callback → genera auth_code y redirige al frontend
    3. Usuario obtiene token: GET /auth/token?code=XXX → devuelve token JWT
    4. Usuario usa la API: Authorization: Bearer <token>
    
    IMPORTANTE: El código es de un solo uso y expira en 60 segundos.
    """
)
async def get_token(
    code: str = Query(..., description="Código de autorización temporal recibido del callback")
):
    """
    Obtiene el token JWT del usuario que se ha identificado.
    
    Valida el código de autorización temporal recibido del callback de OAuth
    y devuelve el token JWT en formato JSON para que el cliente pueda usarlo
    en las peticiones posteriores a la API.
    
    Args:
        code: Código de autorización temporal (UUID)
    
    Returns:
        TokenResponse con el token y datos del usuario
    
    Raises:
        HTTPException 401: Si el código es inválido, expirado o ya fue usado
    """
    # Validar y consumir el código (un solo uso)
    code_data = _validate_and_consume_auth_code(code)
    
    if not code_data:
        raise HTTPException(
            status_code=401,
            detail="Código inválido, expirado o ya utilizado. Inicie sesión nuevamente con GET /auth/google."
        )
    
    user_data = code_data["user_data"]
    
    # Devolver el token con información del usuario
    return TokenResponse(
        access_token=code_data["access_token"],
        token_type="bearer",
        expires_in=settings.jwt_expire_minutes * 60,
        is_new_user=code_data["is_new_user"],
        google_access_token=code_data.get("google_access_token"),
        user=UserInfo(
            external_id=user_data["external_id"],
            email=user_data["email"],
            display_name=user_data["display_name"],
            avatar_url=user_data.get("avatar_url"),
            provider=user_data.get("provider", "google")
        )
    )


@router.post(
    "/logout",
    summary="Cerrar sesión",
    description="Endpoint informativo de logout. El logout real se realiza en el frontend eliminando el token."
)
async def logout():
    """
    Endpoint de logout.
    
    Con tokens JWT sin estado, el logout real se maneja en el frontend
    borrando el token almacenado. Este endpoint existe por completitud
    de la API.
    
    Returns:
        Mensaje de confirmación
    """
    return {"message": "Sesión cerrada correctamente. Elimine el token del cliente."}
