"""
Servicio para gestión de imágenes en AWS S3 (V2).

Proporciona operaciones CRUD para imágenes almacenadas en un bucket de S3.
"""
import uuid
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime
from schemas.s3 import (
    ImageUploadRequest,
    ImageUploadResponse,
    ImageMetadata,
    ImageListResponse,
    ImageDeleteResponse,
    ImageDownloadResponse,
    BulkDeleteResponse
)


class S3ImageService:
    """
    Servicio para gestión de imágenes en AWS S3.
    
    Proporciona operaciones CRUD:
    - Create: Generar URLs presigned para subir imágenes
    - Read: Obtener URLs de descarga y listar imágenes
    - Delete: Eliminar imágenes individuales o en lote
    """
    
    # Tipos MIME permitidos para imágenes
    ALLOWED_CONTENT_TYPES = [
        "image/jpeg",
        "image/png", 
        "image/gif",
        "image/webp",
        "image/svg+xml",
        "image/bmp"
    ]
    
    # Tiempo de expiración por defecto para URLs presigned (1 hora)
    DEFAULT_EXPIRATION = 3600
    
    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_region: str,
        bucket_name: str
    ):
        """
        Inicializa el servicio de S3.
        
        Args:
            aws_access_key_id: ID de clave de acceso de AWS
            aws_secret_access_key: Clave secreta de acceso de AWS
            aws_region: Región de AWS donde está el bucket
            bucket_name: Nombre del bucket de S3
        """
        self.bucket_name = bucket_name
        self.region = aws_region
        
        # Crear cliente de S3 con las credenciales proporcionadas
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
    
    def _generate_unique_key(self, filename: str, folder: str | None = None) -> str:
        """
        Genera una key única para el archivo en S3.
        
        Combina un UUID con el nombre original para evitar colisiones.
        
        Args:
            filename: Nombre original del archivo
            folder: Carpeta opcional (ej: 'events', 'avatars')
            
        Returns:
            str: Key única para S3 (ej: 'events/abc123_imagen.jpg')
        """
        # Generar ID único
        unique_id = str(uuid.uuid4())[:8]
        
        # Limpiar nombre de archivo (quitar caracteres especiales)
        clean_filename = "".join(c for c in filename if c.isalnum() or c in "._-").lower()
        
        # Construir key con o sin carpeta
        if folder:
            return f"{folder}/{unique_id}_{clean_filename}"
        return f"{unique_id}_{clean_filename}"
    
    def _get_public_url(self, key: str) -> str:
        """
        Construye la URL pública de un objeto en S3.
        
        Args:
            key: Key del objeto en S3
            
        Returns:
            str: URL pública del objeto
        """
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
    
    def _validate_content_type(self, content_type: str) -> bool:
        """
        Valida que el tipo de contenido sea una imagen permitida.
        
        Args:
            content_type: Tipo MIME a validar
            
        Returns:
            bool: True si es un tipo permitido
        """
        return content_type in self.ALLOWED_CONTENT_TYPES
    
    # ==================== CREATE ====================
    
    async def generate_upload_url(
        self, 
        request: ImageUploadRequest,
        expiration: int = DEFAULT_EXPIRATION
    ) -> ImageUploadResponse:
        """
        Genera una URL presigned para subir una imagen a S3.
        
        El cliente puede usar esta URL para subir directamente a S3
        sin pasar por el backend, mejorando el rendimiento.
        
        Args:
            request: Datos de la imagen a subir (filename, content_type, folder)
            expiration: Tiempo de expiración de la URL en segundos
            
        Returns:
            ImageUploadResponse: URL de subida, key y URL pública
            
        Raises:
            ValueError: Si el tipo de contenido no es una imagen válida
            Exception: Si hay error al generar la URL
        """
        # Validar tipo de contenido
        if not self._validate_content_type(request.content_type):
            raise ValueError(
                f"Tipo de contenido no permitido: {request.content_type}. "
                f"Tipos permitidos: {', '.join(self.ALLOWED_CONTENT_TYPES)}"
            )
        
        # Generar key única para el archivo
        image_key = self._generate_unique_key(request.filename, request.folder)
        
        try:
            # Generar URL presigned para PUT (subida)
            upload_url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': image_key,
                    'ContentType': request.content_type
                },
                ExpiresIn=expiration
            )
            
            return ImageUploadResponse(
                upload_url=upload_url,
                image_key=image_key,
                public_url=self._get_public_url(image_key),
                expires_in=expiration
            )
            
        except NoCredentialsError:
            raise Exception("Credenciales de AWS no configuradas correctamente")
        except ClientError as e:
            raise Exception(f"Error al generar URL de subida: {str(e)}")
    
    # ==================== READ ====================
    
    async def get_image_metadata(self, key: str) -> ImageMetadata | None:
        """
        Obtiene los metadatos de una imagen en S3.
        
        Args:
            key: Key de la imagen en S3
            
        Returns:
            ImageMetadata: Metadatos de la imagen o None si no existe
        """
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            # Extraer nombre original del archivo de la key
            filename = key.split('/')[-1]
            if '_' in filename:
                # Formato: uuid_filename.ext -> extraer filename.ext
                filename = '_'.join(filename.split('_')[1:])
            
            return ImageMetadata(
                key=key,
                filename=filename,
                url=self._get_public_url(key),
                size=response.get('ContentLength'),
                content_type=response.get('ContentType'),
                last_modified=response.get('LastModified')
            )
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None
            raise Exception(f"Error al obtener metadatos: {str(e)}")
    
    async def generate_download_url(
        self, 
        key: str,
        expiration: int = DEFAULT_EXPIRATION
    ) -> ImageDownloadResponse:
        """
        Genera una URL presigned para descargar una imagen.
        
        Útil para imágenes privadas que requieren autenticación.
        
        Args:
            key: Key de la imagen en S3
            expiration: Tiempo de expiración de la URL en segundos
            
        Returns:
            ImageDownloadResponse: URL de descarga temporal
            
        Raises:
            Exception: Si la imagen no existe o hay error
        """
        try:
            # Verificar que la imagen existe
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            
            # Generar URL presigned para GET (descarga)
            download_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expiration
            )
            
            return ImageDownloadResponse(
                download_url=download_url,
                key=key,
                expires_in=expiration
            )
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                raise Exception(f"Imagen no encontrada: {key}")
            raise Exception(f"Error al generar URL de descarga: {str(e)}")
    
    async def list_images(
        self, 
        prefix: str | None = None,
        max_results: int = 100
    ) -> ImageListResponse:
        """
        Lista las imágenes en el bucket de S3.
        
        Puede filtrar por prefijo/carpeta para obtener imágenes
        de una categoría específica (events, avatars, etc.).
        
        Args:
            prefix: Prefijo/carpeta para filtrar (ej: 'events/')
            max_results: Número máximo de resultados
            
        Returns:
            ImageListResponse: Lista de imágenes con metadatos
        """
        try:
            # Construir parámetros de la petición
            params = {
                'Bucket': self.bucket_name,
                'MaxKeys': max_results
            }
            
            if prefix:
                # Asegurar que el prefijo termine con /
                if not prefix.endswith('/'):
                    prefix = f"{prefix}/"
                params['Prefix'] = prefix
            
            # Listar objetos
            response = self.s3_client.list_objects_v2(**params)
            
            images = []
            for obj in response.get('Contents', []):
                key = obj['Key']
                
                # Filtrar solo imágenes (por extensión)
                if not any(key.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp']):
                    continue
                
                # Extraer nombre original del archivo
                filename = key.split('/')[-1]
                if '_' in filename:
                    filename = '_'.join(filename.split('_')[1:])
                
                images.append(ImageMetadata(
                    key=key,
                    filename=filename,
                    url=self._get_public_url(key),
                    size=obj.get('Size'),
                    content_type=None,  # list_objects_v2 no devuelve ContentType
                    last_modified=obj.get('LastModified')
                ))
            
            return ImageListResponse(
                images=images,
                total=len(images),
                prefix=prefix.rstrip('/') if prefix else None
            )
            
        except ClientError as e:
            raise Exception(f"Error al listar imágenes: {str(e)}")
    
    # ==================== DELETE ====================
    
    async def delete_image(self, key: str) -> ImageDeleteResponse:
        """
        Elimina una imagen del bucket de S3.
        
        Args:
            key: Key de la imagen a eliminar
            
        Returns:
            ImageDeleteResponse: Resultado de la eliminación
        """
        try:
            # Verificar que la imagen existe antes de eliminar
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    return ImageDeleteResponse(
                        success=False,
                        message=f"Imagen no encontrada: {key}",
                        deleted_key=None
                    )
                raise
            
            # Eliminar el objeto
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            return ImageDeleteResponse(
                success=True,
                message="Imagen eliminada correctamente",
                deleted_key=key
            )
            
        except ClientError as e:
            return ImageDeleteResponse(
                success=False,
                message=f"Error al eliminar imagen: {str(e)}",
                deleted_key=None
            )
    
    async def delete_images_bulk(self, keys: list[str]) -> BulkDeleteResponse:
        """
        Elimina múltiples imágenes del bucket de S3.
        
        Más eficiente que eliminar una por una cuando hay
        muchas imágenes que borrar.
        
        Args:
            keys: Lista de keys de imágenes a eliminar
            
        Returns:
            BulkDeleteResponse: Resultado con contador y errores
        """
        if not keys:
            return BulkDeleteResponse(
                success=True,
                deleted_count=0,
                errors=[]
            )
        
        try:
            # Preparar objetos para eliminación masiva
            objects_to_delete = [{'Key': key} for key in keys]
            
            # Eliminar en lote (máximo 1000 objetos por llamada)
            response = self.s3_client.delete_objects(
                Bucket=self.bucket_name,
                Delete={
                    'Objects': objects_to_delete,
                    'Quiet': False  # Para obtener información de errores
                }
            )
            
            # Contar eliminados y errores
            deleted_count = len(response.get('Deleted', []))
            errors = []
            
            for error in response.get('Errors', []):
                errors.append(f"Error al eliminar {error['Key']}: {error['Message']}")
            
            return BulkDeleteResponse(
                success=len(errors) == 0,
                deleted_count=deleted_count,
                errors=errors
            )
            
        except ClientError as e:
            return BulkDeleteResponse(
                success=False,
                deleted_count=0,
                errors=[f"Error en eliminación masiva: {str(e)}"]
            )
    
    # ==================== UTILIDADES ====================
    
    async def image_exists(self, key: str) -> bool:
        """
        Verifica si una imagen existe en S3.
        
        Args:
            key: Key de la imagen a verificar
            
        Returns:
            bool: True si la imagen existe
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise Exception(f"Error al verificar imagen: {str(e)}")
    
    async def copy_image(
        self, 
        source_key: str, 
        destination_folder: str | None = None,
        new_filename: str | None = None
    ) -> ImageMetadata:
        """
        Copia una imagen a otra ubicación en S3.
        
        Útil para mover imágenes entre carpetas o hacer backups.
        
        Args:
            source_key: Key de la imagen origen
            destination_folder: Carpeta destino (opcional)
            new_filename: Nuevo nombre de archivo (opcional)
            
        Returns:
            ImageMetadata: Metadatos de la imagen copiada
            
        Raises:
            Exception: Si la imagen origen no existe o hay error
        """
        try:
            # Verificar que la imagen origen existe
            source_metadata = await self.get_image_metadata(source_key)
            if not source_metadata:
                raise Exception(f"Imagen origen no encontrada: {source_key}")
            
            # Determinar key de destino
            filename = new_filename or source_metadata.filename
            dest_key = self._generate_unique_key(filename, destination_folder)
            
            # Copiar objeto
            self.s3_client.copy_object(
                Bucket=self.bucket_name,
                CopySource={'Bucket': self.bucket_name, 'Key': source_key},
                Key=dest_key
            )
            
            # Obtener metadatos del objeto copiado
            return await self.get_image_metadata(dest_key)
            
        except ClientError as e:
            raise Exception(f"Error al copiar imagen: {str(e)}")
