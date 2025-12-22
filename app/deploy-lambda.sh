#!/bin/bash

###############################################################################
# Script de deployment para Basmati en AWS Lambda
# 
# Prerrequisitos:
# - AWS CLI configurado (aws configure)
# - AWS SAM CLI instalado (https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
# - Docker instalado y corriendo
# - Credenciales AWS con permisos de CloudFormation, Lambda, ECR, S3, API Gateway
###############################################################################

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🚀 Basmati - AWS Lambda Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "template.yaml" ]; then
    echo -e "${RED}❌ Error: template.yaml no encontrado${NC}"
    echo "Por favor ejecuta este script desde el directorio app/"
    exit 1
fi

# Verificar AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI no está instalado${NC}"
    echo "Instala desde: https://aws.amazon.com/cli/"
    exit 1
fi

# Verificar SAM CLI
if ! command -v sam &> /dev/null; then
    echo -e "${RED}❌ SAM CLI no está instalado${NC}"
    echo "Instala desde: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
    exit 1
fi

# Verificar Docker
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker no está corriendo${NC}"
    echo "Inicia Docker Desktop o el daemon de Docker"
    exit 1
fi

# Verificar configuración de AWS
AWS_REGION=$(aws configure get region)
if [ -z "$AWS_REGION" ]; then
    echo -e "${YELLOW}⚠️  AWS region no configurada. Usando us-east-1 por defecto${NC}"
    AWS_REGION="us-east-1"
fi

echo -e "${GREEN}✅ Prerrequisitos verificados${NC}"
echo -e "   📍 Región: ${AWS_REGION}"
echo -e "   👤 AWS Account: $(aws sts get-caller-identity --query Account --output text)"
echo ""

# Crear samconfig.toml si no existe
if [ ! -f "samconfig.toml" ]; then
    echo -e "${YELLOW}⚠️  samconfig.toml no encontrado${NC}"
    if [ -f "samconfig.toml.example" ]; then
        echo -e "${YELLOW}📝 Copiando desde samconfig.toml.example...${NC}"
        cp samconfig.toml.example samconfig.toml
        echo -e "${RED}⚠️  IMPORTANTE: Edita samconfig.toml con tus valores reales antes de continuar${NC}"
        echo "Presiona ENTER cuando hayas editado el archivo..."
        read
    else
        echo -e "${RED}❌ samconfig.toml.example tampoco existe${NC}"
        exit 1
    fi
fi

# Paso 1: Build
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}📦 Paso 1/3: Building containers...${NC}"
echo -e "${GREEN}========================================${NC}"
sam build --use-container

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build falló${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build completado${NC}"
echo ""

# Paso 2: Deploy
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🚀 Paso 2/3: Deploying a AWS...${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Este paso puede tardar 10-15 minutos...${NC}"
echo ""

# Si es el primer deploy, usar --guided
if [ "$1" == "--guided" ]; then
    sam deploy --guided
else
    sam deploy
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Deploy falló${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Deploy completado${NC}"
echo ""

# Paso 3: Obtener outputs
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}📋 Paso 3/3: Información del deployment${NC}"
echo -e "${GREEN}========================================${NC}"

STACK_NAME=$(grep stack_name samconfig.toml | cut -d '"' -f 2)
API_URL=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
    --output text)

echo ""
echo -e "${GREEN}✅ Deployment exitoso!${NC}"
echo ""
echo -e "${GREEN}📍 API Gateway URL:${NC}"
echo -e "   ${API_URL}"
echo ""
echo -e "${GREEN}🔗 Endpoints disponibles:${NC}"
echo -e "   ${API_URL}/health"
echo -e "   ${API_URL}/v1/users"
echo -e "   ${API_URL}/v1/calendars"
echo -e "   ${API_URL}/v1/events"
echo -e "   ${API_URL}/v1/notifications"
echo -e "   ${API_URL}/v1/integrations"
echo -e "   ${API_URL}/docs (FastAPI docs - solo si está habilitado)"
echo ""
echo -e "${YELLOW}💡 Siguiente paso: Despliega el frontend a S3${NC}"
echo -e "   Ejecuta: ./deploy-frontend.sh"
echo ""
