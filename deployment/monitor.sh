#!/bin/bash

##############################################################################
# Basmati - Monitor de Servicios
#
# Verifica el estado de todos los servicios y muestra métricas.
#
# Uso: ./monitor.sh
##############################################################################

echo "📊 Basmati - Monitor de Servicios"
echo "=================================="
echo ""

# Verificar que Docker está corriendo
if ! docker info &> /dev/null; then
    echo "❌ Docker no está corriendo"
    exit 1
fi

cd /opt/basmati/app

# Estado de contenedores
echo "🐳 Estado de Contenedores:"
echo "-------------------------"
docker-compose ps
echo ""

# Health checks
echo "❤️  Health Checks:"
echo "-------------------------"

services=(
    "8000:API Gateway"
    "8001:User Service"
    "8002:Calendar Service"
    "8003:Event Service"
    "8004:Notification Service"
    "8005:Auth Service"
    "8006:Integration Service"
)

for service in "${services[@]}"; do
    IFS=':' read -r port name <<< "$service"
    
    if curl -sf "http://localhost:${port}/health" &> /dev/null; then
        echo "✅ $name (port $port): OK"
    else
        echo "❌ $name (port $port): FAIL"
    fi
done

echo ""

# Uso de recursos
echo "💻 Uso de Recursos:"
echo "-------------------------"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

echo ""

# Espacio en disco
echo "💾 Espacio en Disco:"
echo "-------------------------"
df -h / | tail -n 1

echo ""

# Uptime de contenedores
echo "⏱️  Uptime:"
echo "-------------------------"
docker-compose ps --format "table {{.Service}}\t{{.Status}}"

echo ""
echo "=================================="
echo "📝 Ver logs: docker-compose logs -f"
echo "🔄 Reiniciar: sudo bash /opt/basmati/deployment/deploy.sh"
