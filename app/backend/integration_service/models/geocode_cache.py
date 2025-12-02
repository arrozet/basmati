"""Modelo de caché de geocodificación para MongoDB"""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from models.integration_source import PyObjectId


class GeocodeCacheModel(BaseModel):
    """
    Modelo para almacenar resultados de geocodificación en caché.
    
    Almacena las respuestas de la API de Nominatim para evitar
    llamadas repetidas y respetar los límites de uso del servicio.
    
        Atributos:
        id: ID único del documento en MongoDB
        cache_key: Clave única para identificar la consulta (hash de parámetros)
        query_type: Tipo de consulta ("geocode", "reverse", "search")
        query_params: Parámetros originales de la consulta
        response_data: Respuesta completa de la API almacenada
        created_at: Fecha de creación del registro
        expires_at: Fecha de expiración para TTL automático
        hit_count: Número de veces que se ha utilizado este caché
        last_accessed: Última vez que se accedió a este registro
        schema_version: Versión del esquema del documento (para evolución futura)
    """
    id: PyObjectId | None = Field(alias="_id", default=None)
    cache_key: str = Field(..., description="Clave única de la consulta (hash)")
    query_type: str = Field(..., description="Tipo: geocode, reverse, search")
    query_params: dict = Field(..., description="Parámetros originales de la consulta")
    response_data: dict = Field(..., description="Respuesta de la API cacheada")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(..., description="Fecha de expiración para TTL")
    hit_count: int = Field(default=0, description="Contador de accesos al caché")
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    schema_version: int = Field(default=1, description="Versión del esquema del documento")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "cache_key": "geocode:calle_larios_malaga_espana:5",
                "query_type": "geocode",
                "query_params": {
                    "address": "Calle Larios, Málaga, España",
                    "limit": 5
                },
                "response_data": {
                    "success": True,
                    "query": "Calle Larios, Málaga, España",
                    "results": [],
                    "total_results": 0
                },
                "hit_count": 10,
                "created_at": "2024-01-15T10:30:00Z",
                "expires_at": "2024-01-22T10:30:00Z",
                "last_accessed": "2024-01-16T14:20:00Z",
                "schema_version": 1
            }
        }
    )

