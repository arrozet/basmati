# Basmati

Plataforma de microservicios construida con Docker Compose, FastAPI y MongoDB.

## Estructura del Proyecto

```
app/
├── start-dev.sh                # Script de inicio para desarrollo (Linux/Mac)
├── start-dev.bat               # Script de inicio para desarrollo (Windows)
├── deploy.sh                   # Script de inicio para producción 
├── docker-compose.yml          # Configuración de producción
├── docker-compose.dev.yml      # Configuración de desarrollo
├── .env                        # Variables de entorno (no versionado)
├── .env.example                # Plantilla de variables de entorno
├── .gitignore                  # Archivos ignorados por git
└── backend-api/                # Microservicio FastAPI
    ├── Dockerfile              # Imagen optimizada para producción
    ├── Dockerfile.dev          # Imagen para desarrollo
    ├── requirements.txt        # Dependencias de producción
    ├── requirements-dev.txt    # Dependencias de desarrollo
    ├── main.py                 # Aplicación principal
    ├── config.py               # Configuración
    ├── database.py             # Gestión de MongoDB
    └── tests/                  # Tests y configuración de testing
```

## Microservicios

### Backend API (FastAPI)
- **Puerto**: 8000
- **Tecnologías**: FastAPI, MongoDB (Motor), Pydantic
- **Descripción**: API REST principal con conexión asíncrona a MongoDB

## Requisitos Previos

- Docker (>= 20.10)
- Docker Compose (>= 2.0)

## Configuración Inicial

Configura el archivo `.env`:

```
# MongoDB Configuration
MONGODB_URL=<URL>
MONGODB_DB_NAME=<NOMBRE_BASE_DE_DATOS>

# Backend API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Environment
ENVIRONMENT=development
```

### Desarrollo (Recomendado para desarrollo local)

**Linux/Mac:**
```bash
./start-dev.sh
```

**Windows:**
```cmd
start-dev.bat
```

**Docker Compose directo:**
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### Producción

**Linux/Mac:**
```bash
./start-prod.sh
```

**Windows:**
```cmd
start-prod.bat
```

**Docker Compose directo:**
```bash
docker-compose up -d
```

### Detener Servicios

**Linux/Mac:**
```bash
./stop.sh
```

**Windows:**
```cmd
stop.bat
```

**Docker Compose directo:**
```bash
# Desarrollo
docker-compose -f docker-compose.dev.yml down

# Producción
docker-compose down
```

## Acceso a los Servicios

- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Entornos

### Desarrollo

**Características:**
- Hot-reload activado (cambios en código se reflejan inmediatamente)
- Volúmenes montados para sincronización de código
- Dependencias de testing incluidas
- Logging detallado
- Usuario root en contenedor

**Dockerfile**: `Dockerfile.dev`

**Dependencias**: Base + Testing (pytest, httpx, etc.)

### Producción

**Características:**
- Imagen optimizada mediante multi-stage build
- Código embebido (sin volúmenes)
- Usuario no-root para mayor seguridad
- Health checks configurados
- Solo dependencias necesarias
- Sin hot-reload

**Dockerfile**: `Dockerfile`

**Dependencias**: Solo base (FastAPI, Motor, etc.)

## Comandos Útiles

### Ver Logs

```bash
# Desarrollo
docker-compose -f docker-compose.dev.yml logs -f

# Producción
docker-compose logs -f

# Solo backend-api
docker-compose -f docker-compose.dev.yml logs -f backend-api
```

### Acceder al Contenedor

```bash
# Desarrollo
docker-compose -f docker-compose.dev.yml exec backend-api bash

# Producción
docker-compose exec backend-api bash
```

### Reconstruir Imágenes

```bash
# Desarrollo
docker-compose -f docker-compose.dev.yml up --build

# Producción
docker-compose up --build
```

### Reiniciar Servicios

```bash
# Desarrollo
docker-compose -f docker-compose.dev.yml restart

# Producción
docker-compose restart
```

## Testing

### Ejecutar Tests

**Desde Docker (Desarrollo):**
```bash
docker-compose -f docker-compose.dev.yml exec backend-api pytest tests/ -v
```

**Con Cobertura:**
```bash
docker-compose -f docker-compose.dev.yml exec backend-api pytest tests/ --cov=. --cov-report=html -v
```

**Local:**
```bash
cd backend-api/tests
./run_tests.sh
```

Ver más detalles en `backend-api/tests/README.md`.

## Herramientas de Desarrollo

Las herramientas de calidad de código se ejecutan localmente para mayor velocidad.

### Instalación Local

```bash
pip install black flake8 mypy isort
```

### Formatear Código

```bash
black backend-api/
```

### Linting

```bash
flake8 backend-api/ --exclude=__pycache__,venv,htmlcov
```

### Type Checking

```bash
mypy backend-api/ --ignore-missing-imports
```

### Ordenar Imports

```bash
isort backend-api/
```

## Comparación de Entornos

| Característica | Desarrollo | Producción |
|----------------|------------|------------|
| Dockerfile | `Dockerfile.dev` | `Dockerfile` |
| Compose | `docker-compose.dev.yml` | `docker-compose.yml` |
| Hot-reload | Sí | No |
| Volúmenes | Sí (código sincronizado) | No (código embebido) |
| Tests | Incluidos | No |
| Dev tools | Local (black, flake8, mypy) | No |
| Build | Simple | Multi-stage |
| Usuario | root | no-root (appuser) |
| Health checks | No | Sí |
| Tamaño imagen | ~350MB | ~200MB |
| Dependencias | Base + Testing | Solo Base |

## Troubleshooting

### Error: "Cannot connect to MongoDB"
- Verifica que la contraseña en `.env` es correcta
- Verifica que tu IP tiene acceso en MongoDB Atlas Network Access
- Verifica la conectividad: `curl https://basmaticluster.revmyok.mongodb.net`

### Error: "Port 8000 already in use"
- Detén otros servicios en el puerto 8000
- Cambia el puerto en `docker-compose.yml` o `docker-compose.dev.yml`

### Los cambios no se reflejan en desarrollo
- Verifica que estás usando `docker-compose.dev.yml`
- Verifica que los volúmenes están montados correctamente
- Reinicia el contenedor: `docker-compose -f docker-compose.dev.yml restart`

### Error al ejecutar tests
- Verifica que estás usando el entorno de desarrollo
- Instala dependencias: `docker-compose -f docker-compose.dev.yml exec backend-api pip install -r requirements-dev.txt`

## Documentación Adicional

- **Backend API**: Ver `backend-api/README.md`
- **Tests**: Ver `backend-api/tests/README.md`

## Próximos Pasos

- Agregar más microservicios al `docker-compose.yml`
- Implementar autenticación JWT
- Configurar CI/CD
- Agregar cache con Redis
- Implementar rate limiting
- Configurar logging centralizado

## Microservicios

### Backend API (FastAPI)
- **Puerto**: 8000
- **Descripción**: API REST principal con FastAPI y MongoDB

## Requisitos Previos

- Docker
- Docker Compose

## Configuración

1. Copia el archivo `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edita `.env` y reemplaza `<db_password>` con la contraseña real de MongoDB.

## Entornos

### 🔧 DESARROLLO (Recomendado para desarrollo local)

**Características:**
- ✅ Hot-reload activado
- ✅ Volúmenes montados (cambios en vivo)
- ✅ Herramientas de desarrollo (pytest, black, flake8, mypy)
- ✅ Logging detallado

**Usar con:**
```bash
# Opción 1: Usando el script de ayuda (RECOMENDADO)
./dev.sh

# Opción 2: Docker Compose directo
docker-compose -f docker-compose.dev.yml up

# En segundo plano
docker-compose -f docker-compose.dev.yml up -d

# Reconstruir
docker-compose -f docker-compose.dev.yml up --build

# Detener
docker-compose -f docker-compose.dev.yml down
```

### 🚀 PRODUCCIÓN (Para deployment)

**Características:**
- ✅ Imagen optimizada (multi-stage build)
- ✅ Sin herramientas de desarrollo
- ✅ Usuario no-root (seguridad)
- ✅ Health checks
- ✅ Código embebido (no volúmenes)

**Usar con:**
```bash
# Levantar
docker-compose up -d

# Detener
docker-compose down

# Reconstruir
docker-compose up --build -d
```

## Script de Desarrollo (dev.sh)

Script interactivo con menú para tareas comunes:

```bash
./dev.sh
```

**Opciones disponibles:**
1. Start development environment
2. Stop development environment
3. Rebuild development environment
4. Run tests
5. Run tests with coverage
6. Format code (black)
7. Lint code (flake8)
8. Type check (mypy)
9. View logs
10. Shell into container
11. Start production environment
12. Stop production environment

## Acceso a los Servicios

- **Backend API**: http://localhost:8000
- **Documentación API (Swagger)**: http://localhost:8000/docs
- **Documentación API (ReDoc)**: http://localhost:8000/redoc

## Desarrollo

En desarrollo, los cambios en el código se reflejan automáticamente (hot-reload).

### Comandos útiles en desarrollo

```bash
# Ver logs en tiempo real
docker-compose -f docker-compose.dev.yml logs -f backend-api

# Acceder al shell del contenedor
docker-compose -f docker-compose.dev.yml exec backend-api bash

# Reiniciar un servicio
docker-compose -f docker-compose.dev.yml restart backend-api
```

## Testing

### Ejecutar tests del backend
```bash
# Usando el script de desarrollo
./dev.sh
# Luego selecciona opción 4 o 5

# O directamente
docker-compose -f docker-compose.dev.yml exec backend-api pytest -v

# Con coverage
docker-compose -f docker-compose.dev.yml exec backend-api pytest --cov=. --cov-report=html -v
```

## Herramientas de Desarrollo

Las herramientas de calidad de código (formateo, linting, type checking) se ejecutan **localmente** para mayor velocidad:

```bash
# Instalar herramientas localmente (una vez)
pip install black flake8 mypy isort

# Formatear código
black backend-api/

# Linting
flake8 backend-api/ --exclude=__pycache__,venv,htmlcov

# Type checking
mypy backend-api/ --ignore-missing-imports

# Ordenar imports
isort backend-api/
```

## Comparación de Entornos

| Característica | Desarrollo | Producción |
|----------------|------------|------------|
| Dockerfile | `Dockerfile.dev` | `Dockerfile` |
| docker-compose | `docker-compose.dev.yml` | `docker-compose.yml` |
| Hot-reload | ✅ Sí | ❌ No |
| Volúmenes | ✅ Sí | ❌ No |
| Tests | ✅ Incluidos | ❌ No |
| Dev tools | 💻 Local (black, flake8, mypy) | ❌ No |
| Tamaño imagen | � Mediana | 🟢 Pequeña |
| Build | 🟡 Simple | 🟢 Multi-stage |
| Seguridad | 🟡 Root user | 🟢 Non-root user |
| Health checks | ❌ No | ✅ Sí |
| Dependencias | Base + Tests | Solo Base |
