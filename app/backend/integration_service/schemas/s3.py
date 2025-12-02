"""Schemas para operaciones de imágenes con AWS S3"""
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class ImageUploadRequest(BaseModel):
    """
    Schema para solicitar URL de subida presigned a S3.
    
    El cliente usa esta URL para subir la imagen directamente a S3.
    """
    filename: str = Field(..., description="Nombre del archivo a subir")
    content_type: str = Field(
        default="image/jpeg", 
        description="Tipo MIME del archivo (image/jpeg, image/png, image/gif, image/webp)"
    )
    folder: str | None = Field(
        default=None, 
        description="Carpeta opcional en S3 (ej: 'events', 'avatars', 'calendars')"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "evento_navidad.jpg",
                "content_type": "image/jpeg",
                "folder": "events"
            }
        }
    )


class ImageUploadResponse(BaseModel):
    """Schema de respuesta con URL presigned para subir imagen"""
    upload_url: str = Field(..., description="URL presigned para subir la imagen (válida por 1 hora)")
    image_key: str = Field(..., description="Key única de la imagen en S3")
    public_url: str = Field(..., description="URL pública para acceder a la imagen una vez subida")
    expires_in: int = Field(default=3600, description="Tiempo de expiración de la URL en segundos")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "upload_url": "https://basmati-s3.s3.us-east-1.amazonaws.com/events/abc123.jpg?X-Amz-...",
                "image_key": "events/abc123.jpg",
                "public_url": "https://basmati-s3.s3.us-east-1.amazonaws.com/events/abc123.jpg",
                "expires_in": 3600
            }
        }
    )


class ImageMetadata(BaseModel):
    """Schema con metadatos de una imagen almacenada en S3"""
    key: str = Field(..., description="Key única de la imagen en S3")
    filename: str = Field(..., description="Nombre original del archivo")
    url: str = Field(..., description="URL pública de la imagen")
    size: int | None = Field(None, description="Tamaño del archivo en bytes")
    content_type: str | None = Field(None, description="Tipo MIME del archivo")
    last_modified: datetime | None = Field(None, description="Fecha de última modificación")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "key": "events/abc123.jpg",
                "filename": "evento_navidad.jpg",
                "url": "https://basmati-s3.s3.us-east-1.amazonaws.com/events/abc123.jpg",
                "size": 245678,
                "content_type": "image/jpeg",
                "last_modified": "2025-12-01T10:30:00Z"
            }
        }
    )


class ImageListResponse(BaseModel):
    """Schema de respuesta para listar imágenes"""
    images: list[ImageMetadata] = Field(default_factory=list, description="Lista de imágenes")
    total: int = Field(..., description="Total de imágenes encontradas")
    prefix: str | None = Field(None, description="Prefijo/carpeta filtrado")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "images": [
                    {
                        "key": "events/abc123.jpg",
                        "filename": "evento_navidad.jpg",
                        "url": "https://basmati-s3.s3.us-east-1.amazonaws.com/events/abc123.jpg",
                        "size": 245678,
                        "content_type": "image/jpeg",
                        "last_modified": "2025-12-01T10:30:00Z"
                    }
                ],
                "total": 1,
                "prefix": "events"
            }
        }
    )


class ImageDeleteResponse(BaseModel):
    """Schema de respuesta para eliminar imagen"""
    success: bool = Field(..., description="Indica si la eliminación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo del resultado")
    deleted_key: str | None = Field(None, description="Key de la imagen eliminada")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Imagen eliminada correctamente",
                "deleted_key": "events/abc123.jpg"
            }
        }
    )


class ImageDownloadResponse(BaseModel):
    """Schema de respuesta para obtener URL de descarga"""
    download_url: str = Field(..., description="URL presigned para descargar la imagen")
    key: str = Field(..., description="Key de la imagen en S3")
    expires_in: int = Field(default=3600, description="Tiempo de expiración de la URL en segundos")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "download_url": "https://basmati-s3.s3.us-east-1.amazonaws.com/events/abc123.jpg?X-Amz-...",
                "key": "events/abc123.jpg",
                "expires_in": 3600
            }
        }
    )


class BulkDeleteRequest(BaseModel):
    """Schema para eliminar múltiples imágenes"""
    keys: list[str] = Field(..., description="Lista de keys de imágenes a eliminar", min_length=1)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "keys": ["events/abc123.jpg", "events/def456.png", "avatars/user1.jpg"]
            }
        }
    )


class BulkDeleteResponse(BaseModel):
    """Schema de respuesta para eliminar múltiples imágenes"""
    success: bool = Field(..., description="Indica si todas las eliminaciones fueron exitosas")
    deleted_count: int = Field(..., description="Número de imágenes eliminadas correctamente")
    errors: list[str] = Field(default_factory=list, description="Lista de errores si los hubo")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "deleted_count": 3,
                "errors": []
            }
        }
    )
