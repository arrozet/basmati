"""Endpoints de Email V2 - Envío de correos electrónicos.

Nuevo en V2: Este módulo expone los endpoints para envío de correos
usando SendGrid. Los endpoints no existen en V1.
"""
from fastapi import APIRouter, HTTPException, status, Body
from schemas.email import (
    EmailRequest,
    EmailResponse,
    BulkEmailRequest,
    CommentNotificationRequest
)
from services.v2.email_service import EmailServiceV2

router = APIRouter()


def get_email_service() -> EmailServiceV2:
    """
    Crea una instancia del servicio de email V2.
    
    Returns:
        EmailServiceV2: Servicio de email configurado
    """
    return EmailServiceV2()


@router.post(
    "/send",
    response_model=EmailResponse,
    summary="Enviar correo electrónico",
    description="""
Envía un correo electrónico usando SendGrid.

**Nuevo en V2**: Este endpoint no existe en V1.

El correo se envía desde la cuenta amcgil@uma.es.
Si no hay API key de SendGrid configurada, simula el envío para desarrollo.
    """,
    responses={
        200: {"description": "Correo enviado exitosamente."},
        500: {"description": "Error al enviar el correo."}
    }
)
async def send_email(
    email_request: EmailRequest = Body(..., description="Datos del correo a enviar")
):
    """
    Envía un correo electrónico usando SendGrid.
    
    Args:
        email_request: Datos del correo (destinatario, asunto, contenido)
        
    Returns:
        EmailResponse: Resultado del envío
    """
    try:
        service = get_email_service()
        response = await service.send_email(email_request)
        
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.message
            )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar correo: {str(e)}"
        )


@router.post(
    "/send-digest",
    response_model=EmailResponse,
    summary="Enviar resumen diario de notificaciones",
    description="""
Envía un correo con el resumen diario de notificaciones.

**Nuevo en V2**: Este endpoint no existe en V1.

Formatea las notificaciones en un correo HTML con estilo Basmati.
    """,
    responses={
        200: {"description": "Resumen enviado exitosamente."},
        500: {"description": "Error al enviar el resumen."}
    }
)
async def send_daily_digest(
    request: BulkEmailRequest = Body(..., description="Datos del resumen diario")
):
    """
    Envía un correo con el resumen diario de notificaciones.
    
    Args:
        request: Datos del resumen (destinatario, lista de notificaciones)
        
    Returns:
        EmailResponse: Resultado del envío
    """
    try:
        service = get_email_service()
        response = await service.send_daily_digest(request)
        
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.message
            )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar resumen diario: {str(e)}"
        )


@router.post(
    "/send-comment-notification",
    response_model=EmailResponse,
    summary="Enviar notificación de nuevo comentario",
    description="""
Envía un correo notificando sobre un nuevo comentario en un calendario.

**Nuevo en V2**: Este endpoint no existe en V1.

Formatea el correo con estilo Basmati para notificaciones de comentarios.
    """,
    responses={
        200: {"description": "Notificación enviada exitosamente."},
        500: {"description": "Error al enviar la notificación."}
    }
)
async def send_comment_notification(
    request: CommentNotificationRequest = Body(
        ..., 
        description="Datos de la notificación de comentario"
    )
):
    """
    Envía un correo notificando sobre un nuevo comentario.
    
    Args:
        request: Datos de la notificación (destinatario, evento, comentario)
        
    Returns:
        EmailResponse: Resultado del envío
    """
    try:
        service = get_email_service()
        response = await service.send_comment_notification(request)
        
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.message
            )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar notificación de comentario: {str(e)}"
        )

