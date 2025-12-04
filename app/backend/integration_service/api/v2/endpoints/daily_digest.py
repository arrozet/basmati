"""Endpoints de Daily Digest V2 - Resumen diario de notificaciones.

Este módulo expone los endpoints para el servicio de resumen diario.
Los endpoints permiten enviar digests masivos o individuales.
"""
from fastapi import APIRouter, HTTPException, status
from schemas.daily_digest import (
    DigestRequest,
    BulkDigestResponse,
    DigestSendResponse,
    DigestPreviewResponse
)
from services.v2.daily_digest_service import DailyDigestServiceV2

router = APIRouter()


def get_daily_digest_service() -> DailyDigestServiceV2:
    """
    Crea una instancia del servicio de daily digest V2.
    
    Returns:
        DailyDigestServiceV2: Servicio de daily digest configurado
    """
    return DailyDigestServiceV2()


@router.post(
    "/send-all",
    response_model=BulkDigestResponse,
    summary="Enviar resumen diario a todos los usuarios",
    description="""
Envía el resumen diario a todos los usuarios con frecuencia 'daily'.

Este endpoint debe ser llamado por un cron job a las 00:00.
Recopila las notificaciones de las últimas 24 horas y las envía
agrupadas por calendario.
    """,
    responses={
        200: {"description": "Envío masivo completado."},
        500: {"description": "Error interno del servidor."}
    }
)
async def send_all_daily_digests():
    """
    Envía el resumen diario a todos los usuarios con frecuencia 'daily'.
    
    Returns:
        BulkDigestResponse: Resultado del envío masivo
    """
    try:
        service = get_daily_digest_service()
        return await service.send_all_daily_digests()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en envío masivo de digests: {str(e)}"
        )


@router.post(
    "/send-user",
    response_model=DigestSendResponse,
    summary="Enviar resumen diario a un usuario específico",
    description="""
Envía el resumen diario a un usuario específico.

Útil para pruebas o envíos manuales. Incluye las notificaciones
de las últimas 24 horas.
    """,
    responses={
        200: {"description": "Digest enviado exitosamente."},
        400: {"description": "Usuario sin email configurado."},
        404: {"description": "Usuario no encontrado."},
        500: {"description": "Error al enviar el digest."}
    }
)
async def send_user_digest(request: DigestRequest):
    """
    Envía el resumen diario a un usuario específico.
    
    Args:
        request: Datos de la solicitud con el ID del usuario
        
    Returns:
        DigestSendResponse: Resultado del envío
    """
    try:
        service = get_daily_digest_service()
        return await service.send_user_digest(request.user_external_id)
    except ValueError as e:
        error_message = str(e)
        if "no encontrado" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message
            )
        elif "sin email" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_message
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enviando digest: {str(e)}"
        )


@router.get(
    "/preview/{user_external_id}",
    response_model=DigestPreviewResponse,
    summary="Vista previa del resumen diario",
    description="""
Genera una vista previa del digest sin enviarlo.

Útil para desarrollo y pruebas. Si no hay notificaciones
reales, muestra datos de ejemplo.
    """,
    responses={
        200: {"description": "Vista previa generada."},
        500: {"description": "Error generando vista previa."}
    }
)
async def preview_digest(user_external_id: str):
    """
    Genera una vista previa del digest sin enviarlo.
    
    Args:
        user_external_id: ID externo del usuario
        
    Returns:
        DigestPreviewResponse: Vista previa del digest
    """
    try:
        service = get_daily_digest_service()
        return await service.preview_digest(user_external_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando vista previa: {str(e)}"
        )
