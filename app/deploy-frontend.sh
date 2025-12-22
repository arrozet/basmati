#!/bin/bash

###############################################################################
# Script de deployment del Frontend de Basmati en S3 + CloudFront
###############################################################################

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎨 Basmati Frontend - S3 Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Variables
BUCKET_NAME="${FRONTEND_BUCKET_NAME:-basmati-frontend}"
REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="${STACK_NAME:-basmati-stack}"

# Obtener la URL del API Gateway del stack de Lambda
echo -e "${GREEN}📡 Obteniendo URL del API Gateway...${NC}"
API_URL=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${REGION} \
    --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
    --output text 2>/dev/null)

if [ -z "$API_URL" ]; then
    echo -e "${RED}❌ No se pudo obtener la URL del API Gateway${NC}"
    echo "Asegúrate de que el stack ${STACK_NAME} está desplegado"
    exit 1
fi

echo -e "${GREEN}✅ API Gateway URL: ${API_URL}${NC}"
echo ""

# Cambiar al directorio del frontend
cd frontend

# Crear archivo .env.production con la API URL
echo -e "${GREEN}📝 Configurando variables de entorno...${NC}"
cat > .env.production << EOF
VITE_API_GATEWAY_URL=${API_URL}
EOF

echo -e "${GREEN}✅ Archivo .env.production creado${NC}"
echo ""

# Build del frontend
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}📦 Building frontend...${NC}"
echo -e "${GREEN}========================================${NC}"
pnpm install
pnpm build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build del frontend falló${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build completado${NC}"
echo ""

# Crear bucket S3 si no existe
echo -e "${GREEN}🪣 Creando bucket S3...${NC}"
aws s3 mb s3://${BUCKET_NAME} --region ${REGION} 2>/dev/null || echo "Bucket ya existe"

# Configurar bucket como website
aws s3 website s3://${BUCKET_NAME} \
    --index-document index.html \
    --error-document index.html

# Configurar política pública
cat > /tmp/bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::${BUCKET_NAME}/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket ${BUCKET_NAME} \
    --policy file:///tmp/bucket-policy.json

# Deshabilitar bloqueo de acceso público
aws s3api put-public-access-block \
    --bucket ${BUCKET_NAME} \
    --public-access-block-configuration \
    "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

echo -e "${GREEN}✅ Bucket configurado${NC}"
echo ""

# Subir archivos
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}☁️  Subiendo archivos a S3...${NC}"
echo -e "${GREEN}========================================${NC}"

aws s3 sync dist/ s3://${BUCKET_NAME}/ \
    --delete \
    --cache-control "public, max-age=31536000" \
    --exclude "index.html"

# index.html sin caché (para que siempre se obtenga la última versión)
aws s3 cp dist/index.html s3://${BUCKET_NAME}/index.html \
    --cache-control "no-cache, no-store, must-revalidate"

echo -e "${GREEN}✅ Archivos subidos${NC}"
echo ""

# Obtener URL del website
WEBSITE_URL="http://${BUCKET_NAME}.s3-website-${REGION}.amazonaws.com"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Frontend desplegado exitosamente!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}🌐 URL del Frontend:${NC}"
echo -e "   ${WEBSITE_URL}"
echo ""
echo -e "${YELLOW}💡 Opcional: Configura CloudFront para HTTPS y mejor performance${NC}"
echo ""
echo -e "${YELLOW}Para crear distribución de CloudFront:${NC}"
echo -e "   aws cloudfront create-distribution \\"
echo -e "       --origin-domain-name ${BUCKET_NAME}.s3-website-${REGION}.amazonaws.com \\"
echo -e "       --default-root-object index.html"
echo ""
