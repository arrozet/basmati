#!/bin/bash
# =============================================================================
# Script de Redespliegue de Basmati
# =============================================================================
# Este script reconstruye y redespliega la aplicación con las nuevas
# configuraciones de CORS y el frontend de producción.
#
# Uso:
#   ./redeploy.sh
# =============================================================================

set -e  # Salir si hay algún error

echo "🚀 Iniciando redespliegue de Basmati..."
echo ""

# Cambiar al directorio app
cd /home/drlk/basmati/app || exit 1

echo "📋 Verificando archivo .env..."
if [ ! -f .env ]; then
    echo "❌ Error: No se encontró el archivo .env en /home/drlk/basmati/app"
    exit 1
fi

# Mostrar configuración de CORS
echo "🔧 Configuración de CORS:"
grep "CORS_ORIGINS" .env || echo "   No configurado (usará *)"
echo ""

# Detener contenedores existentes
echo "🛑 Deteniendo contenedores existentes..."
docker-compose -f docker-compose.yml -f /home/drlk/basmati/deployment/docker-compose.prod.yml down

# Eliminar imágenes antiguas del frontend y api-gateway (para forzar rebuild)
echo "🗑️  Eliminando imágenes antiguas..."
docker rmi app-frontend:latest 2>/dev/null || true
docker rmi app-api-gateway:latest 2>/dev/null || true
docker rmi app-auth-service:latest 2>/dev/null || true

# Rebuild con no-cache para frontend y api-gateway
echo "🔨 Reconstruyendo servicios..."
docker-compose -f docker-compose.yml -f /home/drlk/basmati/deployment/docker-compose.prod.yml build --no-cache frontend api-gateway auth-service

# Levantar todos los servicios
echo "🚀 Levantando servicios..."
docker-compose -f docker-compose.yml -f /home/drlk/basmati/deployment/docker-compose.prod.yml up -d

# Esperar a que los servicios estén listos
echo ""
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

# Verificar estado
echo ""
echo "📊 Estado de los servicios:"
docker-compose -f docker-compose.yml -f /home/drlk/basmati/deployment/docker-compose.prod.yml ps

echo ""
echo "✅ Redespliegue completado!"
echo ""
echo "🔍 Para ver los logs:"
echo "   docker-compose -f docker-compose.yml -f /home/drlk/basmati/deployment/docker-compose.prod.yml logs -f"
echo ""
echo "🌐 URLs:"
echo "   Frontend: https://basmati.app"
echo "   API Gateway: https://basmati.app/api"
echo "   API Docs: https://basmati.app/api/docs"
