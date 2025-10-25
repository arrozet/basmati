"""
Users endpoints : api/v1/users/

Endpoints para gestionar usuarios (CRUD completo).
Estructura de usuario: { name, email, pwd }
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import get_database
from schemas.user import UserCreate, UserUpdate, UserResponse, UserList
from schemas.common import MessageResponse, ErrorResponse
from services.user_service import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={
        404: {"model": ErrorResponse, "description": "Usuario no encontrado"},
        400: {"model": ErrorResponse, "description": "Error de validación"},
    }
)


def get_user_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> UserService:
    """Dependency para obtener el servicio de usuarios"""
    return UserService(db)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un nuevo usuario en el sistema",
    response_description="Usuario creado exitosamente"
)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Crear un nuevo usuario
    
    - **name**: Nombre del usuario
    - **email**: Email único del usuario
    - **pwd**: Contraseña del usuario
    """
    try:
        user = await user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=UserList,
    summary="Listar usuarios",
    description="Obtiene lista de usuarios con paginación",
    response_description="Lista de usuarios"
)
async def list_users(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    user_service: UserService = Depends(get_user_service)
):
    """
    Listar usuarios con paginación
    
    - **page**: Número de página (inicia en 1)
    - **page_size**: Cantidad de usuarios por página (1-100)
    """
    skip = (page - 1) * page_size
    users, total = await user_service.get_users(
        skip=skip,
        limit=page_size
    )
    
    return {
        "users": users,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obtener usuario",
    description="Obtiene un usuario específico por su ID",
    response_description="Usuario encontrado"
)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Obtener usuario por ID
    
    - **user_id**: ID único del usuario (ejemplo: 68fa377af47c0bcded1182e2)
    """
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario",
    description="Actualiza los datos de un usuario",
    response_description="Usuario actualizado"
)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Actualizar usuario
    
    - **user_id**: ID del usuario a actualizar
    - **name**: Nuevo nombre (opcional)
    - **email**: Nuevo email (opcional)
    - **pwd**: Nueva contraseña (opcional)
    """
    try:
        user = await user_service.update_user(user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="Eliminar usuario",
    description="Elimina un usuario del sistema",
    response_description="Usuario eliminado"
)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Eliminar usuario
    
    - **user_id**: ID del usuario a eliminar
    """
    deleted = await user_service.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return {"message": "Usuario eliminado exitosamente"}


@router.get(
    "/email/{email}",
    response_model=UserResponse,
    summary="Buscar por email",
    description="Busca un usuario por su email",
    response_description="Usuario encontrado"
)
async def get_user_by_email(
    email: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Buscar usuario por email
    
    - **email**: Email del usuario (ejemplo: davidmunvalle@uma.es)
    """
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user
