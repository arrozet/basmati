"""Schemas para operaciones de OpenStreetMap (Geocoding)"""
from pydantic import BaseModel, ConfigDict, Field


class GeocodeRequest(BaseModel):
    """
    Schema para solicitar geocodificación de una dirección.
    
    Convierte una dirección de texto en coordenadas geográficas.
    """
    address: str = Field(
        ..., 
        min_length=3,
        description="Dirección a geocodificar (ej: 'Calle Larios, Málaga, España')"
    )
    limit: int = Field(
        5, 
        ge=1, 
        le=10, 
        description="Número máximo de resultados a devolver"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "address": "Calle Larios, Málaga, España",
                "limit": 5
            }
        }
    )


class ReverseGeocodeRequest(BaseModel):
    """
    Schema para solicitar geocodificación inversa.
    
    Convierte coordenadas geográficas en una dirección legible.
    """
    latitude: float = Field(
        ..., 
        ge=-90, 
        le=90, 
        description="Latitud en grados decimales (-90 a 90)"
    )
    longitude: float = Field(
        ..., 
        ge=-180, 
        le=180, 
        description="Longitud en grados decimales (-180 a 180)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "latitude": 36.7213,
                "longitude": -4.4217
            }
        }
    )


class LocationResult(BaseModel):
    """
    Schema para un resultado de geocodificación.
    
    Representa una ubicación con sus coordenadas y datos asociados.
    """
    address: str = Field(..., description="Dirección completa formateada")
    latitude: float = Field(..., ge=-90, le=90, description="Latitud en grados decimales")
    longitude: float = Field(..., ge=-180, le=180, description="Longitud en grados decimales")
    place_name: str | None = Field(None, description="Nombre del lugar (si está disponible)")
    city: str | None = Field(None, description="Ciudad")
    country: str | None = Field(None, description="País")
    importance: float | None = Field(None, description="Relevancia del resultado (0-1)")
    osm_id: str | None = Field(None, description="ID de OpenStreetMap para referencia")
    map_provider: str = Field(default="openstreetmap", description="Proveedor del mapa")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "address": "Calle Marqués de Larios, 1, 29015 Málaga, España",
                "latitude": 36.7213,
                "longitude": -4.4217,
                "place_name": "Calle Marqués de Larios",
                "city": "Málaga",
                "country": "España",
                "importance": 0.85,
                "osm_id": "12345678",
                "map_provider": "openstreetmap"
            }
        }
    )


class GeocodeResponse(BaseModel):
    """
    Schema de respuesta para operaciones de geocodificación.
    
    Contiene lista de ubicaciones encontradas.
    """
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    query: str = Field(..., description="Consulta original realizada")
    results: list[LocationResult] = Field(
        default_factory=list, 
        description="Lista de ubicaciones encontradas"
    )
    total_results: int = Field(0, description="Número total de resultados")
    message: str | None = Field(None, description="Mensaje adicional o de error")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "query": "Calle Larios, Málaga, España",
                "results": [
                    {
                        "address": "Calle Marqués de Larios, 1, 29015 Málaga, España",
                        "latitude": 36.7213,
                        "longitude": -4.4217,
                        "place_name": "Calle Marqués de Larios",
                        "city": "Málaga",
                        "country": "España",
                        "importance": 0.85,
                        "osm_id": "12345678",
                        "map_provider": "openstreetmap"
                    }
                ],
                "total_results": 1,
                "message": None
            }
        }
    )


class ReverseGeocodeResponse(BaseModel):
    """
    Schema de respuesta para geocodificación inversa.
    
    Contiene la ubicación encontrada para las coordenadas dadas.
    """
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    latitude: float = Field(..., description="Latitud consultada")
    longitude: float = Field(..., description="Longitud consultada")
    location: LocationResult | None = Field(None, description="Ubicación encontrada")
    message: str | None = Field(None, description="Mensaje adicional o de error")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "latitude": 36.7213,
                "longitude": -4.4217,
                "location": {
                    "address": "Calle Marqués de Larios, 1, 29015 Málaga, España",
                    "latitude": 36.7213,
                    "longitude": -4.4217,
                    "place_name": "Calle Marqués de Larios",
                    "city": "Málaga",
                    "country": "España",
                    "importance": 0.85,
                    "osm_id": "12345678",
                    "map_provider": "openstreetmap"
                },
                "message": None
            }
        }
    )


class SearchPlaceRequest(BaseModel):
    """
    Schema para buscar lugares por nombre o tipo.
    
    Permite buscar lugares específicos como restaurantes, universidades, etc.
    """
    query: str = Field(
        ..., 
        min_length=2,
        description="Término de búsqueda (ej: 'Universidad de Málaga')"
    )
    near_latitude: float | None = Field(
        None, 
        ge=-90, 
        le=90, 
        description="Latitud para priorizar resultados cercanos"
    )
    near_longitude: float | None = Field(
        None, 
        ge=-180, 
        le=180, 
        description="Longitud para priorizar resultados cercanos"
    )
    limit: int = Field(
        5, 
        ge=1, 
        le=20, 
        description="Número máximo de resultados"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "Universidad de Málaga",
                "near_latitude": 36.7213,
                "near_longitude": -4.4217,
                "limit": 5
            }
        }
    )
