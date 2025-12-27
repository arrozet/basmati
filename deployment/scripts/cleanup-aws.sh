#!/bin/bash

# Ir al directorio raíz del proyecto
cd "$(dirname "$0")/../.." || exit 1

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

STACK_NAME="${STACK_NAME:-basmati-app}"
# Usar región de AWS CLI si está configurada
if [ -z "$AWS_REGION" ]; then
    AWS_REGION=$(aws configure get region 2>/dev/null || echo "eu-north-1")
fi
REGION="$AWS_REGION"

echo -e "${RED}========================================${NC}"
echo -e "${RED}   ⚠️  ELIMINAR DEPLOYMENT DE AWS${NC}"
echo -e "${RED}========================================${NC}"
echo ""
echo -e "${YELLOW}Esto eliminará:${NC}"
echo -e "  • Todas las funciones Lambda"
echo -e "  • El API Gateway"
echo -e "  • El bucket S3 del frontend (¡y todo su contenido!)"
echo -e "  • Roles y políticas de IAM"
echo -e "  • Logs de CloudWatch"
echo ""
echo -e "${RED}⚠️  Esta acción NO se puede deshacer${NC}"
echo ""
read -p "¿Estás seguro? Escribe 'DELETE' para confirmar: " confirmation

if [ "$confirmation" != "DELETE" ]; then
    echo -e "${GREEN}Cancelado. No se eliminó nada.${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}Obteniendo información del stack...${NC}"

# Obtener nombre del bucket antes de eliminar el stack
BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" \
    --output text 2>/dev/null || echo "")

if [ -n "$BUCKET_NAME" ]; then
    echo -e "${YELLOW}Vaciando bucket S3: ${BUCKET_NAME}${NC}"
    aws s3 rm "s3://${BUCKET_NAME}" --recursive 2>/dev/null || echo "Bucket ya vacío o no existe"
fi

echo ""
echo -e "${YELLOW}Eliminando stack de CloudFormation...${NC}"
sam delete \
    --stack-name "${STACK_NAME}" \
    --region "${REGION}" \
    --no-prompts

echo ""
echo -e "${GREEN}✅ Stack eliminado exitosamente${NC}"

# Opcional: Limpiar bucket de artefactos SAM
echo ""
read -p "¿Deseas también eliminar el bucket de artefactos SAM? (s/N): " delete_sam_bucket

if [ "$delete_sam_bucket" = "s" ] || [ "$delete_sam_bucket" = "S" ]; then
    SAM_BUCKET="${SAM_BUCKET:-basmati-sam-artifacts}"
    echo -e "${YELLOW}Eliminando bucket SAM: ${SAM_BUCKET}${NC}"
    aws s3 rb "s3://${SAM_BUCKET}" --force 2>/dev/null || echo "Bucket no existe"
    echo -e "${GREEN}✅ Bucket SAM eliminado${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Cleanup completado${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Nota: Los logs de CloudWatch pueden tardar unos minutos en eliminarse completamente${NC}"
echo ""
