"""Repository para caché de geocodificación - Acceso a BD"""
from datetime import datetime, timezone, timedelta
from typing import Any
import hashlib


class GeocodeCacheRepository:
    """
    Repository para operaciones de caché de geocodificación.
    
    Gestiona el almacenamiento y recuperación de resultados de geocodificación
    en MongoDB para evitar llamadas repetidas a la API de Nominatim.
    
    El caché utiliza TTL (Time To Live) para expiración automática y
    mantiene estadísticas de uso para optimización.
    """
    
    # Tiempo de vida del caché por defecto: 7 días
    DEFAULT_TTL_DAYS = 7
    
    # Nombre de la colección en MongoDB
    COLLECTION_NAME = "geocode_cache"

    def __init__(self, db: Any):
        """
        Inicializa el repository de caché de geocodificación.
        
        Args:
            db: Instancia de la base de datos MongoDB (AsyncIOMotorDatabase)
        """
        self.collection = db[self.COLLECTION_NAME]
    
    async def ensure_indexes(self) -> None:
        """
        Crea los índices necesarios para la colección de caché.
        
        Incluye:
        - Índice único en cache_key para búsquedas rápidas
        - Índice TTL en expires_at para limpieza automática
        - Índice en query_type para estadísticas
        """
        # Índice único en cache_key para búsquedas O(1)
        await self.collection.create_index(
            "cache_key", 
            unique=True, 
            name="idx_cache_key_unique"
        )
        
        # Índice TTL para expiración automática (MongoDB elimina documentos expirados)
        await self.collection.create_index(
            "expires_at",
            expireAfterSeconds=0,
            name="idx_ttl_expiration"
        )
        
        # Índice en query_type para estadísticas y consultas por tipo
        await self.collection.create_index(
            "query_type",
            name="idx_query_type"
        )
    
    @staticmethod
    def generate_cache_key(query_type: str, params: dict) -> str:
        """
        Genera una clave única para identificar una consulta en el caché.
        
        Utiliza SHA-256 para crear un hash determinístico de los parámetros,
        asegurando que consultas idénticas generen la misma clave.
        
        Args:
            query_type: Tipo de consulta ("geocode", "reverse", "search")
            params: Diccionario con los parámetros de la consulta
            
        Returns:
            str: Clave única en formato "tipo:hash"
        """
        # Ordenar parámetros para consistencia
        sorted_params = sorted(params.items())
        params_str = str(sorted_params)
        
        # Generar hash SHA-256
        hash_value = hashlib.sha256(params_str.encode()).hexdigest()[:16]
        
        return f"{query_type}:{hash_value}"
    
    async def get(self, cache_key: str) -> dict | None:
        """
        Obtiene un resultado del caché por su clave.
        
        Si encuentra el resultado, actualiza el contador de accesos
        y la fecha de último acceso.
        
        Args:
            cache_key: Clave única de la consulta
            
        Returns:
            dict: Datos de respuesta cacheados o None si no existe/expiró
        """
        try:
            # Buscar y actualizar estadísticas atómicamente
            result = await self.collection.find_one_and_update(
                {
                    "cache_key": cache_key,
                    "expires_at": {"$gt": datetime.now(timezone.utc)}
                },
                {
                    "$inc": {"hit_count": 1},
                    "$set": {"last_accessed": datetime.now(timezone.utc)}
                },
                return_document=True
            )
            
            if result:
                return result.get("response_data")
            return None
            
        except Exception:
            return None
    
    async def set(
        self,
        query_type: str,
        query_params: dict,
        response_data: dict,
        ttl_days: int | None = None
    ) -> bool:
        """
        Almacena un resultado en el caché.
        
        Utiliza upsert para actualizar si ya existe o crear si es nuevo.
        
        Args:
            query_type: Tipo de consulta ("geocode", "reverse", "search")
            query_params: Parámetros originales de la consulta
            response_data: Respuesta de la API a cachear
            ttl_days: Días de vida del caché (default: 7 días)
            
        Returns:
            bool: True si se almacenó correctamente
        """
        if ttl_days is None:
            ttl_days = self.DEFAULT_TTL_DAYS
        
        cache_key = self.generate_cache_key(query_type, query_params)
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=ttl_days)
        
        try:
            cache_doc = {
                "cache_key": cache_key,
                "query_type": query_type,
                "query_params": query_params,
                "response_data": response_data,
                "created_at": now,
                "expires_at": expires_at,
                "hit_count": 0,
                "last_accessed": now,
                "schema_version": 1
            }
            
            # Upsert: actualiza si existe, crea si no
            await self.collection.update_one(
                {"cache_key": cache_key},
                {"$set": cache_doc},
                upsert=True
            )
            return True
            
        except Exception:
            return False
    
    async def get_or_none(self, query_type: str, query_params: dict) -> dict | None:
        """
        Busca en caché usando tipo y parámetros directamente.
        
        Método de conveniencia que genera la clave automáticamente.
        
        Args:
            query_type: Tipo de consulta
            query_params: Parámetros de la consulta
            
        Returns:
            dict: Datos cacheados o None
        """
        cache_key = self.generate_cache_key(query_type, query_params)
        return await self.get(cache_key)
    
    async def delete(self, cache_key: str) -> bool:
        """
        Elimina una entrada específica del caché.
        
        Args:
            cache_key: Clave de la entrada a eliminar
            
        Returns:
            bool: True si se eliminó
        """
        try:
            result = await self.collection.delete_one({"cache_key": cache_key})
            return result.deleted_count > 0
        except Exception:
            return False
    
    async def clear_expired(self) -> int:
        """
        Limpia manualmente las entradas expiradas.
        
        Nota: MongoDB hace esto automáticamente con el índice TTL,
        pero este método permite limpieza manual si es necesario.
        
        Returns:
            int: Número de entradas eliminadas
        """
        try:
            result = await self.collection.delete_many({
                "expires_at": {"$lt": datetime.now(timezone.utc)}
            })
            return result.deleted_count
        except Exception:
            return 0
    
    async def clear_all(self) -> int:
        """
        Limpia todo el caché.
        
        Útil para forzar recarga de datos frescos.
        
        Returns:
            int: Número de entradas eliminadas
        """
        try:
            result = await self.collection.delete_many({})
            return result.deleted_count
        except Exception:
            return 0
    
    async def get_stats(self) -> dict:
        """
        Obtiene estadísticas del caché.
        
        Returns:
            dict: Estadísticas incluyendo total de entradas, hits, etc.
        """
        try:
            # Contar total de entradas
            total = await self.collection.count_documents({})
            
            # Contar por tipo de consulta
            pipeline = [
                {"$group": {
                    "_id": "$query_type",
                    "count": {"$sum": 1},
                    "total_hits": {"$sum": "$hit_count"}
                }}
            ]
            
            type_stats = {}
            async for doc in self.collection.aggregate(pipeline):
                type_stats[doc["_id"]] = {
                    "count": doc["count"],
                    "total_hits": doc["total_hits"]
                }
            
            # Calcular total de hits
            total_hits = sum(s["total_hits"] for s in type_stats.values())
            
            return {
                "total_entries": total,
                "total_hits": total_hits,
                "by_type": type_stats,
                "ttl_days": self.DEFAULT_TTL_DAYS
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "total_entries": 0,
                "total_hits": 0,
                "by_type": {}
            }

