#!/bin/bash

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

STACK_NAME="${STACK_NAME:-basmati-app}"
# Usar región de AWS CLI si está configurada
if [ -z "$AWS_REGION" ]; then
    AWS_REGION=$(aws configure get region 2>/dev/null || echo "eu-north-1")
fi
REGION="$AWS_REGION"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Basmati Lambda Logs${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Menú de opciones
echo "Selecciona la función Lambda para ver logs:"
echo ""
echo "  1) API Gateway"
echo "  2) User Service"
echo "  3) Calendar Service"
echo "  4) Event Service"
echo "  5) Notification Service"
echo "  6) Integration Service"
echo "  7) Todas las funciones (combinado)"
echo ""
read -p "Opción (1-7): " option

case $option in
    1)
        FUNCTION_NAME="ApiGatewayFunction"
        ;;
    2)
        FUNCTION_NAME="UserServiceFunction"
        ;;
    3)
        FUNCTION_NAME="CalendarServiceFunction"
        ;;
    4)
        FUNCTION_NAME="EventServiceFunction"
        ;;
    5)
        FUNCTION_NAME="NotificationServiceFunction"
        ;;
    6)
        FUNCTION_NAME="IntegrationServiceFunction"
        ;;
    7)
        echo -e "${YELLOW}Mostrando logs de todas las funciones...${NC}"
        sam logs --stack-name "${STACK_NAME}" --tail --region "${REGION}"
        exit 0
        ;;
    *)
        echo -e "${YELLOW}Opción inválida${NC}"
        exit 1
        ;;
esac

echo -e "${BLUE}Mostrando logs de ${FUNCTION_NAME}...${NC}"
echo -e "${YELLOW}Presiona Ctrl+C para salir${NC}"
echo ""

# Tail logs de la función específica
sam logs \
    --stack-name "${STACK_NAME}" \
    --name "${FUNCTION_NAME}" \
    --tail \
    --region "${REGION}"
