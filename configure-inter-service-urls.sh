#!/bin/bash

# Script para actualizar template.yaml con las URLs del API Gateway
# después del primer deployment

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

STACK_NAME="basmati-app"
REGION="${AWS_REGION:-eu-north-1}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🔧 Configurar URLs Inter-Servicios${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Verificar que el stack existe
echo -e "${BLUE}🔍 Verificando stack CloudFormation...${NC}"
if ! aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${REGION}" &> /dev/null; then
    echo -e "${RED}❌ Error: Stack '${STACK_NAME}' no encontrado${NC}"
    echo -e "${YELLOW}Ejecuta primero: ./deploy.sh${NC}"
    exit 1
fi

# Obtener URL del API Gateway
echo -e "${BLUE}📡 Obteniendo URL del API Gateway...${NC}"
API_URL=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
    --output text)

if [ -z "$API_URL" ] || [ "$API_URL" == "None" ]; then
    echo -e "${RED}❌ No se pudo obtener la URL del API Gateway${NC}"
    exit 1
fi

echo -e "${GREEN}✅ URL encontrada: ${API_URL}${NC}"
echo ""

# Crear backup del template actual
BACKUP_FILE="template.yaml.backup-$(date +%Y%m%d-%H%M%S)"
echo -e "${BLUE}💾 Creando backup: ${BACKUP_FILE}${NC}"
cp template.yaml "$BACKUP_FILE"

# Función para agregar variables de entorno a una función
add_environment_vars() {
    local function_name=$1
    local vars=$2
    
    echo -e "${BLUE}  Configurando ${function_name}...${NC}"
    
    # Buscar el comentario "No environment variables needed" y reemplazarlo
    sed -i "/# No environment variables needed.*${function_name}/,/^$/c\\
      Environment:\\
        Variables:\\
${vars}" template.yaml
}

echo -e "${BLUE}📝 Actualizando template.yaml...${NC}"
echo ""

# Agregar variables al ApiGatewayFunction
add_environment_vars "ApiGatewayFunction" "          API_GATEWAY_URL: ${API_URL}\\
          USER_SERVICE_URL: !Sub \"\${API_GATEWAY_URL}/user\"\\
          CALENDAR_SERVICE_URL: !Sub \"\${API_GATEWAY_URL}/calendar\"\\
          EVENT_SERVICE_URL: !Sub \"\${API_GATEWAY_URL}/event\"\\
          NOTIFICATION_SERVICE_URL: !Sub \"\${API_GATEWAY_URL}/notification\"\\
          INTEGRATION_SERVICE_URL: !Sub \"\${API_GATEWAY_URL}/integration\""

# Agregar variables al EventServiceFunction
add_environment_vars "EventServiceFunction" "          API_GATEWAY_URL: ${API_URL}\\
          NOTIFICATION_SERVICE_URL: !Sub \"\${API_GATEWAY_URL}/notification\"\\
          CALENDAR_SERVICE_URL: !Sub \"\${API_GATEWAY_URL}/calendar\"\\
          USER_SERVICE_URL: !Sub \"\${API_GATEWAY_URL}/user\"\\
          INTEGRATION_SERVICE_URL: !Sub \"\${API_GATEWAY_URL}/integration\""

# Agregar variables al NotificationServiceFunction
add_environment_vars "NotificationServiceFunction" "          API_GATEWAY_URL: ${API_URL}\\
          USER_SERVICE_URL: !Sub \"\${API_GATEWAY_URL}/user\""

# Agregar variables al IntegrationServiceFunction
add_environment_vars "IntegrationServiceFunction" "          API_GATEWAY_URL: ${API_URL}\\
          CALENDAR_SERVICE_URL: !Sub \"\${API_GATEWAY_URL}/calendar\"\\
          EVENT_SERVICE_URL: !Sub \"\${API_GATEWAY_URL}/event\""

echo ""
echo -e "${GREEN}✅ template.yaml actualizado${NC}"
echo ""
echo -e "${YELLOW}⚠️  ADVERTENCIA: Este cambio hardcodea la URL del API Gateway${NC}"
echo -e "${YELLOW}Si destruyes y recreas el stack, la URL cambiará y deberás${NC}"
echo -e "${YELLOW}ejecutar este script de nuevo.${NC}"
echo ""
echo -e "${BLUE}Para aplicar los cambios:${NC}"
echo -e "  ${GREEN}./deploy.sh${NC}"
echo ""
echo -e "${BLUE}Para restaurar el backup:${NC}"
echo -e "  ${YELLOW}cp ${BACKUP_FILE} template.yaml${NC}"
echo ""
