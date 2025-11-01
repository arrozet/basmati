# Servicios en Scaffolding - Guía de Implementación

Este documento es una guía para implementar los servicios que actualmente solo tienen estructura de directorios (scaffolding).

## Servicios Pendientes

- ⚠️ **CalendarService** (Puerto 8002)
- ⚠️ **EventService** (Puerto 8003)
- ⚠️ **NotificationService** (Puerto 8004)
- ⚠️ **SearchService** (Puerto 8005)
- ⚠️ **IntegrationService** (Puerto 8006)

## Estructura de Cada Servicio

Todos los servicios siguen la misma estructura:

```
service_name/
├── main.py                    ✅ Creado (health check básico)
├── Dockerfile                 ✅ Creado
├── requirements.txt           ✅ Creado
├── core/
│   ├── __init__.py           ✅ Creado
│   ├── config.py             ⚠️ TODO
│   └── database.py           ⚠️ TODO
├── models/
│   ├── __init__.py           ✅ Creado
│   └── *.py                  ⚠️ TODO
├── schemas/
│   ├── __init__.py           ✅ Creado
│   ├── common.py             ✅ Creado
│   └── *.py                  ⚠️ TODO
├── services/
│   ├── __init__.py           ✅ Creado
│   └── *_service.py          ⚠️ TODO
└── api/
    ├── __init__.py           ✅ Creado
    └── v1/
        ├── __init__.py       ✅ Creado
        ├── router.py         ⚠️ TODO
        └── endpoints/
            ├── __init__.py   ✅ Creado
            └── *.py          ⚠️ TODO
```

## Ejemplo de Referencia: UserService

El **UserService** está completamente implementado y puede usarse como referencia para:

1. **Configuración** (`core/config.py`):
   - Uso de `pydantic-settings`
   - Variables de entorno
   - Configuración de MongoDB

2. **Conexión a Base de Datos** (`core/database.py`):
   - Cliente asíncrono de Motor
   - Funciones de conexión/desconexión
   - Función `get_database()`

3. **Modelos** (`models/user.py`):
   - PyObjectId personalizado
   - Modelos Pydantic para MongoDB
   - Configuración de serialización

4. **Schemas** (`schemas/user.py`):
   - Schemas para Create, Update, Response
   - Validación con Pydantic
   - EmailStr para emails

5. **Servicios** (`services/user_service.py`):
   - Clase de servicio con lógica de negocio
   - Métodos CRUD completos
   - Búsquedas parametrizadas
   - Conversión de documentos

6. **Endpoints** (`api/v1/endpoints/users.py`):
   - Router de FastAPI
   - Documentación con docstrings
   - Manejo de errores con HTTPException
   - Response models

## Pasos para Implementar un Servicio

### 1. Configuración (`core/config.py`)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_uri: str
    service_port: int = 800X  # Cambiar X por el puerto
    database_name: str = "basmati"
    # Agregar URLs de otros servicios si es necesario
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 2. Database (`core/database.py`)

Copiar la implementación de UserService, es genérica para todos.

### 3. Modelos (`models/*.py`)

Seguir la estructura del schema MongoDB definido en `AGENTS.md`:

```python
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    # Copiar de UserService
    ...

class TuModelo(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    # Campos según AGENTS.md
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
```

### 4. Schemas (`schemas/*.py`)

Crear schemas para:
- `Base` - Campos comunes
- `Create` - Para POST (hereda de Base)
- `Update` - Para PUT (campos opcionales)
- `Response` - Para respuestas (incluye id y timestamps)

### 5. Services (`services/*_service.py`)

Implementar la lógica de negocio:

```python
from motor.motor_asyncio import AsyncIOMotorDatabase

class TuService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["nombre_coleccion"]
    
    async def create_x(self, data: XCreate) -> XResponse:
        # Implementar creación
        ...
    
    async def get_x(self, id: str) -> Optional[XResponse]:
        # Implementar lectura
        ...
    
    # IMPORTANTE: Implementar al menos 2 queries parametrizadas
    async def search_by_field1(self, value: str) -> List[XResponse]:
        ...
    
    async def search_by_field2(self, value: str) -> List[XResponse]:
        ...
```

### 6. Router (`api/v1/router.py`)

```python
from fastapi import APIRouter
from api.v1.endpoints import tu_endpoint

api_router = APIRouter()
api_router.include_router(tu_endpoint.router, prefix="/ruta", tags=["tag"])
```

### 7. Endpoints (`api/v1/endpoints/*.py`)

```python
from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from schemas.tu_schema import *
from services.tu_service import TuService
from core.database import get_database

router = APIRouter()

@router.post("", response_model=XResponse, status_code=status.HTTP_201_CREATED)
async def create_x(data: XCreate):
    """
    Docstring en español explicando la operación.
    
    Args:
        data: Descripción
        
    Returns:
        XResponse: Descripción
        
    Example:
        ```json
        { ejemplo }
        ```
    """
    db = get_database()
    service = TuService(db)
    return await service.create_x(data)

# Implementar todos los endpoints según AGENTS.md
```

### 8. Actualizar main.py

```python
from fastapi import FastAPI
from api.v1.router import api_router
from core.config import settings

app = FastAPI(
    title="Nombre del Servicio",
    description="Descripción",
    version="1.0.0"
)

app.include_router(api_router, prefix="/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "nombre-servicio", "port": settings.service_port}
```

## Requisitos por Servicio

Consultar `AGENTS.md` para:

1. **Endpoints requeridos** de cada servicio
2. **Schemas de MongoDB** (estructura de colecciones)
3. **Variables de entorno** necesarias
4. **Queries parametrizadas** (mínimo 2 por servicio)
5. **Queries relacionales** (cuando aplique)
6. **Comunicación inter-servicios** (con httpx)

## Checklist de Implementación

Para cada servicio, asegurar:

- [ ] `core/config.py` - Configuración con todas las variables necesarias
- [ ] `core/database.py` - Conexión a MongoDB
- [ ] `models/*.py` - Modelos según schema en AGENTS.md
- [ ] `schemas/*.py` - Schemas Create, Update, Response
- [ ] `services/*_service.py` - Lógica de negocio completa
- [ ] Al menos 2 búsquedas parametrizadas
- [ ] Queries relacionales si aplica
- [ ] `api/v1/router.py` - Router configurado
- [ ] `api/v1/endpoints/*.py` - Todos los endpoints requeridos
- [ ] `main.py` - App con router incluido
- [ ] Docstrings en español en todos los métodos
- [ ] Ejemplos en docstrings para Swagger UI
- [ ] Manejo de errores con HTTPException

## Testing

1. **Levantar solo tu servicio:**
   ```bash
   cd tu_servicio
   pip install -r requirements.txt
   uvicorn main:app --reload --port 800X
   ```

2. **Acceder a Swagger UI:**
   ```
   http://localhost:800X/docs
   ```

3. **Probar con Docker Compose:**
   ```bash
   cd ../..
   docker-compose up --build tu-servicio
   ```

## Comunicación Inter-Servicios

Si tu servicio necesita llamar a otro:

```python
import httpx
from core.config import settings

async def call_other_service(data):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.other_service_url}/v1/endpoint",
                json=data
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            # Manejar error
            raise HTTPException(status_code=503, detail=f"Error conectando con servicio: {e}")
```

## Recursos

- **UserService completo:** `../user_service/`
- **Especificaciones:** `../../../AGENTS.md`
- **Docker Compose:** `../docker-compose.yml`
- **Schemas MongoDB:** Ver `AGENTS.md` sección "Database Schema"

## Contacto

Para dudas o coordinación entre equipos, consultar la documentación en `AGENTS.md` o revisar la implementación de referencia en `user_service/`.

---

**Nota:** Este es un proyecto académico. El código debe ser limpio, bien documentado y seguir las convenciones establecidas (snake_case, docstrings en español, código en inglés).
