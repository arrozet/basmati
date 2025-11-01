"""Endpoints de usuarios"""
from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List
from schemas.user import UserCreate, UserUpdate, UserResponse
from schemas.common import ResponseMessage
from services.user_service import UserService
from core.database import get_database

router = APIRouter()

# Dependency: Inyección de dependencias para UserService
# 
# ¿Por qué usamos Depends()?
# - Permite que FastAPI maneje automáticamente la creación y destrucción de recursos
# - Cada request obtiene su propia instancia de UserService (aislamiento de datos)
# - Facilita testing: podemos mockear la dependencia fácilmente
# - Evita repetir código: no escribimos db = get_database() en cada endpoint
# - Proporciona ciclo de vida claro: FastAPI controla cuándo se crea y destruye
#
# ¿Qué es Depends()?
# - Es una función de FastAPI que implementa el patrón de "Dependency Injection" (inyección de dependencias)
# - Tells FastAPI: "necesito que ejecutes esta función y me pases su resultado como parámetro"
# - En este caso: ejecuta get_database(), pasa la BD a get_user_service(), 
#   y el resultado se inyecta como 'service' en los endpoints
#
# Flujo de una request:
# 1. Request llega -> FastAPI ve "service: UserService = Depends(get_user_service)"
# 2. Ejecuta get_user_service() que necesita get_database()
# 3. Ejecuta get_database() primero (dependencia anidada)
# 4. Pasa el resultado a get_user_service()
# 5. Inyecta el resultado final en el endpoint
# 6. Al terminar la request, limpia los recursos

async def get_user_service(db = Depends(get_database)) -> UserService:
    """
    Proporciona una instancia de UserService con la conexión a BD.
    
    Args:
        db: Conexión a la base de datos (inyectada por FastAPI)
        
    Returns:
        UserService: Instancia del servicio de usuarios
    """
    return UserService(db)

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    """
    Crea un nuevo usuario en el sistema con OAuth.
    
    Args:
        user: Datos del usuario a crear (incluye external_id y provider)
        service: Servicio de usuarios (inyectado por FastAPI)
        
    Returns:
        UserResponse: El usuario creado con su ID
    """
    # Verificar si el external_id ya existe para ese provider
    existing = await service.search_by_oauth(user.external_id, user.provider)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya está registrado con este proveedor OAuth"
        )
    
    return await service.create_user(user)

# ⚠️ IMPORTANTE: Las rutas con /search/ deben ir ANTES que /{user_id}
# Porque FastAPI evalúa las rutas en orden y "google_123456789" coincidiría con /{user_id}
# antes de llegar a /search/by-oauth

@router.get("/search/by-email", response_model=UserResponse)
async def search_by_email(email: str = Query(..., description="Email del usuario"), service: UserService = Depends(get_user_service)):
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

@router.get("/search/by-display-name", response_model=List[UserResponse])
async def search_by_display_name(display_name: str = Query(..., description="Nombre o parte del nombre"), service: UserService = Depends(get_user_service)):
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

@router.get("/search/by-oauth", response_model=UserResponse)
async def search_by_oauth(
    external_id: str = Query(..., description="ID del proveedor OAuth"),
    provider: str = Query(..., description="Proveedor OAuth (google/facebook)"),
    service: UserService = Depends(get_user_service)
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

# RUTAS CRUD POR ID (van DESPUÉS de /search/ para evitar conflictos)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, service: UserService = Depends(get_user_service)):
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

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: UserUpdate, service: UserService = Depends(get_user_service)):
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

@router.delete("/{user_id}", response_model=ResponseMessage)
async def delete_user(user_id: str, service: UserService = Depends(get_user_service)):
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
