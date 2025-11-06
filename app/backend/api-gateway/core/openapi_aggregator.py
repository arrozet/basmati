"""
OpenAPI Aggregator para el API Gateway.
Obtiene y combina las especificaciones OpenAPI de todos los servicios backend.
"""
import httpx
from typing import Dict, Any, Optional
from core.config import SERVICES
import logging

logger = logging.getLogger(__name__)

# Cache para las especificaciones OpenAPI
_openapi_cache: Optional[Dict[str, Any]] = None


async def fetch_service_openapi(service_name: str, service_url: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene la especificación OpenAPI de un servicio backend.

    Args:
        service_name: Nombre del servicio
        service_url: URL base del servicio

    Returns:
        Dict con la especificación OpenAPI o None si falla
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{service_url}/openapi.json")
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Service {service_name} returned status {response.status_code} for OpenAPI spec")
                return None
    except Exception as e:
        logger.warning(f"Failed to fetch OpenAPI spec from {service_name}: {e}")
        return None


async def aggregate_openapi_specs(force_refresh: bool = False) -> Dict[str, Any]:
    """
    Combina las especificaciones OpenAPI de todos los servicios en una sola.

    Args:
        force_refresh: Si True, ignora el cache y recarga las specs

    Returns:
        Dict con la especificación OpenAPI combinada
    """
    global _openapi_cache

    # Usar cache si existe y no se fuerza refresh
    if _openapi_cache is not None and not force_refresh:
        return _openapi_cache

    # Spec base del gateway
    combined_spec = {
        "openapi": "3.1.0",
        "info": {
            "title": "Basmati API Gateway",
            "description": "Punto de entrada centralizado para todos los servicios de Basmati",
            "version": "1.0.0"
        },
        "paths": {},
        "components": {
            "schemas": {}
        }
    }

    # Obtener specs de todos los servicios
    for service_name, service_url in SERVICES.items():
        logger.info(f"Fetching OpenAPI spec from {service_name} at {service_url}")
        service_spec = await fetch_service_openapi(service_name, service_url)

        if service_spec is None:
            logger.warning(f"Skipping service {service_name} - no OpenAPI spec available")
            continue

        logger.info(f"Processing {len(service_spec.get('paths', {}))} paths from {service_name}")

        # Combinar schemas de componentes primero
        service_schema_mapping = {}
        if "components" in service_spec and "schemas" in service_spec["components"]:
            for schema_name, schema_def in service_spec["components"]["schemas"].items():
                # Prefijar schemas con el nombre del servicio para evitar colisiones
                prefixed_schema_name = f"{service_name.capitalize()}{schema_name}"
                combined_spec["components"]["schemas"][prefixed_schema_name] = schema_def
                service_schema_mapping[schema_name] = prefixed_schema_name

        # Combinar paths del servicio
        if "paths" in service_spec:
            for path, path_item in service_spec["paths"].items():
                # Prefijar las rutas con /v1/{service}
                # Los servicios ya tienen /v1/ en sus paths, así que solo añadimos el prefijo del servicio
                gateway_path = path.replace("/v1/", f"/v1/{service_name}/", 1)

                # Filtrar solo los métodos que soportamos: GET, POST, PUT, DELETE
                filtered_path_item = {}
                for method in ["get", "post", "put", "delete"]:
                    if method in path_item:
                        filtered_path_item[method] = path_item[method]

                        # Log si tiene requestBody (para debugging)
                        if "requestBody" in path_item[method]:
                            logger.debug(f"  {method.upper()} {gateway_path} has requestBody")

                # Solo añadir el path si tiene al menos un método soportado
                if filtered_path_item:
                    combined_spec["paths"][gateway_path] = filtered_path_item

    # Añadir endpoint de health del gateway
    combined_spec["paths"]["/health"] = {
        "get": {
            "summary": "Health Check del API Gateway",
            "description": "Verifica el estado del API Gateway",
            "responses": {
                "200": {
                    "description": "Gateway saludable",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string"},
                                    "service": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    # Cachear el resultado
    _openapi_cache = combined_spec

    return combined_spec


def clear_openapi_cache():
    """Limpia el cache de especificaciones OpenAPI."""
    global _openapi_cache
    _openapi_cache = None
