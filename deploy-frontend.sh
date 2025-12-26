#!/bin/bash
set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Deploy Frontend Only to S3${NC}"
echo -e "${GREEN}========================================${NC}"

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js no está instalado${NC}"
    exit 1
fi

# Verificar AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI no está instalado${NC}"
    exit 1
fi

# Variables
STACK_NAME="${STACK_NAME:-basmati-app}"
# Usar región de AWS CLI si está configurada
if [ -z "$AWS_REGION" ]; then
    AWS_REGION=$(aws configure get region 2>/dev/null || echo "eu-north-1")
fi
REGION="$AWS_REGION"

echo -e "${GREEN}✅ Usando credenciales de AWS CLI${NC}"
echo -e "${BLUE}   Región: ${REGION}${NC}"

# Obtener la URL del API desde CloudFormation
echo -e "${YELLOW}📡 Obteniendo URL del API Gateway...${NC}"
API_URL=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
    --output text 2>/dev/null)

if [ -z "$API_URL" ]; then
    echo -e "${RED}❌ No se pudo obtener la URL del API. ¿Está desplegado el backend?${NC}"
    echo -e "${YELLOW}Ejecuta primero: ./deploy.sh${NC}"
    exit 1
fi

# Obtener nombre del bucket
BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" \
    --output text 2>/dev/null)

if [ -z "$BUCKET_NAME" ]; then
    echo -e "${RED}❌ No se pudo obtener el nombre del bucket${NC}"
    exit 1
fi

echo -e "${GREEN}✅ API URL: ${API_URL}${NC}"
echo -e "${GREEN}✅ Bucket: ${BUCKET_NAME}${NC}"

# Build del frontend
echo ""
echo -e "${GREEN}🔨 Building frontend...${NC}"
cd app/frontend

# Crear .env.production
cat > .env.production << EOF
VITE_API_GATEWAY_URL=${API_URL}
EOF

# Instalar dependencias si no existen
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Instalando dependencias...${NC}"
    npm install
fi

# Build
npm run build

# Deploy a S3
echo ""
echo -e "${GREEN}📤 Uploading to S3...${NC}"
cd ../..

aws s3 sync app/frontend/dist "s3://${BUCKET_NAME}" \
    --delete \
    --cache-control "public, max-age=31536000" \
    --exclude "*.html" \
    --exclude "*.json"

# HTML sin cache para evitar problemas con actualizaciones
aws s3 sync app/frontend/dist "s3://${BUCKET_NAME}" \
    --exclude "*" \
    --include "*.html" \
    --include "*.json" \
    --cache-control "no-cache, no-store, must-revalidate"

# Obtener URL del website
FRONTEND_URL=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='FrontendUrl'].OutputValue" \
    --output text)

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Frontend desplegado!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "📱 Frontend URL: ${YELLOW}${FRONTEND_URL}${NC}"
echo ""
