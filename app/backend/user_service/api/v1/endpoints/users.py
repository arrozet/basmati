"""Endpoints de usuarios"""
from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List
from schemas.user import UserCreate, UserUpdate, UserResponse
from schemas.common import ResponseMessage
from services.user_service import UserService
from core.database import get_user_repository

router = APIRouter()

# Dependency: Inyección de dependencias para UserService y UserDAO
# 
# ¿Por qué usamos Depends()?
# - Permite que FastAPI maneje automáticamente la creación y destrucción de recursos
# - Cada request obtiene su propia instancia de UserDAO y UserService (aislamiento de datos)
# - Facilita testing: podemos mockear la dependencia fácilmente
# - Evita repetir código: no escribimos db = get_database() en cada endpoint
# - Proporciona ciclo de vida claro: FastAPI controla cuándo se crea y destruye
#
# ¿Qué es Depends()?
# - Es una función de FastAPI que implementa el patrón de "Dependency Injection" (inyección de dependencias)
# - Tells FastAPI: "necesito que ejecutes esta función y me pases su resultado como parámetro"
# - En este caso: ejecuta get_database(), pasa la BD a get_user_dao(),
#   y el resultado se inyecta como 'user_dao' en los endpoints
#
# Flujo de una request:
# 1. Request llega -> FastAPI ve "user_dao: UserDAO = Depends(get_user_dao)"
# 2. Ejecuta get_user_dao() que necesita get_database()
# 3. Ejecuta get_database() primero (dependencia anidada)
# 4. Pasa el resultado a get_user_dao()
# 5. Inyecta el resultado final en el endpoint
# 6. Al terminar la request, limpia los recursos

async def get_user_service(user_repository = Depends(get_user_repository)) -> UserService:
    """
    Proporciona una instancia de UserService con el Repository.
    
    Args:
        user_repository: Repository de usuarios (inyectado por FastAPI)
        
    Returns:
        UserService: Instancia del servicio de usuarios
    """
    return UserService(user_repository)

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo usuario",
    description="""
Crea un nuevo usuario en el sistema mediante **autenticación OAuth**.

**Campos requeridos:**
- **external_id**: ID único del proveedor OAuth
- **provider**: Proveedor OAuth ("google" o "facebook")
- **email**: Correo electrónico
- **display_name**: Nombre visible del usuario

**Validación automática:**
- Verifica que no exista usuario con el mismo `external_id` + `provider`
- Asigna automáticamente `created_at` y `last_login`
- Inicializa array vacío de `followed_calendar_ids`

**Ejemplo:**
```json
{
  "external_id": "123456789",
  "provider": "google",
  "email": "juan@example.com",
  "display_name": "Juan Pérez"
}
```
"""
)
async def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    """
    Crea un nuevo usuario en el sistema mediante **autenticación OAuth**.

    **Validación automática:**
    - Verifica que no exista un usuario con el mismo `external_id` + `provider`
    - Asigna automáticamente `created_at` y `last_login`
    - Inicializa array vacío de `followed_calendar_ids`

    Args:
        user: Datos del usuario a crear (incluye **external_id** y **provider**)
        service: Servicio de usuarios (inyectado por FastAPI)

    Returns:
        UserResponse: El usuario creado con su **ID de MongoDB**

    Raises:
        HTTPException 400: Si ya existe un usuario con esas credenciales OAuth
    """
    try:
        return await service.create_user(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obtener un usuario por ID",
    description="""
Obtiene un usuario específico por su **ID de MongoDB**.

**Información devuelta:**
- **Perfil**: email, display_name, avatar_url
- **OAuth**: external_id, provider
- **Preferencias**: notification_preferences
- **Actividad**: followed_calendar_ids, created_at, last_login
"""
)
async def get_user(user_id: str, service: UserService = Depends(get_user_service)):
    """
    Obtiene un usuario por su **ID de MongoDB**.

    **Información devuelta:**
    - **Perfil**: email, display_name, avatar_url
    - **OAuth**: external_id, provider
    - **Preferencias**: notification_preferences
    - **Actividad**: followed_calendar_ids, created_at, last_login

    Args:
        user_id: ID del usuario (MongoDB ObjectId como string)
        service: Servicio de usuarios (inyectado por FastAPI)

    Returns:
        UserResponse: Usuario encontrado con toda su información

    Raises:
        HTTPException 404: Si el usuario no existe
    """
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user

@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar un usuario",
    description="""
Actualiza un usuario existente (**actualización parcial**).

**Campos actualizables:**
- **email**, **display_name**, **avatar_url**
- **notification_preferences**
- **followed_calendar_ids**

**Nota:** Los campos `external_id` y `provider` (credenciales OAuth) **NO** se pueden modificar.
"""
)
async def update_user(user_id: str, user: UserUpdate, service: UserService = Depends(get_user_service)):
    """
    Actualiza un usuario existente (**actualización parcial**).

    **Campos actualizables:**
    - **email**, **display_name**, **avatar_url**: Información del perfil
    - **notification_preferences**: Preferencias de notificaciones
    - **followed_calendar_ids**: Calendarios que sigue

    **Nota:** Los campos `external_id` y `provider` (credenciales OAuth) **NO** se pueden modificar.

    Args:
        user_id: ID del usuario
        user: Datos a actualizar (solo los campos que cambiarán)
        service: Servicio de usuarios (inyectado por FastAPI)

    Returns:
        UserResponse: Usuario actualizado con los cambios aplicados

    Raises:
        HTTPException 400: Si hay error de validación
        HTTPException 404: Si el usuario no existe
    """
    updated_user = await service.update_user(user_id, user)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return updated_user

@router.delete(
    "/{user_id}",
    response_model=ResponseMessage,
    summary="Eliminar un usuario",
    description="""
Elimina un usuario del sistema de forma **permanente**.

**⚠️ Advertencia:**
- La eliminación es **irreversible**
- Los calendarios creados por el usuario **NO** se eliminan
- Los comentarios del usuario permanecen (quedan huérfanos)
- Se recomienda implementar "soft delete" en producción
"""
)
async def delete_user(user_id: str, service: UserService = Depends(get_user_service)):
    """
    Elimina un usuario del sistema de forma **permanente**.

    **⚠️ Advertencia:**
    - La eliminación es **irreversible**
    - Los calendarios creados por el usuario **NO** se eliminan
    - Los comentarios del usuario permanecen (quedan huérfanos)
    - Se recomienda implementar "soft delete" en producción

    Args:
        user_id: ID del usuario a eliminar
        service: Servicio de usuarios (inyectado por FastAPI)

    Returns:
        ResponseMessage: Mensaje de confirmación de eliminación

    Raises:
        HTTPException 404: Si el usuario no existe
    """
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return ResponseMessage(message="Usuario eliminado exitosamente")

@router.get(
    "/search/by-email",
    response_model=UserResponse,
    summary="Buscar usuario por email",
    description="""
Busca un usuario por su **email** (coincidencia exacta).

**Caso de uso:** Login, verificación de existencia, recuperación de cuenta.
"""
)
async def search_by_email(email: str = Query(..., description="Email del usuario"), service: UserService = Depends(get_user_service)):
    """
    Busca un usuario por su **email** (coincidencia exacta).

    **Caso de uso:** Login, verificación de existencia, recuperación de cuenta.

    Args:
        email: Email del usuario (búsqueda exacta, case-sensitive)
        service: Servicio de usuarios (inyectado por FastAPI)

    Returns:
        UserResponse: Usuario con ese email

    Raises:
        HTTPException 404: Si no existe usuario con ese email
    """
    user = await service.search_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user

@router.get(
    "/search/by-display-name",
    response_model=List[UserResponse],
    summary="Buscar usuarios por nombre",
    description="""
Busca usuarios por **nombre visible** (coincidencia parcial, case-insensitive).

Utiliza regex: `"Juan"` encuentra `"Juan Pérez"`, `"María Juan"`, etc.

**Caso de uso:** Autocompletar, búsqueda de usuarios, menciones.
"""
)
async def search_by_display_name(display_name: str = Query(..., description="Nombre o parte del nombre"), service: UserService = Depends(get_user_service)):
    """
    Busca usuarios por **nombre visible** (coincidencia parcial, case-insensitive).

    Utiliza regex para búsqueda parcial: `"Juan"` encuentra `"Juan Pérez"`, `"María Juan"`, etc.

    **Caso de uso:** Autocompletar, búsqueda de usuarios, menciones.

    Args:
        display_name: Nombre o parte del nombre del usuario
        service: Servicio de usuarios (inyectado por FastAPI)

    Returns:
        List[UserResponse]: Lista de usuarios que coinciden (puede estar vacía)
    """
    users = await service.search_by_display_name(display_name)
    return users

@router.get(
    "/search/by-oauth",
    response_model=UserResponse,
    summary="Buscar usuario por credenciales OAuth",
    description="""
Busca un usuario por sus **credenciales OAuth** (external_id + provider).

**Combinación única:** `external_id` + `provider` identifica de forma única al usuario.

**Caso de uso:** Login OAuth, vinculación de cuentas.
"""
)
async def search_by_oauth(
    external_id: str = Query(..., description="ID del proveedor OAuth"),
    provider: str = Query(..., description="Proveedor OAuth (google/facebook)"),
    service: UserService = Depends(get_user_service)
):
    """
    Busca un usuario por sus **credenciales OAuth** (external_id + provider).

    **Combinación única:** La combinación `external_id` + `provider` identifica de forma única al usuario.

    **Caso de uso:** Login OAuth, vinculación de cuentas.

    Args:
        external_id: ID único del proveedor OAuth (ej: "123456789")
        provider: Proveedor OAuth ("google" o "facebook")
        service: Servicio de usuarios (inyectado por FastAPI)

    Returns:
        UserResponse: Usuario con esas credenciales OAuth

    Raises:
        HTTPException 404: Si no existe usuario con esas credenciales
    """
    user = await service.search_by_oauth(external_id, provider)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user
