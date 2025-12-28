#!/bin/bash

##############################################################################
# Basmati - Quick Deploy Script
#
# Script simplificado para desarrollo/testing rápido.
# NO usar en producción - usar deploy.sh para producción.
#
# Uso: ./quick-deploy.sh
##############################################################################

set -e

cd "$(dirname "$0")/../app"

echo "🚀 Quick Deploy - Basmati"
echo ""

# Detener servicios
echo "⏸️  Deteniendo servicios..."
docker-compose down 2>/dev/null || true

# Build rápido
echo "🔨 Construyendo imágenes..."
DOCKER_BUILDKIT=1 docker-compose build --parallel

# Iniciar
echo "▶️  Iniciando servicios..."
docker-compose up -d

# Esperar health checks
echo "⏳ Esperando servicios..."
sleep 10

# Verificar
echo ""
echo "✅ Estado de servicios:"
docker-compose ps

echo ""
echo "🌐 URLs disponibles:"
echo "  - API Gateway: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Frontend: http://localhost:5173"

echo ""
echo "📝 Ver logs: docker-compose logs -f"
