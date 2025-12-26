#!/bin/bash
set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Basmati Local Testing with SAM${NC}"
echo -e "${GREEN}========================================${NC}"

# Verificar que SAM CLI está instalado
if ! command -v sam &> /dev/null; then
    echo -e "${RED}❌ SAM CLI no está instalado. Instálalo con: pip install aws-sam-cli${NC}"
    exit 1
fi

# Verificar que Docker está corriendo
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker no está corriendo. Inicia Docker Desktop o el daemon de Docker${NC}"
    exit 1
fi

# Cargar variables de entorno desde app/.env
if [ -f "app/.env" ]; then
    echo -e "${BLUE}📋 Cargando variables de entorno desde app/.env${NC}"
    export $(cat app/.env | grep -v '^#' | grep -v '^$' | xargs)
else
    echo -e "${RED}❌ Archivo app/.env no encontrado${NC}"
    echo -e "${YELLOW}El archivo de configuración debe estar en app/.env${NC}"
    exit 1
fi

if [ -z "$MONGO_URI" ]; then
    echo -e "${RED}❌ MONGO_URI no está definido en app/.env${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Configuración cargada desde app/.env${NC}"
echo -e "${BLUE}   Región AWS: ${AWS_REGION}${NC}"
echo -e "${BLUE}   Bucket S3: ${AWS_S3_BUCKET_NAME}${NC}"
echo ""

# Crear archivo de parámetros para SAM local
cat > samconfig-local.toml << EOF
version = 0.1

[default.local_invoke.parameters]
parameter_overrides = "MongoURI=${MONGO_URI} FrontendBucketName=basmati-frontend-local"
env_vars = "env-vars.json"
EOF

# Crear archivo de variables de entorno para SAM local
cat > env-vars.json << EOF
{
  "ApiGatewayFunction": {
    "MONGO_URI": "${MONGO_URI}",
    "USER_SERVICE_URL": "http://localhost:3001",
    "CALENDAR_SERVICE_URL": "http://localhost:3002",
    "EVENT_SERVICE_URL": "http://localhost:3003",
    "NOTIFICATION_SERVICE_URL": "http://localhost:3004",
    "INTEGRATION_SERVICE_URL": "http://localhost:3006"
  },
  "UserServiceFunction": {
    "MONGO_URI": "${MONGO_URI}"
  },
  "CalendarServiceFunction": {
    "MONGO_URI": "${MONGO_URI}"
  },
  "EventServiceFunction": {
    "MONGO_URI": "${MONGO_URI}",
    "NOTIFICATION_SERVICE_URL": "http://localhost:3004",
    "CALENDAR_SERVICE_URL": "http://localhost:3002"
  },
  "NotificationServiceFunction": {
    "MONGO_URI": "${MONGO_URI}",
    "USER_SERVICE_URL": "http://localhost:3001"
  },
  "IntegrationServiceFunction": {
    "MONGO_URI": "${MONGO_URI}",
    "CALENDAR_SERVICE_URL": "http://localhost:3002",
    "EVENT_SERVICE_URL": "http://localhost:3003"
  }
}
EOF

echo ""
echo -e "${GREEN}🔨 Building SAM application...${NC}"
sam build

echo ""
echo -e "${GREEN}🚀 Starting local API...${NC}"
echo -e "${BLUE}La API estará disponible en: http://127.0.0.1:3000${NC}"
echo -e "${BLUE}Documentación interactiva: http://127.0.0.1:3000/docs${NC}"
echo ""
echo -e "${YELLOW}Presiona Ctrl+C para detener el servidor${NC}"
echo ""

# Iniciar API local
sam local start-api \
    --port 3000 \
    --env-vars env-vars.json \
    --parameter-overrides "MongoURI=${MONGO_URI} FrontendBucketName=basmati-frontend-local" \
    --warm-containers EAGER
