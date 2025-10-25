# Backend API - FastAPI Microservice

Microservicio backend con FastAPI, MongoDB y arquitectura por capas siguiendo las mejores prácticas de desarrollo.

## Características

- **FastAPI**: Framework web moderno y de alto rendimiento
- **MongoDB**: Base de datos NoSQL con Motor (driver asíncrono)
- **Arquitectura por capas**: Separación clara de responsabilidades
- **Versionado de API**: Sistema de versiones por URL (`/api/v1/`)
- **Validación**: Automática con Pydantic schemas
- **Documentación**: Generada automáticamente (Swagger + ReDoc)
- **Async**: Código completamente asíncrono
- **Tests**: Suite completa con pytest
- **Type hints**: Tipado estático en todo el código
- **Docker**: Configuraciones separadas para desarrollo y producción

## Estructura del Proyecto

```
backend-api/
├── api/                        # Capa de API (endpoints HTTP)
│   └── v1/                     # Versión 1 de la API
│       ├── endpoints/          # Endpoints por recurso
│       │   └── users.py        # CRUD completo de usuarios
│       └── router.py           # Router principal v1
│
├── core/                       # Núcleo de la aplicación
│   ├── config.py               # Configuración (variables de entorno)
│   └── database.py             # Gestión de conexión a MongoDB
│
├── models/                     # Modelos de dominio
│   └── user.py                 # Modelo de usuario
│
├── schemas/                    # Schemas de Pydantic (validación I/O)
│   ├── common.py               # Schemas comunes
│   └── user.py                 # Schemas de usuario
│
├── services/                   # Lógica de negocio
│   └── user_service.py         # Servicio de usuarios
│
├── utils/                      # Utilidades
│   └── security.py             # Funciones de seguridad
│
├── tests/                      # Tests
│   ├── conftest.py             # Configuración pytest
│   ├── pytest.ini              # Config pytest
│   ├── run_tests.sh            # Script de tests
│   └── test_database.py        # Tests de BD
│
├── main.py                     # Aplicación FastAPI principal
├── Dockerfile                  # Imagen de producción
├── Dockerfile.dev              # Imagen de desarrollo
├── requirements.txt            # Dependencias de producción
├── requirements-dev.txt        # Dependencias de desarrollo
├── ARCHITECTURE.md             # Documentación detallada de arquitectura
├── API.md                      # Guía de uso de la API
└── README.md                   # Esta documentación
```

## Arquitectura por Capas

### 1. API Layer (`api/`)
- Define endpoints HTTP
- Maneja requests/responses
- Validación de entrada (Pydantic)
- Documentación de endpoints

### 2. Service Layer (`services/`)
- Lógica de negocio
- Validaciones de negocio
- Orquestación de operaciones
- Independiente de HTTP

### 3. Model Layer (`models/`)
- Modelos de dominio
- Estructura de datos
- Conversiones (to_dict, from_dict)

### 4. Schema Layer (`schemas/`)
- Validación con Pydantic
- DTOs (Data Transfer Objects)
- Documentación automática
- Ejemplos para OpenAPI

### 5. Core Layer (`core/`)
- Configuración centralizada
- Gestión de base de datos
- Funcionalidad compartida

Ver [ARCHITECTURE.md](./ARCHITECTURE.md) para más detalles.

## API Versionada

### Estrategia: URL Path Versioning

**Formato**: `/api/v{version}/{resource}`

**Ejemplo**: `/api/v1/users/`

### Ventajas
- Claridad en la versión
- Múltiples versiones pueden coexistir
- Fácil de documentar y navegar
- Permite migración gradual

## Ejemplo: CRUD de Usuarios

### Endpoints Disponibles

```
POST   /api/v1/users/                    # Crear usuario
GET    /api/v1/users/                    # Listar usuarios (paginado)
GET    /api/v1/users/{user_id}           # Obtener usuario
PUT    /api/v1/users/{user_id}           # Actualizar usuario
DELETE /api/v1/users/{user_id}           # Eliminar usuario
GET    /api/v1/users/email/{email}       # Buscar por email
GET    /api/v1/users/username/{username} # Buscar por username
```

### Crear Usuario

```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "john_doe",
    "full_name": "John Doe",
    "password": "SecurePass123!"
  }'
```

Ver [API.md](./API.md) para guía completa de uso.

## Tecnologías

### Dependencias de Producción
- **FastAPI** (0.109.0): Framework web
- **Uvicorn** (0.27.0): Servidor ASGI
- **Motor** (3.4.0): Driver async de MongoDB
- **PyMongo** (4.6.3): Driver de MongoDB
- **Pydantic** (2.5.3): Validación de datos
- **python-dotenv** (1.0.0): Variables de entorno

### Dependencias de Desarrollo
- **pytest** (7.4.3): Framework de testing
- **pytest-asyncio** (0.21.1): Tests asíncronos
- **pytest-cov** (4.1.0): Cobertura de código
- **httpx** (0.26.0): Cliente HTTP para tests

## Configuración

### Variables de Entorno

Archivo `.env` en la raíz del proyecto:

```env
# MongoDB
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=basmati_db

# API
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Environment
ENVIRONMENT=development
```

## Desarrollo

### Con Docker (Recomendado)

Desde la raíz del proyecto:

```bash
# Desarrollo (con hot-reload)
docker-compose -f docker-compose.dev.yml up

# Producción
docker-compose up
```

### Sin Docker

Requiere Python 3.11+:

```bash
# Instalar dependencias
pip install -r requirements-dev.txt

# Ejecutar
python main.py

# O con uvicorn
uvicorn main:app --reload
```

## Testing

```bash
# Con Docker
docker-compose -f docker-compose.dev.yml exec backend-api pytest tests/ -v

# Con coverage
docker-compose -f docker-compose.dev.yml exec backend-api pytest tests/ --cov=. --cov-report=html -v

# Local
cd tests
./run_tests.sh
```

Ver [tests/README.md](./tests/README.md) para más información.

## Documentación

### Documentación Interactiva

Una vez iniciado el servidor:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Documentación Adicional

- **[ARCHITECTURE.md](./ARCHITECTURE.md)**: Arquitectura detallada, patrones y flujos
- **[API.md](./API.md)**: Guía completa de uso de la API con ejemplos
- **[tests/README.md](./tests/README.md)**: Documentación de tests

## Mejores Prácticas Implementadas

### Arquitectura
- Separación de capas (API, Service, Model, Schema)
- Dependency Injection
- Repository Pattern (en services)
- DTOs con Pydantic

### Código
- Async/await en todo el código
- Type hints completos
- Docstrings en funciones y clases
- Validación automática con Pydantic

### API
- Versionado por URL
- Paginación en listados
- Códigos HTTP apropiados
- Manejo consistente de errores
- Documentación automática

### Datos
- Validación de entrada
- Serialización automática
- ObjectId a string para JSON
- Timestamps automáticos

### Seguridad
- Hashing de contraseñas
- Validación de datos
- CORS configurado
- Variables de entorno para secrets

## Agregar Nuevos Recursos

### 1. Crear Modelo

```python
# models/product.py
class ProductModel:
    collection_name = "products"
    
    def __init__(self, name, price, ...):
        self.name = name
        self.price = price
```

### 2. Crear Schemas

```python
# schemas/product.py
class ProductCreate(BaseModel):
    name: str
    price: float

class ProductResponse(BaseModel):
    id: str
    name: str
    price: float
```

### 3. Crear Servicio

```python
# services/product_service.py
class ProductService:
    async def create_product(self, data: ProductCreate):
        ...
```

### 4. Crear Endpoints

```python
# api/v1/endpoints/products.py
router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/")
async def create_product(...):
    ...
```

### 5. Registrar en Router

```python
# api/v1/router.py
from api.v1.endpoints import users, products

api_router.include_router(users.router)
api_router.include_router(products.router)
```

## Próximos Pasos

### Funcionalidad
- [ ] Autenticación JWT
- [ ] Autorización (roles y permisos)
- [ ] Más recursos (products, orders, etc.)
- [ ] Filtros avanzados en listados
- [ ] Búsqueda full-text

### Infraestructura
- [ ] Cache con Redis
- [ ] Rate limiting
- [ ] Logging estructurado
- [ ] Métricas (Prometheus)
- [ ] Tracing distribuido

### Calidad
- [ ] Más tests (unit + integration)
- [ ] CI/CD pipeline
- [ ] Pre-commit hooks
- [ ] Code quality checks automatizados

### Seguridad
- [ ] HTTPS/TLS
- [ ] API Keys
- [ ] Auditoría de logs
- [ ] Encriptación de datos sensibles

## Recursos

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Motor Documentation](https://motor.readthedocs.io/)
- [MongoDB Best Practices](https://www.mongodb.com/docs/manual/administration/production-notes/)
- [REST API Best Practices](https://restfulapi.net/)
