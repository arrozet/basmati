"""Endpoints de OpenStreetMap V2 - Geocodificación y búsqueda de lugares"""
from fastapi import APIRouter, HTTPException, status, Query
from schemas.openstreetmap import (
    GeocodeRequest,
    ReverseGeocodeRequest,
    SearchPlaceRequest,
    GeocodeResponse,
    ReverseGeocodeResponse
)
from services.v2.openstreetmap_service import OpenStreetMapServiceV2

router = APIRouter()


def get_osm_service() -> OpenStreetMapServiceV2:
    """Crea una instancia del servicio de OpenStreetMap V2"""
    return OpenStreetMapServiceV2()


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
