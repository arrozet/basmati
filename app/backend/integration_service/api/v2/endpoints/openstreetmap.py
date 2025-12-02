"""Endpoints de OpenStreetMap V2 - Geocodificación y búsqueda de lugares con caché"""
from fastapi import APIRouter, HTTPException, status, Query, Depends
from schemas.openstreetmap import (
    GeocodeRequest,
    ReverseGeocodeRequest,
    SearchPlaceRequest,
    GeocodeResponse,
    ReverseGeocodeResponse
)
from services.v2.openstreetmap_service import OpenStreetMapServiceV2
from repositories.geocode_cache_repository import GeocodeCacheRepository
from core.database import get_database

router = APIRouter()


def get_osm_service() -> OpenStreetMapServiceV2:
    """
    Crea una instancia del servicio de OpenStreetMap V2 con caché.
    
    Inyecta el repositorio de caché conectado a MongoDB para
    almacenar y recuperar resultados de geocodificación.
    
    Returns:
        OpenStreetMapServiceV2: Servicio configurado con caché
    """
    database = get_database()
    cache_repository = GeocodeCacheRepository(database)
    return OpenStreetMapServiceV2(cache_repository=cache_repository)


@router.get(
    "/geocode",
    response_model=GeocodeResponse,
    status_code=status.HTTP_200_OK,
    summary="Geocodificar dirección (V2)",
    description="Convierte una dirección de texto en coordenadas geográficas usando OpenStreetMap.",
    responses={
        200: {"description": "Geocodificación exitosa."},
        400: {"description": "Parámetros de búsqueda inválidos."},
        500: {"description": "Error interno del servidor al geocodificar."}
    }
)
async def geocode_address(
    address: str = Query(
        ..., 
        min_length=3,
        description="Dirección a geocodificar (ej: 'Calle Larios, Málaga, España')"
    ),
    limit: int = Query(
        5, 
        ge=1, 
        le=10, 
        description="Número máximo de resultados a devolver"
    )
):
    """
    Geocodifica una dirección convirtiéndola en coordenadas geográficas.
    
    Utiliza la API de Nominatim (OpenStreetMap) para buscar direcciones
    y devolver sus coordenadas (latitud, longitud).
    
    Args:
        address: Dirección a geocodificar
        limit: Número máximo de resultados
        
    Returns:
        GeocodeResponse: Lista de ubicaciones encontradas con sus coordenadas
    """
    try:
        service = get_osm_service()
        request = GeocodeRequest(address=address, limit=limit)
        return await service.geocode(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al geocodificar dirección: {str(e)}"
        )


@router.get(
    "/reverse-geocode",
    response_model=ReverseGeocodeResponse,
    status_code=status.HTTP_200_OK,
    summary="Geocodificación inversa (V2)",
    description="Convierte coordenadas geográficas en una dirección legible usando OpenStreetMap.",
    responses={
        200: {"description": "Geocodificación inversa exitosa."},
        400: {"description": "Coordenadas inválidas."},
        500: {"description": "Error interno del servidor."}
    }
)
async def reverse_geocode(
    latitude: float = Query(
        ..., 
        ge=-90, 
        le=90, 
        description="Latitud en grados decimales (-90 a 90)"
    ),
    longitude: float = Query(
        ..., 
        ge=-180, 
        le=180, 
        description="Longitud en grados decimales (-180 a 180)"
    )
):
    """
    Realiza geocodificación inversa: coordenadas a dirección.
    
    Convierte un par de coordenadas (latitud, longitud) en una
    dirección legible usando la API de Nominatim.
    
    Args:
        latitude: Latitud en grados decimales
        longitude: Longitud en grados decimales
        
    Returns:
        ReverseGeocodeResponse: Ubicación encontrada con su dirección
    """
    try:
        service = get_osm_service()
        request = ReverseGeocodeRequest(latitude=latitude, longitude=longitude)
        return await service.reverse_geocode(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al realizar geocodificación inversa: {str(e)}"
        )


@router.get(
    "/search-places",
    response_model=GeocodeResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar lugares (V2)",
    description="Busca lugares por nombre o tipo usando OpenStreetMap. Opcionalmente prioriza resultados cercanos a unas coordenadas.",
    responses={
        200: {"description": "Búsqueda de lugares exitosa."},
        400: {"description": "Parámetros de búsqueda inválidos."},
        500: {"description": "Error interno del servidor."}
    }
)
async def search_places(
    query: str = Query(
        ..., 
        min_length=2,
        description="Término de búsqueda (ej: 'Universidad de Málaga')"
    ),
    near_latitude: float | None = Query(
        None, 
        ge=-90, 
        le=90, 
        description="Latitud para priorizar resultados cercanos (opcional)"
    ),
    near_longitude: float | None = Query(
        None, 
        ge=-180, 
        le=180, 
        description="Longitud para priorizar resultados cercanos (opcional)"
    ),
    limit: int = Query(
        5, 
        ge=1, 
        le=20, 
        description="Número máximo de resultados"
    )
):
    """
    Busca lugares por nombre o tipo.
    
    Permite buscar lugares específicos como universidades, restaurantes, etc.
    Opcionalmente puede priorizar resultados cercanos a unas coordenadas dadas.
    
    Args:
        query: Término de búsqueda
        near_latitude: Latitud para priorizar cercanía (opcional)
        near_longitude: Longitud para priorizar cercanía (opcional)
        limit: Número máximo de resultados
        
    Returns:
        GeocodeResponse: Lista de lugares encontrados
    """
    try:
        service = get_osm_service()
        request = SearchPlaceRequest(
            query=query,
            near_latitude=near_latitude,
            near_longitude=near_longitude,
            limit=limit
        )
        return await service.search_places(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar lugares: {str(e)}"
        )


@router.get(
    "/cache/stats",
    status_code=status.HTTP_200_OK,
    summary="Estadísticas del caché de geocodificación",
    description="Obtiene estadísticas del sistema de caché de geocodificación.",
    responses={
        200: {"description": "Estadísticas del caché."},
        500: {"description": "Error interno del servidor."}
    }
)
async def get_cache_stats():
    """
    Obtiene estadísticas del caché de geocodificación.
    
    Muestra información sobre:
    - Total de entradas en caché
    - Total de hits (accesos exitosos al caché)
    - Estadísticas por tipo de consulta (geocode, reverse, search)
    - Tiempo de vida configurado (TTL)
    
    Returns:
        dict: Estadísticas del caché
    """
    try:
        service = get_osm_service()
        stats = await service.get_cache_stats()
        if stats is None:
            return {"message": "Caché no configurado", "enabled": False}
        return {"enabled": True, **stats}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas del caché: {str(e)}"
        )


@router.delete(
    "/cache",
    status_code=status.HTTP_200_OK,
    summary="Limpiar caché de geocodificación",
    description="Elimina todas las entradas del caché de geocodificación.",
    responses={
        200: {"description": "Caché limpiado exitosamente."},
        500: {"description": "Error interno del servidor."}
    }
)
async def clear_cache():
    """
    Limpia todo el caché de geocodificación.
    
    Útil para forzar la recarga de datos frescos desde la API de Nominatim.
    
    Returns:
        dict: Número de entradas eliminadas
    """
    try:
        service = get_osm_service()
        deleted_count = await service.clear_cache()
        return {
            "success": True,
            "message": f"Caché limpiado exitosamente",
            "deleted_entries": deleted_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al limpiar caché: {str(e)}"
        )
