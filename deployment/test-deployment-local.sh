#!/bin/bash

##############################################################################
# Basmati - Test de Despliegue Local
#
# Script para probar el despliegue en tu máquina local antes de ir a EC2.
# Simula el proceso de despliegue sin necesidad de un servidor.
#
# Uso: ./test-deployment-local.sh
##############################################################################

set -e

echo "🧪 Test de Despliegue Local - Basmati"
echo "======================================"
echo ""

# Variables
APP_DIR="../app"
ENV_FILE="$APP_DIR/.env"

# Verificar que estamos en el directorio correcto
if [ ! -f "$APP_DIR/docker-compose.yml" ]; then
    echo "❌ Error: No se encuentra docker-compose.yml"
    echo "Ejecuta este script desde el directorio deployment/"
    exit 1
fi

# Verificar Docker
echo "📦 Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker daemon no está corriendo"
    exit 1
fi

echo "✅ Docker está listo"
echo ""

# Verificar .env
echo "🔍 Verificando .env..."
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️  No hay archivo .env, usando valores por defecto"
    echo "Para producción, copia .env.production.template a $APP_DIR/.env"
else
    echo "✅ Archivo .env encontrado"
fi
echo ""

# Detener servicios actuales
echo "⏸️  Deteniendo servicios actuales..."
cd "$APP_DIR"
docker-compose down 2>/dev/null || true
echo ""

# Limpiar (opcional)
read -p "¿Limpiar imágenes antiguas? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 Limpiando..."
    docker system prune -f
fi
echo ""

# Build
echo "🔨 Construyendo imágenes..."
DOCKER_BUILDKIT=1 docker-compose build --parallel || {
    echo "❌ Error en build"
    exit 1
}
echo "✅ Build completado"
echo ""

# Iniciar servicios
echo "🚀 Iniciando servicios..."
docker-compose up -d || {
    echo "❌ Error al iniciar servicios"
    exit 1
}
echo "✅ Servicios iniciados"
echo ""

# Esperar health checks
echo "⏳ Esperando que los servicios estén listos (30s)..."
sleep 30

# Verificar servicios
echo ""
echo "🔍 Verificando servicios..."

services=(
    "8000:API Gateway"
    "8001:User Service"
    "8002:Calendar Service"
    "8003:Event Service"
    "8004:Notification Service"
    "8005:Auth Service"
    "8006:Integration Service"
    "5173:Frontend"
)

failed=()
for service_info in "${services[@]}"; do
    IFS=':' read -r port name <<< "$service_info"
    
    if [ "$port" = "5173" ]; then
        # Frontend solo verificar que responde
        if curl -sf "http://localhost:${port}" &> /dev/null; then
            echo "✅ $name (port $port): OK"
        else
            echo "⚠️  $name (port $port): No responde (puede estar iniciando)"
        fi
    else
        # Backend verificar /health
        if curl -sf "http://localhost:${port}/health" &> /dev/null; then
            echo "✅ $name (port $port): OK"
        else
            echo "❌ $name (port $port): FAIL"
            failed+=("$name")
        fi
    fi
done

echo ""

# Resultado
if [ ${#failed[@]} -eq 0 ]; then
    echo "════════════════════════════════════════"
    echo "✅ ¡Test de Despliegue Exitoso!"
    echo "════════════════════════════════════════"
    echo ""
    echo "🌐 URLs disponibles:"
    echo "  - Frontend:  http://localhost:5173"
    echo "  - API Docs:  http://localhost:8000/docs"
    echo "  - API Gateway: http://localhost:8000"
    echo ""
    echo "📝 Comandos útiles:"
    echo "  - Ver logs:     docker-compose logs -f"
    echo "  - Ver estado:   docker-compose ps"
    echo "  - Detener:      docker-compose down"
    echo ""
    echo "🎉 Todo funciona correctamente!"
    echo "   Ahora puedes desplegar en EC2 con confianza."
    echo ""
else
    echo "════════════════════════════════════════"
    echo "❌ Test Falló"
    echo "════════════════════════════════════════"
    echo ""
    echo "Servicios fallidos: ${failed[*]}"
    echo ""
    echo "🔍 Revisa los logs:"
    echo "  docker-compose logs"
    echo ""
    echo "Para ver logs de un servicio específico:"
    echo "  docker-compose logs ${failed[0],,} | head -50"
    echo ""
    exit 1
fi
