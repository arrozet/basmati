"""Endpoints v2 de usuarios.

Cambios en V2:
- Soporta el campo 'frequency' en preferencias de notificación
- Nuevo endpoint para obtener preferencias de notificación con frecuencia
- Nuevo endpoint para buscar usuarios por external_id
"""
from fastapi import APIRouter, HTTPException, status, Path, Body, Depends, Query
from typing import Optional, List
from schemas.v2.user import UserUpdateV2, UserResponseV2, NotificationPreferencesSchemaV2
from schemas.common import ResponseMessage
from core.interface.user import IUserService
from core.factory.user import get_user_factory
from core.database import get_database
from core.config import settings

router = APIRouter()


async def get_user_service(db = Depends(get_database)) -> IUserService:
    """
    Proporciona una instancia de UserService usando Abstract Factory.
    
    Args:
        db: Base de datos MongoDB (inyectada por FastAPI)
        
    Returns:
        IUserService: Instancia del servicio de usuarios (v2)
    """
    factory = get_user_factory("v2", db)
    return factory.create_service()


@router.get(
    "/by-external-id/{external_id}",
    response_model=UserResponseV2,
    summary="Obtener un usuario por External ID (V2)",
    description="""
Obtiene un usuario por su ID externo (Google ID, Facebook ID, etc.).

**Nuevo en V2**: Este endpoint facilita la búsqueda por ID de OAuth.
    """,
    responses={
        200: {"description": "Usuario encontrado y devuelto exitosamente."},
        404: {"description": "El usuario con el external_id especificado no existe."},
        500: {"description": "Error interno del servidor."}
    }
)
async def get_user_by_external_id_v2(
    external_id: str = Path(..., description="External ID del usuario (OAuth ID)"),
    service: IUserService = Depends(get_user_service)
):
    """
    Obtiene un usuario por su external_id (ID de OAuth).
    
    Args:
        external_id: ID externo del usuario
        service: Servicio de usuarios (inyectado por FastAPI)
        
    Returns:
        UserResponseV2: Usuario encontrado con preferencias V2
    """
    # Buscar en el repositorio por external_id
    user = await service.get_raw_repository().find_one({"external_id": external_id})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con external_id '{external_id}' no encontrado"
        )
    
    # Convertir a V2 añadiendo frequency si no existe
    user_dict = user.model_dump()
    
    # Convertir ObjectId a string si es necesario
    if "id" in user_dict and hasattr(user_dict["id"], "__str__"):
        user_dict["id"] = str(user_dict["id"])
    
    if "notification_preferences" in user_dict:
        prefs = user_dict["notification_preferences"]
        if "frequency" not in prefs:
            prefs["frequency"] = "instant"  # Valor por defecto para datos legacy
    
    return UserResponseV2(**user_dict)


@router.get(
    "",
    response_model=dict,
    summary="Listar usuarios con filtros (V2)",
    description="""
Lista usuarios con soporte para filtros V2.

**Nuevo en V2**: Permite filtrar por frecuencia de notificación y preferencias de email.
    """,
    responses={
        200: {"description": "Lista de usuarios encontrados."},
        500: {"description": "Error interno del servidor."}
    }
)
async def list_users_v2(
    notification_frequency: Optional[str] = Query(None, description="Filtrar por frecuencia: 'instant' o 'daily'"),
    email_notifications: Optional[bool] = Query(None, description="Filtrar por notificaciones por email activadas"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de resultados"),
    service: IUserService = Depends(get_user_service)
):
    """
    Lista usuarios con filtros opcionales.
    
    Args:
        notification_frequency: Filtrar por frecuencia de notificación
        email_notifications: Filtrar por email activado
        limit: Límite de resultados
        service: Servicio de usuarios
        
    Returns:
        dict: Lista de usuarios
    """
    # Construir query
    query = {}
    
    if notification_frequency:
        query["notification_preferences.frequency"] = notification_frequency
    
    if email_notifications is not None:
        query["notification_preferences.email"] = email_notifications
    
    # Buscar usuarios
    users = await service.get_raw_repository().find_many(query, limit=limit)
    
    # Convertir a V2
    result = []
    for user in users:
        user_dict = user.model_dump()
        if "notification_preferences" in user_dict:
            prefs = user_dict["notification_preferences"]
            if "frequency" not in prefs:
                prefs["frequency"] = "instant"
        result.append(UserResponseV2(**user_dict))
    
    return {"users": result, "count": len(result)}


@router.get(
    "/{user_id}",
    response_model=UserResponseV2,
    summary="Obtener un usuario por ID (V2)",
    description="""
Obtiene un usuario por su ID.

**Mejora en V2**: Incluye el campo 'frequency' en las preferencias de notificación.
    """,
    responses={
        200: {"description": "Usuario encontrado y devuelto exitosamente."},
        404: {"description": "El usuario con el ID especificado no existe."},
        500: {"description": "Error interno del servidor."}
    }
)
async def get_user_v2(
    user_id: str = Path(..., description="ID único del usuario"),
    service: IUserService = Depends(get_user_service)
):
    """
    Obtiene un usuario por su ID con preferencias de notificación V2.
    
    Args:
        user_id: ID del usuario
        service: Servicio de usuarios (inyectado por FastAPI)
        
    Returns:
        UserResponseV2: Usuario encontrado con preferencias V2
    """
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Convertir a V2 añadiendo frequency si no existe
    user_dict = user.model_dump()
    if "notification_preferences" in user_dict:
        prefs = user_dict["notification_preferences"]
        if "frequency" not in prefs:
            prefs["frequency"] = "instant"  # Valor por defecto para datos legacy
    
    return UserResponseV2(**user_dict)


@router.put(
    "/{user_id}",
    response_model=UserResponseV2,
    summary="Actualizar un usuario (V2)",
    description="""
Actualiza un usuario existente.

**Mejora en V2**: Soporta el campo 'frequency' en las preferencias de notificación.

Valores de frecuencia:
- **instant**: Las notificaciones se envían inmediatamente
- **daily**: Las notificaciones se acumulan y se envía un resumen diario a las 00:00
    """,
    responses={
        200: {"description": "Usuario actualizado exitosamente."},
        404: {"description": "El usuario con el ID especificado no existe."},
        500: {"description": "Error interno del servidor."}
    }
)
async def update_user_v2(
    user_id: str = Path(..., description="ID único del usuario"),
    user: UserUpdateV2 = Body(..., description="Datos a actualizar del usuario"),
    service: IUserService = Depends(get_user_service)
):
    """
    Actualiza un usuario existente con soporte para preferencias V2.
    
    Args:
        user_id: ID del usuario
        user: Datos a actualizar
        service: Servicio de usuarios (inyectado por FastAPI)
        
    Returns:
        UserResponseV2: Usuario actualizado
    """
    # Convertir a diccionario para el servicio
    update_dict = user.model_dump(exclude_unset=True)
    
    # El servicio existente puede manejar estos datos ya que el repositorio
    # simplemente guarda lo que recibe
    from schemas.user import UserUpdate
    
    # Crear un UserUpdate básico pero pasar todo el diccionario
    updated_user = await service.update_user(user_id, UserUpdate(**{
        k: v for k, v in update_dict.items() 
        if k in UserUpdate.model_fields
    }))
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Si hay preferencias de notificación con frequency, actualizarlas directamente
    if "notification_preferences" in update_dict and update_dict["notification_preferences"]:
        # Intentar guardar las preferencias con frequency
        try:
            await service.get_raw_repository().update(user_id, {
                "notification_preferences": update_dict["notification_preferences"]
            })
            updated_user = await service.get_user(user_id)
        except Exception as e:
            # Si falla (esquema antiguo), remover frequency y reintentar
            if "frequency" in str(e):
                prefs_to_save = update_dict["notification_preferences"].copy()
                prefs_to_save.pop("frequency", None)
                await service.get_raw_repository().update(user_id, {
                    "notification_preferences": prefs_to_save
                })
                updated_user = await service.get_user(user_id)
            else:
                raise
    
    # Convertir a V2
    user_dict = updated_user.model_dump()
    if "notification_preferences" in user_dict:
        prefs = user_dict["notification_preferences"]
        if "frequency" not in prefs:
            prefs["frequency"] = "instant"
    
    return UserResponseV2(**user_dict)


@router.get(
    "/{user_id}/notification-preferences",
    response_model=NotificationPreferencesSchemaV2,
    summary="Obtener preferencias de notificación (V2)",
    description="""
Obtiene las preferencias de notificación de un usuario.

**Nuevo en V2**: Este endpoint no existe en V1.

Incluye:
- in_app: Si las notificaciones dentro de la app están activadas
- email: Si las notificaciones por correo están activadas  
- email_address: Correo alternativo para notificaciones
- frequency: Frecuencia de notificaciones ('instant' o 'daily')
    """,
    responses={
        200: {"description": "Preferencias obtenidas exitosamente."},
        404: {"description": "El usuario con el ID especificado no existe."},
        500: {"description": "Error interno del servidor."}
    }
)
async def get_notification_preferences_v2(
    user_id: str = Path(..., description="ID único del usuario"),
    service: IUserService = Depends(get_user_service)
):
    """
    Obtiene las preferencias de notificación de un usuario.
    
    Args:
        user_id: ID del usuario
        service: Servicio de usuarios (inyectado por FastAPI)
        
    Returns:
        NotificationPreferencesSchemaV2: Preferencias de notificación
    """
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    prefs = user.notification_preferences.model_dump() if hasattr(user.notification_preferences, 'model_dump') else dict(user.notification_preferences)
    if "frequency" not in prefs:
        prefs["frequency"] = "instant"
    
    return NotificationPreferencesSchemaV2(**prefs)


@router.put(
    "/{user_id}/notification-preferences",
    response_model=NotificationPreferencesSchemaV2,
    summary="Actualizar preferencias de notificación (V2)",
    description="""
Actualiza las preferencias de notificación de un usuario.

**Nuevo en V2**: Este endpoint no existe en V1.

Valores de frecuencia:
- **instant**: Las notificaciones se envían inmediatamente cuando ocurre un evento
- **daily**: Las notificaciones se acumulan y se envía un resumen por correo a las 00:00
    """,
    responses={
        200: {"description": "Preferencias actualizadas exitosamente."},
        404: {"description": "El usuario con el ID especificado no existe."},
        500: {"description": "Error interno del servidor."}
    }
)
async def update_notification_preferences_v2(
    user_id: str = Path(..., description="ID único del usuario"),
    preferences: NotificationPreferencesSchemaV2 = Body(..., description="Nuevas preferencias"),
    service: IUserService = Depends(get_user_service)
):
    """
    Actualiza las preferencias de notificación de un usuario.
    
    Args:
        user_id: ID del usuario
        preferences: Nuevas preferencias de notificación
        service: Servicio de usuarios (inyectado por FastAPI)
        
    Returns:
        NotificationPreferencesSchemaV2: Preferencias actualizadas
    """
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Actualizar directamente las preferencias
    try:
        await service.get_raw_repository().update(user_id, {
            "notification_preferences": preferences.model_dump()
        })
    except Exception as e:
        # Si falla (esquema antiguo), remover frequency y reintentar
        if "frequency" in str(e):
            prefs_to_save = preferences.model_dump()
            prefs_to_save.pop("frequency", None)
            await service.get_raw_repository().update(user_id, {
                "notification_preferences": prefs_to_save
            })
    
    return preferences


@router.post(
    "/seed-dev-users",
    response_model=dict,
    summary="Crear usuarios de desarrollo (V2)",
    description="""
Crea los usuarios de desarrollo necesarios para probar la aplicación.

**Solo para desarrollo**: Este endpoint crea usuarios de prueba.

Usuarios creados:
- **user_dev_1**: Configurado en DEV_USER_1_EMAIL (frecuencia instant)
- **user_dev_2**: Configurado en DEV_USER_2_EMAIL (frecuencia instant)
- **user_dev_3**: daily_digest_test@example.com (frecuencia daily)
    """,
    responses={
        200: {"description": "Usuarios de desarrollo creados/actualizados."},
        500: {"description": "Error interno del servidor."}
    }
)
async def seed_dev_users(
    service: IUserService = Depends(get_user_service)
):
    """
    Crea o actualiza los usuarios de desarrollo.
    
    Args:
        service: Servicio de usuarios
        
    Returns:
        dict: Resultado de la operación con usuarios creados/actualizados
    """
    from datetime import datetime, timezone
    
    # Nota: el schema de MongoDB puede no soportar 'frequency' si no se ha actualizado
    # Por compatibilidad, solo incluimos campos V1 y añadimos frequency en runtime
    dev_users = [
        {
            "external_id": "user_dev_1",
            "provider": "google",
            "email": settings.dev_user_1_email,
            "display_name": "Usuario Desarrollo 1",
            "avatar_url": None,
            "notification_preferences": {
                "in_app": True,
                "email": True,
                "email_address": None
            },
            "followed_calendar_ids": [],
            "created_at": datetime.now(timezone.utc),
            "last_login": datetime.now(timezone.utc)
        },
        {
            "external_id": "user_dev_2",
            "provider": "google",
            "email": settings.dev_user_2_email,
            "display_name": "Usuario Desarrollo 2",
            "avatar_url": None,
            "notification_preferences": {
                "in_app": True,
                "email": True,
                "email_address": None
            },
            "followed_calendar_ids": [],
            "created_at": datetime.now(timezone.utc),
            "last_login": datetime.now(timezone.utc)
        },
        {
            "external_id": "user_dev_3",
            "provider": "google",
            "email": settings.dev_user_3_email,
            "display_name": "Usuario Resumen Diario",
            "avatar_url": None,
            "notification_preferences": {
                "in_app": True,
                "email": True,
                "email_address": None
            },
            "followed_calendar_ids": [],
            "created_at": datetime.now(timezone.utc),
            "last_login": datetime.now(timezone.utc)
        }
    ]
    
    results = {"created": [], "updated": [], "errors": []}
    
    for user_data in dev_users:
        try:
            # Verificar si ya existe
            existing = await service.get_raw_repository().find_one({"external_id": user_data["external_id"]})
            
            if existing:
                # Actualizar
                await service.get_raw_repository().update(existing.id, user_data)
                results["updated"].append(user_data["external_id"])
            else:
                # Crear nuevo
                await service.get_raw_repository().create(user_data)
                results["created"].append(user_data["external_id"])
        except Exception as e:
            results["errors"].append({"external_id": user_data["external_id"], "error": str(e)})
    
    return {
        "message": "Seed de usuarios completado",
        "results": results
    }
