@echo off
REM =============================================================================
REM Script de despliegue para DESARROLLO (Windows)
REM Levanta el entorno de desarrollo con hot-reload
REM =============================================================================

echo ================================
echo   Basmati - Desarrollo
echo ================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "docker-compose.dev.yml" (
    echo Error: No se encuentra docker-compose.dev.yml
    echo Este script debe ejecutarse desde el directorio app/
    exit /b 1
)

REM Verificar que existe .env
if not exist ".env" (
    echo  No se encuentra el archivo .env
    echo  Copiando .env.example a .env...
    copy .env.example .env
    echo  Por favor, edita .env y configura tu contraseña de MongoDB
    echo.
    pause
)

echo Construyendo imagen de desarrollo...
docker-compose -f docker-compose.dev.yml build

echo.
echo Levantando contenedores...
docker-compose -f docker-compose.dev.yml up -d

echo.
echo Entorno de desarrollo iniciado!
echo.
echo Servicios disponibles:
echo    • API: http://localhost:8000
echo    • Docs (Swagger): http://localhost:8000/docs
echo    • ReDoc: http://localhost:8000/redoc
echo.
echo Comandos útiles:
echo    • Ver logs: docker-compose -f docker-compose.dev.yml logs -f
echo    • Detener: docker-compose -f docker-compose.dev.yml down
echo    • Ejecutar tests: docker-compose -f docker-compose.dev.yml exec backend-api pytest tests/ -v
echo    • Shell: docker-compose -f docker-compose.dev.yml exec backend-api bash
echo.
pause
