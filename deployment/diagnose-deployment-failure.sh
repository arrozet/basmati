#!/bin/bash

##############################################################################
# Basmati - Diagnóstico de Fallos de Despliegue
#
# Script para diagnosticar por qué fallan los health checks durante el
# despliegue y proporcionar información detallada del problema.
#
# Uso: ./diagnose-deployment-failure.sh
##############################################################################

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "╔════════════════════════════════════════════════════════╗"
echo "║   Basmati - Diagnóstico de Fallos                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Cambiar al directorio de la app
DEPLOY_DIR="${DEPLOY_DIR:-/opt/basmati}"
APP_DIR="$DEPLOY_DIR/app"

if [ ! -d "$APP_DIR" ]; then
    APP_DIR="$(pwd)/../app"
fi

if [ ! -f "$APP_DIR/docker-compose.yml" ]; then
    log_error "No se encuentra docker-compose.yml"
    exit 1
fi

cd "$APP_DIR"

# 1. Estado de los contenedores
echo "════════════════════════════════════════════════════════"
log_info "1. Estado de Contenedores"
echo "════════════════════════════════════════════════════════"
docker-compose ps
echo ""

# 2. Verificar que los contenedores están corriendo
log_info "Verificando contenedores en ejecución..."
running_containers=$(docker-compose ps -q | wc -l)
if [ "$running_containers" -eq 0 ]; then
    log_error "No hay contenedores en ejecución"
    log_info "Intenta: docker-compose up -d"
    exit 1
else
    log_success "$running_containers contenedores en ejecución"
fi
echo ""

# 3. Verificar conectividad a puertos
echo "════════════════════════════════════════════════════════"
log_info "2. Verificación de Puertos"
echo "════════════════════════════════════════════════════════"

services=(
    "8000|API Gateway"
    "8001|User Service"
    "8002|Calendar Service"
    "8003|Event Service"
    "8004|Notification Service"
    "8005|Auth Service"
    "8006|Integration Service"
)

for service in "${services[@]}"; do
    IFS='|' read -r port name <<< "$service"
    
    if nc -z localhost "$port" 2>/dev/null; then
        log_success "$name - Puerto $port: ABIERTO"
    else
        log_error "$name - Puerto $port: CERRADO"
    fi
done
echo ""

# 4. Health check individual
echo "════════════════════════════════════════════════════════"
log_info "3. Health Checks HTTP"
echo "════════════════════════════════════════════════════════"

for service in "${services[@]}"; do
    IFS='|' read -r port name <<< "$service"
    url="http://localhost:${port}/health"
    
    response=$(curl -s -w "\n%{http_code}" "$url" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        log_success "$name: HTTP $http_code"
    else
        log_error "$name: HTTP $http_code"
        if [ -n "$body" ]; then
            echo "  Response: $body"
        fi
    fi
done
echo ""

# 5. Logs de errores recientes
echo "════════════════════════════════════════════════════════"
log_info "4. Errores Recientes en Logs (últimos 20 líneas)"
echo "════════════════════════════════════════════════════════"

for service in api-gateway user-service calendar-service event-service notification-service auth-service integration-service; do
    echo ""
    log_info "--- $service ---"
    docker-compose logs --tail=20 "$service" 2>&1 | grep -i "error\|exception\|failed\|traceback" || echo "  No hay errores evidentes"
done
echo ""

# 6. Conectividad a MongoDB
echo "════════════════════════════════════════════════════════"
log_info "5. Verificación de MongoDB"
echo "════════════════════════════════════════════════════════"

mongo_test=$(docker-compose exec -T user-service python -c "
import os
from pymongo import MongoClient
try:
    uri = os.getenv('MONGO_URI')
    if not uri:
        print('ERROR: MONGO_URI no configurado')
        exit(1)
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    info = client.server_info()
    print(f'OK: Conectado a MongoDB {info[\"version\"]}')
    exit(0)
except Exception as e:
    print(f'ERROR: {str(e)}')
    exit(1)
" 2>&1)

if echo "$mongo_test" | grep -q "^OK:"; then
    log_success "$mongo_test"
else
    log_error "$mongo_test"
fi
echo ""

# 7. Variables de entorno críticas
echo "════════════════════════════════════════════════════════"
log_info "6. Variables de Entorno Críticas"
echo "════════════════════════════════════════════════════════"

check_env_var() {
    local service=$1
    local var=$2
    
    value=$(docker-compose exec -T "$service" printenv "$var" 2>/dev/null || echo "NOT_SET")
    
    if [ "$value" = "NOT_SET" ] || [ -z "$value" ]; then
        log_error "$service: $var no configurado"
    else
        # Ocultar valor sensible
        masked_value=$(echo "$value" | head -c 20)
        if [ ${#value} -gt 20 ]; then
            masked_value="${masked_value}..."
        fi
        log_success "$service: $var = $masked_value"
    fi
}

check_env_var "user-service" "MONGO_URI"
check_env_var "api-gateway" "USER_SERVICE_URL"
check_env_var "auth-service" "GOOGLE_CLIENT_ID"
check_env_var "integration-service" "AWS_ACCESS_KEY_ID"
echo ""

# 8. Uso de recursos
echo "════════════════════════════════════════════════════════"
log_info "7. Uso de Recursos"
echo "════════════════════════════════════════════════════════"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
echo ""

# 9. Espacio en disco
log_info "Espacio en disco:"
df -h / | grep -E '^Filesystem|/$'
echo ""

# 10. Logs completos del servicio que más falla
echo "════════════════════════════════════════════════════════"
log_info "8. Logs Completos del API Gateway (últimas 50 líneas)"
echo "════════════════════════════════════════════════════════"
docker-compose logs --tail=50 api-gateway
echo ""

# Resumen y recomendaciones
echo "════════════════════════════════════════════════════════"
log_info "RESUMEN Y RECOMENDACIONES"
echo "════════════════════════════════════════════════════════"
echo ""

# Verificar si todos los health checks pasaron
all_healthy=true
for service in "${services[@]}"; do
    IFS='|' read -r port name <<< "$service"
    if ! curl -sf "http://localhost:${port}/health" &> /dev/null; then
        all_healthy=false
        break
    fi
done

if [ "$all_healthy" = true ]; then
    log_success "Todos los servicios están funcionando correctamente"
    echo ""
    echo "El problema puede haber sido temporal. Intenta el despliegue nuevamente."
else
    log_warning "Algunos servicios no están respondiendo correctamente"
    echo ""
    echo "Acciones recomendadas:"
    echo ""
    echo "1. Revisa los logs completos:"
    echo "   docker-compose logs -f"
    echo ""
    echo "2. Si el problema es MongoDB:"
    echo "   - Verifica MONGO_URI en .env"
    echo "   - Verifica que la IP del servidor esté en MongoDB Atlas whitelist"
    echo "   - Prueba la conexión: docker-compose exec user-service python -c 'from pymongo import MongoClient; ...'"
    echo ""
    echo "3. Si el problema es de variables de entorno:"
    echo "   - Verifica que .env esté completo"
    echo "   - Ejecuta: grep -v '^#' .env | grep '='"
    echo ""
    echo "4. Si el problema es de memoria:"
    echo "   - Verifica: free -h"
    echo "   - Considera agregar más swap o aumentar instancia EC2"
    echo ""
    echo "5. Reiniciar servicios uno por uno:"
    echo "   docker-compose restart user-service"
    echo "   docker-compose restart api-gateway"
    echo ""
    echo "6. Si todo falla, reconstruir desde cero:"
    echo "   docker-compose down"
    echo "   docker system prune -a"
    echo "   bash deployment/deploy.sh"
fi

echo ""
echo "════════════════════════════════════════════════════════"
