"""Servicio de integración con OpenStreetMap (Nominatim API) - V2 con Caché"""
import httpx
from typing import Any
from schemas.openstreetmap import (
    GeocodeRequest,
    ReverseGeocodeRequest,
    SearchPlaceRequest,
    GeocodeResponse,
    ReverseGeocodeResponse,
    LocationResult
)
from repositories.geocode_cache_repository import GeocodeCacheRepository


class OpenStreetMapServiceV2:
    """
    Servicio para interactuar con la API de OpenStreetMap (Nominatim).
    
    Proporciona funcionalidades de:
    - Geocodificación: Convertir direcciones a coordenadas
    - Geocodificación inversa: Convertir coordenadas a direcciones
    - Búsqueda de lugares: Encontrar lugares por nombre
    
    Utiliza la API pública de Nominatim (OpenStreetMap) que es gratuita
    con límite de 1 solicitud por segundo.
    
    Implementa un sistema de caché en MongoDB para:
    - Evitar llamadas repetidas a la misma dirección/coordenadas
    - Respetar los límites de uso del servicio
    - Mejorar el rendimiento de la aplicación
    """
    
    # URL base de la API de Nominatim (OpenStreetMap)
    NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
    
    # User-Agent requerido por la política de uso de Nominatim
    USER_AGENT = "BasmatiCalendarApp/1.0 (contact@basmati.app)"
    
    def __init__(self, cache_repository: GeocodeCacheRepository | None = None):
        """
        Inicializa el servicio de OpenStreetMap.
        
        Args:
            cache_repository: Repository de caché (opcional). Si no se proporciona,
                              el servicio funcionará sin caché.
        """
        self.headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "application/json",
            "Accept-Language": "es,en"
        }
        self.cache = cache_repository
    
    async def geocode(self, request: GeocodeRequest) -> GeocodeResponse:
        """
        Geocodifica una dirección convirtiéndola en coordenadas.
        
        Utiliza la API de Nominatim para buscar direcciones y devolver
        sus coordenadas geográficas. Los resultados se cachean para
        evitar llamadas repetidas.
        
        Args:
            request: Datos de la solicitud (dirección, límite de resultados)
            
        Returns:
            GeocodeResponse: Respuesta con las ubicaciones encontradas
        """
        # Parámetros para la clave de caché
        cache_params = {
            "address": request.address.lower().strip(),
            "limit": request.limit
        }
        
        # Intentar obtener del caché
        if self.cache:
            cached = await self.cache.get_or_none("geocode", cache_params)
            if cached:
                # Reconstruir respuesta desde caché
                return GeocodeResponse(**cached)
        
        # Si no hay caché o no se encontró, llamar a la API
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Construir parámetros de búsqueda
                params = {
                    "q": request.address,
                    "format": "json",
                    "addressdetails": 1,
                    "limit": request.limit,
                    "polygon_geojson": 0
                }
                
                response = await client.get(
                    f"{self.NOMINATIM_BASE_URL}/search",
                    params=params,
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    return GeocodeResponse(
                        success=False,
                        query=request.address,
                        results=[],
                        total_results=0,
                        message=f"Error de Nominatim API: {response.status_code}"
                    )
                
                data = response.json()
                results = self._parse_nominatim_results(data)
                
                geocode_response = GeocodeResponse(
                    success=True,
                    query=request.address,
                    results=results,
                    total_results=len(results),
                    message=None
                )
                
                # Guardar en caché si está disponible
                if self.cache:
                    await self.cache.set(
                        "geocode",
                        cache_params,
                        geocode_response.model_dump()
                    )
                
                return geocode_response
                
        except httpx.TimeoutException:
            return GeocodeResponse(
                success=False,
                query=request.address,
                results=[],
                total_results=0,
                message="Timeout al conectar con OpenStreetMap"
            )
        except Exception as e:
            return GeocodeResponse(
                success=False,
                query=request.address,
                results=[],
                total_results=0,
                message=f"Error interno: {str(e)}"
            )
    
    async def reverse_geocode(self, request: ReverseGeocodeRequest) -> ReverseGeocodeResponse:
        """
        Realiza geocodificación inversa: coordenadas a dirección.
        
        Convierte un par de coordenadas (latitud, longitud) en una
        dirección legible. Los resultados se cachean.
        
        Args:
            request: Coordenadas a consultar
            
        Returns:
            ReverseGeocodeResponse: Respuesta con la ubicación encontrada
        """
        # Parámetros para la clave de caché (redondear coordenadas a 6 decimales)
        cache_params = {
            "latitude": round(request.latitude, 6),
            "longitude": round(request.longitude, 6)
        }
        
        # Intentar obtener del caché
        if self.cache:
            cached = await self.cache.get_or_none("reverse", cache_params)
            if cached:
                return ReverseGeocodeResponse(**cached)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    "lat": request.latitude,
                    "lon": request.longitude,
                    "format": "json",
                    "addressdetails": 1,
                    "zoom": 18
                }
                
                response = await client.get(
                    f"{self.NOMINATIM_BASE_URL}/reverse",
                    params=params,
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    return ReverseGeocodeResponse(
                        success=False,
                        latitude=request.latitude,
                        longitude=request.longitude,
                        location=None,
                        message=f"Error de Nominatim API: {response.status_code}"
                    )
                
                data = response.json()
                
                # Verificar si hay error en la respuesta
                if "error" in data:
                    return ReverseGeocodeResponse(
                        success=False,
                        latitude=request.latitude,
                        longitude=request.longitude,
                        location=None,
                        message=data.get("error", "Ubicación no encontrada")
                    )
                
                location = self._parse_single_nominatim_result(data)
                
                reverse_response = ReverseGeocodeResponse(
                    success=True,
                    latitude=request.latitude,
                    longitude=request.longitude,
                    location=location,
                    message=None
                )
                
                # Guardar en caché si está disponible
                if self.cache:
                    await self.cache.set(
                        "reverse",
                        cache_params,
                        reverse_response.model_dump()
                    )
                
                return reverse_response
                
        except httpx.TimeoutException:
            return ReverseGeocodeResponse(
                success=False,
                latitude=request.latitude,
                longitude=request.longitude,
                location=None,
                message="Timeout al conectar con OpenStreetMap"
            )
        except Exception as e:
            return ReverseGeocodeResponse(
                success=False,
                latitude=request.latitude,
                longitude=request.longitude,
                location=None,
                message=f"Error interno: {str(e)}"
            )
    
    async def search_places(self, request: SearchPlaceRequest) -> GeocodeResponse:
        """
        Busca lugares por nombre o tipo.
        
        Permite buscar lugares específicos como universidades, restaurantes, etc.
        Opcionalmente puede priorizar resultados cercanos a unas coordenadas.
        Los resultados se cachean.
        
        Args:
            request: Datos de búsqueda (query, coordenadas opcionales, límite)
            
        Returns:
            GeocodeResponse: Respuesta con los lugares encontrados
        """
        # Parámetros para la clave de caché
        cache_params: dict[str, Any] = {
            "query": request.query.lower().strip(),
            "limit": request.limit
        }
        
        # Incluir coordenadas si se proporcionan (redondeadas)
        if request.near_latitude is not None:
            cache_params["near_latitude"] = round(request.near_latitude, 4)
        if request.near_longitude is not None:
            cache_params["near_longitude"] = round(request.near_longitude, 4)
        
        # Intentar obtener del caché
        if self.cache:
            cached = await self.cache.get_or_none("search", cache_params)
            if cached:
                return GeocodeResponse(**cached)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                params: dict[str, Any] = {
                    "q": request.query,
                    "format": "json",
                    "addressdetails": 1,
                    "limit": request.limit,
                    "polygon_geojson": 0
                }
                
                # Si se proporcionan coordenadas, priorizar resultados cercanos
                if request.near_latitude is not None and request.near_longitude is not None:
                    # Usar viewbox para priorizar resultados cercanos (radio de ~50km)
                    lat = request.near_latitude
                    lon = request.near_longitude
                    delta = 0.5  # Aproximadamente 50km
                    params["viewbox"] = f"{lon - delta},{lat - delta},{lon + delta},{lat + delta}"
                    params["bounded"] = 0  # No limitar estrictamente al viewbox
                
                response = await client.get(
                    f"{self.NOMINATIM_BASE_URL}/search",
                    params=params,
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    return GeocodeResponse(
                        success=False,
                        query=request.query,
                        results=[],
                        total_results=0,
                        message=f"Error de Nominatim API: {response.status_code}"
                    )
                
                data = response.json()
                results = self._parse_nominatim_results(data)
                
                search_response = GeocodeResponse(
                    success=True,
                    query=request.query,
                    results=results,
                    total_results=len(results),
                    message=None
                )
                
                # Guardar en caché si está disponible
                if self.cache:
                    await self.cache.set(
                        "search",
                        cache_params,
                        search_response.model_dump()
                    )
                
                return search_response
                
        except httpx.TimeoutException:
            return GeocodeResponse(
                success=False,
                query=request.query,
                results=[],
                total_results=0,
                message="Timeout al conectar con OpenStreetMap"
            )
        except Exception as e:
            return GeocodeResponse(
                success=False,
                query=request.query,
                results=[],
                total_results=0,
                message=f"Error interno: {str(e)}"
            )
    
    def _parse_nominatim_results(self, data: list[dict]) -> list[LocationResult]:
        """
        Parsea los resultados de Nominatim a nuestro schema.
        
        Args:
            data: Lista de resultados de Nominatim
            
        Returns:
            list[LocationResult]: Lista de ubicaciones parseadas
        """
        results = []
        for item in data:
            location = self._parse_single_nominatim_result(item)
            if location:
                results.append(location)
        return results
    
    def _parse_single_nominatim_result(self, item: dict) -> LocationResult | None:
        """
        Parsea un único resultado de Nominatim.
        
        Args:
            item: Resultado individual de Nominatim
            
        Returns:
            LocationResult: Ubicación parseada o None si hay error
        """
        try:
            address_details = item.get("address", {})
            
            # Construir dirección formateada
            display_name = item.get("display_name", "")
            
            # Extraer ciudad (puede estar en varios campos)
            city = (
                address_details.get("city") or
                address_details.get("town") or
                address_details.get("village") or
                address_details.get("municipality") or
                address_details.get("county")
            )
            
            # Extraer nombre del lugar
            place_name = (
                address_details.get("amenity") or
                address_details.get("building") or
                address_details.get("road") or
                item.get("name")
            )
            
            # Calcular importancia (normalizada entre 0 y 1)
            importance = item.get("importance")
            if importance is not None:
                importance = min(max(float(importance), 0.0), 1.0)
            
            return LocationResult(
                address=display_name,
                latitude=float(item.get("lat", 0)),
                longitude=float(item.get("lon", 0)),
                place_name=place_name,
                city=city,
                country=address_details.get("country"),
                importance=importance,
                osm_id=str(item.get("osm_id", "")),
                map_provider="openstreetmap"
            )
        except Exception:
            return None
    
    async def get_cache_stats(self) -> dict | None:
        """
        Obtiene estadísticas del caché de geocodificación.
        
        Returns:
            dict: Estadísticas del caché o None si no hay caché configurado
        """
        if self.cache:
            return await self.cache.get_stats()
        return None
    
    async def clear_cache(self) -> int:
        """
        Limpia todo el caché de geocodificación.
        
        Returns:
            int: Número de entradas eliminadas, 0 si no hay caché
        """
        if self.cache:
            return await self.cache.clear_all()
        return 0
