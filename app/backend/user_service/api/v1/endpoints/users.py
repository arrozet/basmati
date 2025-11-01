"""Endpoints de usuarios"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from schemas.user import UserCreate, UserUpdate, UserResponse
from schemas.common import ResponseMessage
from services.user_service import UserService
from core.database import get_database

router = APIRouter()

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Crea un nuevo usuario en el sistema.
    
    Args:
        user: Datos del usuario a crear
        
    Returns:
        UserResponse: El usuario creado con su ID
        
    Example:
        ```json
        {
            "email": "usuario@ejemplo.com",
            "name": "Juan Pérez",
            "notification_preferences": {
                "email_enabled": true,
                "in_app_enabled": true
            }
        }
        ```
        
    Response:
        ```json
        {
            "id": "507f191e810c19729de860ea",
            "email": "usuario@ejemplo.com",
            "name": "Juan Pérez",
            "notification_preferences": {
                "email_enabled": true,
                "in_app_enabled": true
            },
            "created_at": "2025-01-15T10:30:00Z",
            "updated_at": "2025-01-15T10:30:00Z"
        }
        ```
    """
    db = get_database()
    service = UserService(db)
    
    # Verificar si el email ya existe
    existing = await service.search_by_email(user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    return await service.create_user(user)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """
    Obtiene un usuario por su ID.
    
    Args:
        user_id: ID del usuario
        
    Returns:
        UserResponse: Usuario encontrado
    """
    db = get_database()
    service = UserService(db)
    
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: UserUpdate):
    """
    Actualiza un usuario existente.
    
    Args:
        user_id: ID del usuario
        user: Datos a actualizar
        
    Returns:
        UserResponse: Usuario actualizado
    """
    db = get_database()
    service = UserService(db)
    
    updated_user = await service.update_user(user_id, user)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return updated_user

@router.delete("/{user_id}", response_model=ResponseMessage)
async def delete_user(user_id: str):
    """
    Elimina un usuario del sistema.
    
    Args:
        user_id: ID del usuario
        
    Returns:
        ResponseMessage: Mensaje de confirmación
    """
    db = get_database()
    service = UserService(db)
    
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return ResponseMessage(message="Usuario eliminado exitosamente")

@router.get("/search/by-email", response_model=UserResponse)
async def search_by_email(email: str = Query(..., description="Email del usuario")):
    """
    Busca un usuario por email (parametrized query 1).
    
    Args:
        email: Email del usuario
        
    Returns:
        UserResponse: Usuario encontrado
    """
    db = get_database()
    service = UserService(db)
    
    user = await service.search_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user

@router.get("/search/by-name", response_model=List[UserResponse])
async def search_by_name(name: str = Query(..., description="Nombre o parte del nombre")):
    """
    Busca usuarios por nombre parcial (parametrized query 2).
    
    Args:
        name: Nombre o parte del nombre
        
    Returns:
        List[UserResponse]: Lista de usuarios encontrados
    """
    db = get_database()
    service = UserService(db)
    
    users = await service.search_by_name(name)
    return users
