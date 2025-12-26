#!/bin/bash
set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Basmati AWS Lambda Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Verificar que AWS CLI está instalado
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI no está instalado. Instálalo con: pip install awscli${NC}"
    exit 1
fi

# Verificar que SAM CLI está instalado
if ! command -v sam &> /dev/null; then
    echo -e "${RED}❌ SAM CLI no está instalado. Instálalo con: pip install aws-sam-cli${NC}"
    exit 1
fi

# Verificar que Node.js está instalado (para frontend)
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js no está instalado${NC}"
    exit 1
fi

# Variables de configuración
STACK_NAME="basmati-app"
REGION="${AWS_REGION:-eu-north-1}"  # Usar región de .env o por defecto
S3_BUCKET="${SAM_BUCKET:-basmati-sam-artifacts}"

# Cargar SOLO MONGO_URI desde app/.env (NO credenciales de AWS)
if [ -f "app/.env" ]; then
    echo -e "${BLUE}📋 Cargando MONGO_URI desde app/.env${NC}"
    # Cargar solo MONGO_URI, no AWS credentials
    export MONGO_URI=$(grep "^MONGO_URI=" app/.env | cut -d '=' -f 2-)
else
    echo -e "${RED}❌ Archivo app/.env no encontrado${NC}"
    echo -e "${YELLOW}Debe existir app/.env con MONGO_URI configurado${NC}"
    exit 1
fi

if [ -z "$MONGO_URI" ]; then
    echo -e "${RED}❌ MONGO_URI no está definido en app/.env${NC}"
    exit 1
fi

# Usar región de AWS CLI si está configurada
if [ -z "$AWS_REGION" ]; then
    AWS_REGION=$(aws configure get region 2>/dev/null || echo "eu-north-1")
fi
REGION="$AWS_REGION"

echo -e "${GREEN}✅ Usando credenciales de AWS CLI${NC}"
echo -e "${BLUE}   Usuario AWS: $(aws sts get-caller-identity --query 'Arn' --output text 2>/dev/null || echo 'No identificado')${NC}"
echo -e "${BLUE}   Región: ${REGION}${NC}"

# Solicitar nombre del bucket para frontend
echo ""
read -p "Ingresa el nombre del bucket S3 para el frontend (debe ser único globalmente): " FRONTEND_BUCKET
if [ -z "$FRONTEND_BUCKET" ]; then
    FRONTEND_BUCKET="basmati-frontend-$(date +%s)"
    echo -e "${YELLOW}Usando nombre por defecto: ${FRONTEND_BUCKET}${NC}"
fi

echo ""
echo -e "${GREEN}📦 Paso 1: Verificando/Creando bucket S3 para artefactos SAM...${NC}"
if ! aws s3 ls "s3://${S3_BUCKET}" 2>&1 > /dev/null; then
    echo "Creando bucket ${S3_BUCKET}..."
    aws s3 mb "s3://${S3_BUCKET}" --region "${REGION}"
else
    echo "Bucket ${S3_BUCKET} ya existe"
fi

echo ""
echo -e "${GREEN}🔨 Paso 2: Building SAM application...${NC}"
sam build --use-container

echo ""
echo -e "${GREEN}📤 Paso 3: Deploying to AWS Lambda...${NC}"
sam deploy \
    --stack-name "${STACK_NAME}" \
    --s3-bucket "${S3_BUCKET}" \
    --region "${REGION}" \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        "MongoURI=${MONGO_URI}" \
        "FrontendBucketName=${FRONTEND_BUCKET}" \
    --no-confirm-changeset \
    --no-fail-on-empty-changeset

echo ""
echo -e "${GREEN}✅ Backend desplegado exitosamente${NC}"

# Obtener URL del API Gateway
API_URL=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
    --output text)

echo ""
echo -e "${GREEN}🌐 API Gateway URL: ${YELLOW}${API_URL}${NC}"

# Build del frontend
echo ""
echo -e "${GREEN}🔨 Paso 4: Building frontend...${NC}"
cd app/frontend

# Crear archivo .env.production con la URL del API
cat > .env.production << EOF
VITE_API_GATEWAY_URL=${API_URL}
EOF

# Instalar dependencias y build
npm install
npm run build

echo ""
echo -e "${GREEN}📤 Paso 5: Deploying frontend to S3...${NC}"
cd ../..

# Sincronizar archivos del frontend con S3
aws s3 sync app/frontend/dist "s3://${FRONTEND_BUCKET}" --delete

# Obtener URL del website
FRONTEND_URL=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='FrontendUrl'].OutputValue" \
    --output text)

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment completado!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "📱 Frontend URL: ${YELLOW}${FRONTEND_URL}${NC}"
echo -e "🔌 API URL:      ${YELLOW}${API_URL}${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE: Comunicación entre servicios${NC}"
echo -e "${YELLOW}Este es el PRIMER deployment. Las llamadas inter-servicios${NC}"
echo -e "${YELLOW}(ej: Event Service → Notification Service) NO funcionarán aún.${NC}"
echo ""
echo -e "${YELLOW}Para habilitar comunicación entre servicios:${NC}"
echo -e "  1. Guarda esta URL del API Gateway: ${API_URL}"
echo -e "  2. Lee CIRCULAR_DEPENDENCY_FIX.md para instrucciones"
echo -e "  3. Actualiza template.yaml con la URL del API Gateway"
echo -e "  4. Ejecuta ./deploy.sh de nuevo"
echo ""
echo -e "${YELLOW}Nota: Si el frontend no carga correctamente, espera unos minutos${NC}"
echo -e "${YELLOW}para que S3 propague los cambios.${NC}"
echo ""
