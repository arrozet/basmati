"""
OpenAPI Aggregator para el API Gateway.
Obtiene y combina las especificaciones OpenAPI de todos los servicios backend.
"""
import httpx
from typing import Dict, Any, Optional
from core.config import SERVICES
import logging
import json
import re

logger = logging.getLogger(__name__)

# Cache para las especificaciones OpenAPI
_openapi_cache: Optional[Dict[str, Any]] = None


def update_schema_refs(obj: Any, schema_mapping: Dict[str, str]) -> Any:
    """
    Actualiza recursivamente las referencias $ref en un objeto OpenAPI.

    Reemplaza referencias como #/components/schemas/UserCreate con el nombre prefijado
    como #/components/schemas/UsersUserCreate según el mapeo proporcionado.

    Args:
        obj: Objeto (dict, list, o valor primitivo) a procesar
        schema_mapping: Mapeo de nombre original -> nombre prefijado

    Returns:
        Copia del objeto con referencias actualizadas
    """
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            if key == "$ref" and isinstance(value, str):
                # Actualizar referencia si apunta a un schema
                match = re.match(r"#/components/schemas/(.+)", value)
                if match:
                    schema_name = match.group(1)
                    if schema_name in schema_mapping:
                        new_schema_name = schema_mapping[schema_name]
                        result[key] = f"#/components/schemas/{new_schema_name}"
                        logger.debug(f"Updated ref: {schema_name} -> {new_schema_name}")
                    else:
                        result[key] = value
                else:
                    result[key] = value
            else:
                # Procesar recursivamente
                result[key] = update_schema_refs(value, schema_mapping)
        return result

    elif isinstance(obj, list):
        # Procesar recursivamente todos los elementos de la lista
        return [update_schema_refs(item, schema_mapping) for item in obj]

    else:
        # Valores primitivos (str, int, bool, None) se devuelven tal cual
        return obj


async def fetch_service_openapi(
    service_name: str, 
    service_url: str,
    max_retries: int = 5,
    initial_delay: float = 1.0
) -> Optional[Dict[str, Any]]:
    """
    Obtiene la especificación OpenAPI de un servicio backend con reintentos.

    Implementa exponential backoff para manejar servicios que aún no están
    listos durante el arranque.

    Args:
        service_name: Nombre del servicio
        service_url: URL base del servicio
        max_retries: Número máximo de reintentos (default: 5)
        initial_delay: Delay inicial en segundos entre reintentos (default: 1.0)

    Returns:
        Dict con la especificación OpenAPI o None si falla tras todos los reintentos
    """
    import asyncio
    
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{service_url}/openapi.json")
                if response.status_code == 200:
                    if attempt > 0:
                        logger.info(f"Successfully fetched OpenAPI from {service_name} after {attempt + 1} attempts")
                    return response.json()
                else:
                    logger.warning(f"Service {service_name} returned status {response.status_code} for OpenAPI spec")
                    return None
        except Exception as e:
            if attempt < max_retries - 1:
                logger.info(f"Attempt {attempt + 1}/{max_retries} failed for {service_name}, retrying in {delay:.1f}s...")
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                logger.warning(f"Failed to fetch OpenAPI spec from {service_name} after {max_retries} attempts: {e}")
                return None
    
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
            # Primero crear el mapeo de nombres
            for schema_name, schema_def in service_spec["components"]["schemas"].items():
                prefixed_schema_name = f"{service_name.capitalize()}{schema_name}"
                service_schema_mapping[schema_name] = prefixed_schema_name

            # Luego copiar los schemas actualizando sus referencias internas
            for schema_name, schema_def in service_spec["components"]["schemas"].items():
                prefixed_schema_name = service_schema_mapping[schema_name]
                # Actualizar referencias dentro del schema (por si un schema referencia a otro)
                updated_schema_def = update_schema_refs(schema_def, service_schema_mapping)
                combined_spec["components"]["schemas"][prefixed_schema_name] = updated_schema_def

        # Combinar paths del servicio
        if "paths" in service_spec:
            for path, path_item in service_spec["paths"].items():
                # Los servicios ya tienen sus rutas completas (ej: /v1/users/...)
                # En el gateway queremos mantenerlas igual, sin duplicar el nombre del recurso
                # Ejemplo: /v1/users del servicio → /v1/users en el gateway (NO /v1/users/users)
                gateway_path = path

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
                    # Actualizar todas las referencias $ref en este path
                    filtered_path_item = update_schema_refs(filtered_path_item, service_schema_mapping)
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
