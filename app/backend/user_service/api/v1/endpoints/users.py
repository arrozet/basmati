"""Endpoints de usuarios"""
from fastapi import APIRouter, HTTPException, status, Query, Path, Body, Depends
from typing import List
from schemas.user import UserCreate, UserUpdate, UserResponse
from schemas.common import ResponseMessage
from core.interface.user import IUserService
from core.factory.user import get_user_factory
from core.database import get_database

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

async def get_user_service(db = Depends(get_database)) -> IUserService:
    """
    Proporciona una instancia de UserService usando Abstract Factory.
    
    Args:
        db: Base de datos MongoDB (inyectada por FastAPI)
        
    Returns:
        IUserService: Instancia del servicio de usuarios (v1)
    """
    factory = get_user_factory("v1", db)
    return factory.create_service()

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo usuario",
    description="Crea un nuevo usuario en el sistema con OAuth.",
    responses={
        201: {"description": "Usuario creado exitosamente."},
        400: {"description": "Error de validación o ya existe un usuario con esas credenciales OAuth."},
        500: {"description": "Error interno del servidor."}
    }
)
async def create_user(
    user: UserCreate = Body(..., description="Datos del usuario a crear (incluye external_id y provider)"),
    service: IUserService = Depends(get_user_service)
):
    """
    Crea un nuevo usuario en el sistema con OAuth.
    
    Args:
        user: Datos del usuario a crear (incluye external_id y provider)
        service: Servicio de usuarios (inyectado por FastAPI)
        
    Returns:
        UserResponse: El usuario creado con su ID
        
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
    description="Obtiene un usuario por su ID.",
    responses={
        200: {"description": "Usuario encontrado y devuelto exitosamente."},
        404: {"description": "El usuario con el ID especificado no existe."},
        500: {"description": "Error interno del servidor."}
    }
)
async def get_user(
    user_id: str = Path(..., description="ID único del usuario"),
    service: IUserService = Depends(get_user_service)
):
    """
    Obtiene un usuario por su ID.
    
    Args:
        user_id: ID del usuario
        service: Servicio de usuarios (inyectado por FastAPI)
        
    Returns:
        UserResponse: Usuario encontrado
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
    description="Actualiza un usuario existente.",
    responses={
        200: {"description": "Usuario actualizado exitosamente."},
        404: {"description": "El usuario con el ID especificado no existe."},
        500: {"description": "Error interno del servidor."}
    }
)
async def update_user(
    user_id: str = Path(..., description="ID único del usuario"),
    user: UserUpdate = Body(..., description="Datos a actualizar del usuario"),
    service: IUserService = Depends(get_user_service)
):
    """
    Actualiza un usuario existente.
    
    Args:
        user_id: ID del usuario
        user: Datos a actualizar
        service: Servicio de usuarios (inyectado por FastAPI)
        
    Returns:
        UserResponse: Usuario actualizado
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
    description="Elimina un usuario del sistema.",
    responses={
        200: {"description": "Usuario eliminado exitosamente."},
        404: {"description": "El usuario con el ID especificado no existe."},
        500: {"description": "Error interno del servidor."}
    }
)
async def delete_user(
    user_id: str = Path(..., description="ID único del usuario"),
    service: IUserService = Depends(get_user_service)
):
    """
    Elimina un usuario del sistema.
    
    Args:
        user_id: ID del usuario
        service: Servicio de usuarios (inyectado por FastAPI)
        
    Returns:
        ResponseMessage: Mensaje de confirmación
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
    description="Busca un usuario por email (parametrized query 1).",
    responses={
        200: {"description": "Usuario encontrado y devuelto exitosamente."},
        404: {"description": "No se encontró un usuario con ese email."},
        500: {"description": "Error interno del servidor."}
    }
)
async def search_by_email(
    email: str = Query(..., description="Email del usuario"),
    service: IUserService = Depends(get_user_service)
):
    """
    Busca un usuario por email (parametrized query 1).
    
    Args:
        email: Email del usuario
        service: Servicio de usuarios (inyectado por FastAPI)
        
    Returns:
        UserResponse: Usuario encontrado
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
    description="Busca usuarios por display_name parcial (parametrized query 2).",
    responses={
        200: {"description": "Lista de usuarios encontrados."},
        500: {"description": "Error interno del servidor."}
    }
)
async def search_by_display_name(
    display_name: str = Query(..., description="Nombre o parte del nombre"),
    service: IUserService = Depends(get_user_service)
):
    """
    Busca usuarios por display_name parcial (parametrized query 2).
    
    Args:
        display_name: Nombre o parte del nombre
        service: Servicio de usuarios (inyectado por FastAPI)
        
    Returns:
        List[UserResponse]: Lista de usuarios encontrados
    """
    users = await service.search_by_display_name(display_name)
    return users

@router.get(
    "/search/by-oauth",
    response_model=UserResponse,
    summary="Buscar usuario por credenciales OAuth",
    description="Busca un usuario por sus credenciales OAuth.",
    responses={
        200: {"description": "Usuario encontrado y devuelto exitosamente."},
        404: {"description": "No se encontró un usuario con esas credenciales OAuth."},
        500: {"description": "Error interno del servidor."}
    }
)
async def search_by_oauth(
    external_id: str = Query(..., description="ID del proveedor OAuth"),
    provider: str = Query(..., description="Proveedor OAuth (google/facebook)"),
    service: IUserService = Depends(get_user_service)
):
    """
    Busca un usuario por sus credenciales OAuth.
    
    Args:
        external_id: ID del proveedor OAuth
        provider: Proveedor OAuth ("google" o "facebook")
        service: Servicio de usuarios (inyectado por FastAPI)
        
    Returns:
        UserResponse: Usuario encontrado
    """
    user = await service.search_by_oauth(external_id, provider)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user
