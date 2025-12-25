"""
Endpoints de imágenes AWS S3 (V2).

CRUD completo para gestión de imágenes almacenadas en S3.
Incluye compresión automática para optimizar almacenamiento.
"""
import base64
from fastapi import APIRouter, HTTPException, status, Query, Body, File, UploadFile
from schemas.s3 import (
    ImageUploadDirectRequest,
    ImageUploadRequest,
    ImageUploadResponse,
    ImageMetadata,
    ImageListResponse,
    ImageDeleteResponse,
    ImageDownloadResponse,
    BulkDeleteRequest,
    BulkDeleteResponse
)
from services.v2.s3_service import S3ImageService
from core.config import settings

router = APIRouter()


def get_s3_service() -> S3ImageService:
    """
    Crea una instancia del servicio de S3 con la configuración del entorno.
    
    Returns:
        S3ImageService: Instancia configurada del servicio
        
    Raises:
        HTTPException: Si la configuración de AWS no está disponible
    """
    # Validar que las credenciales de AWS estén configuradas
    if not settings.aws_access_key_id or not settings.aws_secret_access_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de almacenamiento S3 no configurado. Faltan credenciales de AWS."
        )
    
    if not settings.aws_s3_bucket_name:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bucket de S3 no configurado."
        )
    
    return S3ImageService(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        aws_region=settings.aws_region,
        bucket_name=settings.aws_s3_bucket_name
    )


# ==================== CREATE ====================

@router.post(
    "/upload-direct",
    response_model=ImageMetadata,
    status_code=status.HTTP_201_CREATED,
    summary="Subir imagen directamente (con compresión)",
    description="""
Sube una imagen directamente al backend con compresión automática.

**Ventajas de este método:**
- ✅ Compresión automática de imágenes (ahorra espacio y ancho de banda)
- ✅ Redimensiona imágenes grandes automáticamente
- ✅ Optimiza JPEG/PNG para web
- ✅ Convierte formatos pesados a más eficientes

**Optimizaciones aplicadas:**
- Redimensiona a máximo 1920x1080 (mantiene aspect ratio)
- Comprime JPEG con calidad 85%
- Optimiza PNG
- Convierte GIF/BMP a JPEG si no tienen transparencia

**Formatos soportados:**
- image/jpeg, image/png, image/gif, image/webp, image/svg+xml, image/bmp

**Uso recomendado:**
- Para imágenes subidas por usuarios (avatares, fotos de eventos, etc.)
- Cuando el cliente no puede comprimir la imagen
- Cuando se quiere garantizar tamaño optimizado
""",
    responses={
        201: {"description": "Imagen subida y comprimida exitosamente."},
        400: {"description": "Archivo inválido o tipo no permitido."},
        413: {"description": "Archivo demasiado grande (máx 10MB)."},
        503: {"description": "Servicio S3 no disponible."}
    }
)
async def upload_image_direct(
    file: UploadFile = File(..., description="Archivo de imagen a subir"),
    folder: str | None = Query(None, description="Carpeta en S3 (ej: 'events', 'avatars')"),
    compress: bool = Query(True, description="Si True, comprime la imagen automáticamente")
):
    """
    Sube una imagen directamente con compresión automática.
    
    El backend recibe la imagen, la comprime y la sube a S3.
    Esto optimiza el almacenamiento y reduce costos.
    
    Args:
        file: Archivo de imagen (multipart/form-data)
        folder: Carpeta opcional en S3
        compress: Activar compresión automática
        
    Returns:
        ImageMetadata: Metadatos de la imagen subida
    """
    try:
        # Validar que sea un archivo de imagen
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El archivo debe ser una imagen. Tipo recibido: {file.content_type}"
            )
        
        # Leer contenido del archivo
        image_data = await file.read()
        
        # Validar tamaño máximo (10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(image_data) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Archivo demasiado grande. Máximo: 10MB, recibido: {len(image_data)/1024/1024:.1f}MB"
            )
        
        service = get_s3_service()
        
        # Subir con compresión
        metadata = await service.upload_image_direct(
            image_data=image_data,
            filename=file.filename or "imagen.jpg",
            content_type=file.content_type,
            folder=folder,
            compress=compress
        )
        
        return metadata
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        error_message = str(e)
        # Mejorar mensajes de error para problemas de AWS
        if "Credenciales de AWS" in error_message or "NoCredentialsError" in error_message:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio S3 no disponible: Credenciales de AWS no configuradas correctamente"
            )
        elif "Error al subir imagen a S3" in error_message:
            # Error específico de S3 (permisos, bucket, etc.)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=error_message  # Ya incluye el mensaje descriptivo del servicio
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al subir imagen: {error_message}"
            )


@router.post(
    "/upload",
    response_model=ImageUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener URL para subir imagen",
    description="""
Genera una URL presigned para subir una imagen directamente a AWS S3.

**Flujo de uso:**
1. Llamar a este endpoint con el nombre y tipo de archivo
2. Usar la `upload_url` devuelta para hacer PUT con el archivo
3. Una vez subido, la imagen estará disponible en `public_url`

**Tipos de imagen soportados:**
- image/jpeg, image/png, image/gif, image/webp, image/svg+xml, image/bmp

**Carpetas disponibles:**
- `events`: Imágenes de eventos
- `avatars`: Fotos de perfil de usuarios
- `calendars`: Imágenes de calendarios
- `attachments`: Archivos adjuntos generales
""",
    responses={
        200: {"description": "URL de subida generada exitosamente."},
        400: {"description": "Tipo de contenido no válido o datos incorrectos."},
        503: {"description": "Servicio S3 no disponible o mal configurado."}
    }
)
async def generate_upload_url(
    request: ImageUploadRequest = Body(..., description="Datos del archivo a subir")
):
    """
    Genera una URL presigned para subir una imagen a S3.
    
    El cliente debe usar esta URL para hacer un PUT request
    directamente a S3 con el contenido del archivo.
    
    Args:
        request: Datos de la imagen (filename, content_type, folder)
        
    Returns:
        ImageUploadResponse: URL de subida, key y URL pública
    """
    try:
        service = get_s3_service()
        return await service.generate_upload_url(request)
    except ValueError as e:
        # Error de validación (tipo de contenido no permitido)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar URL de subida: {str(e)}"
        )


# ==================== READ ====================

@router.get(
    "/images",
    response_model=ImageListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar imágenes",
    description="""
Lista las imágenes almacenadas en S3.

**Filtros disponibles:**
- `prefix`: Filtrar por carpeta (ej: 'events', 'avatars')
- `max_results`: Limitar número de resultados (máx 1000)
""",
    responses={
        200: {"description": "Lista de imágenes obtenida exitosamente."},
        503: {"description": "Servicio S3 no disponible."}
    }
)
async def list_images(
    prefix: str | None = Query(
        None, 
        description="Prefijo/carpeta para filtrar (ej: 'events', 'avatars')"
    ),
    max_results: int = Query(
        100, 
        ge=1, 
        le=1000, 
        description="Número máximo de resultados"
    )
):
    """
    Lista las imágenes almacenadas en S3.
    
    Args:
        prefix: Prefijo/carpeta para filtrar (opcional)
        max_results: Número máximo de resultados
        
    Returns:
        ImageListResponse: Lista de imágenes con metadatos
    """
    try:
        service = get_s3_service()
        return await service.list_images(prefix=prefix, max_results=max_results)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar imágenes: {str(e)}"
        )


@router.get(
    "/images/{image_key:path}",
    response_model=ImageMetadata,
    status_code=status.HTTP_200_OK,
    summary="Obtener metadatos de imagen",
    description="Obtiene los metadatos de una imagen específica en S3.",
    responses={
        200: {"description": "Metadatos obtenidos exitosamente."},
        404: {"description": "Imagen no encontrada."},
        503: {"description": "Servicio S3 no disponible."}
    }
)
async def get_image_metadata(
    image_key: str
):
    """
    Obtiene los metadatos de una imagen en S3.
    
    Args:
        image_key: Key de la imagen en S3 (puede incluir carpeta, ej: 'events/abc123.jpg')
        
    Returns:
        ImageMetadata: Metadatos de la imagen
    """
    try:
        service = get_s3_service()
        metadata = await service.get_image_metadata(image_key)
        
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Imagen no encontrada: {image_key}"
            )
        
        return metadata
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener metadatos: {str(e)}"
        )


@router.get(
    "/download/{image_key:path}",
    response_model=ImageDownloadResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener URL de descarga",
    description="""
Genera una URL presigned temporal para descargar una imagen.

Útil para imágenes que requieren acceso autenticado o cuando
se necesita una URL temporal con expiración.
""",
    responses={
        200: {"description": "URL de descarga generada exitosamente."},
        404: {"description": "Imagen no encontrada."},
        503: {"description": "Servicio S3 no disponible."}
    }
)
async def get_download_url(
    image_key: str,
    expiration: int = Query(
        3600, 
        ge=60, 
        le=43200, 
        description="Tiempo de expiración en segundos (1 min - 12 horas)"
    )
):
    """
    Genera una URL presigned para descargar una imagen.
    
    Args:
        image_key: Key de la imagen en S3
        expiration: Tiempo de expiración de la URL en segundos
        
    Returns:
        ImageDownloadResponse: URL temporal de descarga
    """
    try:
        service = get_s3_service()
        return await service.generate_download_url(image_key, expiration)
    except Exception as e:
        if "no encontrada" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar URL de descarga: {str(e)}"
        )


# ==================== DELETE ====================

@router.delete(
    "/images/{image_key:path}",
    response_model=ImageDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar imagen",
    description="Elimina una imagen del bucket de S3.",
    responses={
        200: {"description": "Imagen eliminada exitosamente o no existía."},
        503: {"description": "Servicio S3 no disponible."}
    }
)
async def delete_image(
    image_key: str
):
    """
    Elimina una imagen del bucket de S3.
    
    Args:
        image_key: Key de la imagen a eliminar (puede incluir carpeta)
        
    Returns:
        ImageDeleteResponse: Resultado de la eliminación
    """
    try:
        service = get_s3_service()
        return await service.delete_image(image_key)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar imagen: {str(e)}"
        )


@router.post(
    "/images/bulk-delete",
    response_model=BulkDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar múltiples imágenes",
    description="""
Elimina múltiples imágenes del bucket de S3 en una sola operación.

Más eficiente que eliminar una por una cuando hay muchas imágenes que borrar.
Máximo 1000 imágenes por llamada.
""",
    responses={
        200: {"description": "Eliminación masiva completada (puede incluir errores parciales)."},
        400: {"description": "Lista de keys vacía o inválida."},
        503: {"description": "Servicio S3 no disponible."}
    }
)
async def delete_images_bulk(
    request: BulkDeleteRequest = Body(..., description="Lista de keys de imágenes a eliminar")
):
    """
    Elimina múltiples imágenes del bucket de S3.
    
    Args:
        request: Lista de keys de imágenes a eliminar
        
    Returns:
        BulkDeleteResponse: Resultado con contador y errores
    """
    try:
        # Validar que no se supere el límite de S3
        if len(request.keys) > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Máximo 1000 imágenes por llamada de eliminación masiva"
            )
        
        service = get_s3_service()
        return await service.delete_images_bulk(request.keys)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en eliminación masiva: {str(e)}"
        )


# ==================== UTILIDADES ====================

@router.get(
    "/images/{image_key:path}/exists",
    status_code=status.HTTP_200_OK,
    summary="Verificar si imagen existe",
    description="Verifica si una imagen existe en el bucket de S3.",
    responses={
        200: {"description": "Verificación completada."},
        503: {"description": "Servicio S3 no disponible."}
    }
)
async def check_image_exists(
    image_key: str
):
    """
    Verifica si una imagen existe en S3.
    
    Args:
        image_key: Key de la imagen a verificar
        
    Returns:
        dict: {"exists": bool, "key": str}
    """
    try:
        service = get_s3_service()
        exists = await service.image_exists(image_key)
        return {"exists": exists, "key": image_key}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar imagen: {str(e)}"
        )
