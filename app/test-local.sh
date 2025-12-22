#!/bin/bash

###############################################################################
# Script de testing local para Basmati usando SAM Local
# 
# Prerrequisitos:
# - Docker corriendo
# - AWS SAM CLI instalado
# - Archivo .env en el directorio app/
###############################################################################

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🧪 Basmati - Testing Local con SAM${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "template.yaml" ]; then
    echo -e "${RED}❌ Error: template.yaml no encontrado${NC}"
    echo "Por favor ejecuta este script desde el directorio app/"
    exit 1
fi

# Verificar Docker
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker no está corriendo${NC}"
    exit 1
fi

# Verificar SAM CLI
if ! command -v sam &> /dev/null; then
    echo -e "${RED}❌ SAM CLI no está instalado${NC}"
    exit 1
fi

# Cargar variables de entorno desde .env
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Archivo .env no encontrado${NC}"
    echo "Crea un archivo .env con las variables necesarias"
    exit 1
fi

echo -e "${GREEN}✅ Prerrequisitos verificados${NC}"
echo ""

# Cargar .env en variables de shell
export $(grep -v '^#' .env | xargs)

# Crear string de parámetros para SAM Local
PARAM_OVERRIDES="MongoUri=\"${MONGO_URI}\" "
PARAM_OVERRIDES+="DevUser1Email=\"${DEV_USER_1_EMAIL:-amcgil@uma.es}\" "
PARAM_OVERRIDES+="DevUser2Email=\"${DEV_USER_2_EMAIL:-rubenoliva@uma.es}\" "
PARAM_OVERRIDES+="DevUser3Email=\"${DEV_USER_3_EMAIL:-daily_digest_test@example.com}\" "
PARAM_OVERRIDES+="AwsS3BucketName=\"${AWS_S3_BUCKET_NAME:-basmati-uploads}\" "
PARAM_OVERRIDES+="SendGridApiKey=\"${SENDGRID_API_KEY:-}\" "
PARAM_OVERRIDES+="SenderEmail=\"${SENDER_EMAIL:-amcgil@uma.es}\" "
PARAM_OVERRIDES+="FrontendUrl=\"http://localhost:5173\""

echo -e "${BLUE}📋 Opciones disponibles:${NC}"
echo -e "  ${GREEN}1.${NC} Build y start API Gateway local (puerto 3000)"
echo -e "  ${GREEN}2.${NC} Invocar función específica"
echo -e "  ${GREEN}3.${NC} Build sin iniciar API"
echo -e "  ${GREEN}4.${NC} Limpiar builds anteriores"
echo ""
echo -e "${YELLOW}Selecciona una opción (1-4):${NC} "
read -r option

case $option in
    1)
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}🚀 Starting API Gateway Local${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo ""
        echo -e "${YELLOW}Building containers...${NC}"
        sam build
        
        echo ""
        echo -e "${GREEN}✅ Build completado${NC}"
        echo ""
        echo -e "${BLUE}📡 Iniciando API Gateway en http://127.0.0.1:3000${NC}"
        echo ""
        echo -e "${YELLOW}Endpoints disponibles:${NC}"
        echo -e "  • http://127.0.0.1:3000/health"
        echo -e "  • http://127.0.0.1:3000/v1/users"
        echo -e "  • http://127.0.0.1:3000/v1/calendars"
        echo -e "  • http://127.0.0.1:3000/v1/events"
        echo -e "  • http://127.0.0.1:3000/v1/notifications"
        echo -e "  • http://127.0.0.1:3000/v1/integrations"
        echo ""
        echo -e "${YELLOW}Presiona Ctrl+C para detener${NC}"
        echo ""
        
        sam local start-api \
            --parameter-overrides "${PARAM_OVERRIDES}" \
            --warm-containers EAGER \
            --port 3000
        ;;
        
    2)
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}🔧 Invocar Función Específica${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo ""
        echo -e "${BLUE}Funciones disponibles:${NC}"
        echo -e "  ${GREEN}1.${NC} ApiGatewayFunction"
        echo -e "  ${GREEN}2.${NC} UserServiceFunction"
        echo -e "  ${GREEN}3.${NC} CalendarServiceFunction"
        echo -e "  ${GREEN}4.${NC} EventServiceFunction"
        echo -e "  ${GREEN}5.${NC} NotificationServiceFunction"
        echo -e "  ${GREEN}6.${NC} IntegrationServiceFunction"
        echo ""
        echo -e "${YELLOW}Selecciona función (1-6):${NC} "
        read -r func_option
        
        case $func_option in
            1) FUNCTION="ApiGatewayFunction" ;;
            2) FUNCTION="UserServiceFunction" ;;
            3) FUNCTION="CalendarServiceFunction" ;;
            4) FUNCTION="EventServiceFunction" ;;
            5) FUNCTION="NotificationServiceFunction" ;;
            6) FUNCTION="IntegrationServiceFunction" ;;
            *) echo -e "${RED}Opción inválida${NC}"; exit 1 ;;
        esac
        
        echo ""
        echo -e "${YELLOW}Building container para ${FUNCTION}...${NC}"
        sam build
        
        # Crear evento de prueba (health check)
        cat > /tmp/test-event.json << 'EVENTEOF'
{
  "httpMethod": "GET",
  "path": "/health",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": null
}
EVENTEOF
        
        echo ""
        echo -e "${GREEN}✅ Invocando ${FUNCTION}...${NC}"
        echo ""
        
        sam local invoke ${FUNCTION} \
            --parameter-overrides "${PARAM_OVERRIDES}" \
            --event /tmp/test-event.json
        ;;
        
    3)
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}📦 Building Containers${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo ""
        
        sam build
        
        echo ""
        echo -e "${GREEN}✅ Build completado${NC}"
        echo -e "${YELLOW}Para iniciar el API: sam local start-api --port 3000${NC}"
        ;;
        
    4)
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}🧹 Limpiando Builds${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo ""
        
        rm -rf .aws-sam/
        echo -e "${GREEN}✅ Directorio .aws-sam/ eliminado${NC}"
        
        # Limpiar imágenes Docker de SAM
        echo ""
        echo -e "${YELLOW}¿Eliminar imágenes Docker locales de SAM? (y/n):${NC} "
        read -r clean_docker
        
        if [ "$clean_docker" == "y" ]; then
            docker images --filter "reference=*basmati*" -q | xargs -r docker rmi -f
            echo -e "${GREEN}✅ Imágenes Docker limpiadas${NC}"
        fi
        ;;
        
    *)
        echo -e "${RED}❌ Opción inválida${NC}"
        exit 1
        ;;
esac

# Limpiar archivo temporal
rm -f /tmp/test-event.json

echo ""
echo -e "${GREEN}✅ Finalizado${NC}"
