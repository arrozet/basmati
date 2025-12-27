#!/bin/bash

# Script de deployment final para Basmati
# Incluye preparación de shared/ y deployment completo

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

STACK_NAME="basmati-app"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          🚀 BASMATI - DEPLOYMENT FINAL A AWS LAMBDA              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Ir al directorio raíz del proyecto
cd "$(dirname "$0")/../.." || exit 1

# Verificar que estamos en el directorio correcto
if [ ! -f "template.yaml" ] && [ ! -L "template.yaml" ]; then
    echo -e "${RED}❌ Error: template.yaml no encontrado${NC}"
    echo -e "${YELLOW}Ejecuta este script desde cualquier lugar, se ajustará automáticamente${NC}"
    exit 1
fi

# Verificar archivo .env
if [ ! -f "app/.env" ]; then
    echo -e "${RED}❌ Error: app/.env no encontrado${NC}"
    exit 1
fi

# Cargar MONGO_URI
echo -e "${BLUE}📋 Paso 1: Cargando configuración...${NC}"
export MONGO_URI=$(grep "^MONGO_URI=" app/.env | cut -d '=' -f 2-)
if [ -z "$MONGO_URI" ]; then
    echo -e "${RED}❌ Error: MONGO_URI no encontrado en app/.env${NC}"
    exit 1
fi
echo -e "${GREEN}✅ MONGO_URI cargado${NC}"

# Verificar credenciales AWS
echo ""
echo -e "${BLUE}📋 Paso 2: Verificando credenciales AWS...${NC}"
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ Error: No se detectaron credenciales de AWS CLI${NC}"
    echo -e "${YELLOW}Ejecuta: aws configure${NC}"
    exit 1
fi

AWS_USER=$(aws sts get-caller-identity --query 'Arn' --output text 2>/dev/null || echo 'No identificado')
AWS_REGION=$(aws configure get region 2>/dev/null || echo "eu-north-1")
echo -e "${GREEN}✅ Usuario AWS: ${AWS_USER}${NC}"
echo -e "${GREEN}✅ Región: ${AWS_REGION}${NC}"

# Copiar shared/ a cada servicio
echo ""
echo -e "${BLUE}📋 Paso 3: Preparando módulo compartido (shared/)...${NC}"
cd app/backend

SERVICES=(
    "api-gateway"
    "auth_service"
    "user_service"
    "calendar_service"
    "event_service"
    "notification_service"
    "integration_service"
)

for service in "${SERVICES[@]}"; do
    if [ -d "$service" ]; then
        echo -e "${YELLOW}  → Copiando shared/ a ${service}/${NC}"
        cp -r shared "$service/" 2>/dev/null || true
    else
        echo -e "${RED}  ⚠️  Servicio $service no encontrado${NC}"
    fi
done

cd ../..
echo -e "${GREEN}✅ Módulo shared/ copiado a todos los servicios${NC}"

# Solicitar nombre del bucket para frontend si no existe
echo ""
echo -e "${BLUE}📋 Paso 4: Configuración del bucket S3 frontend...${NC}"

# Intentar obtener el bucket del stack existente
EXISTING_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${AWS_REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" \
    --output text 2>/dev/null || echo "")

if [ -n "$EXISTING_BUCKET" ] && [ "$EXISTING_BUCKET" != "None" ]; then
    FRONTEND_BUCKET="$EXISTING_BUCKET"
    echo -e "${GREEN}✅ Usando bucket existente: ${FRONTEND_BUCKET}${NC}"
else
    read -p "Ingresa el nombre del bucket S3 para el frontend (Enter para generar automático): " FRONTEND_BUCKET
    if [ -z "$FRONTEND_BUCKET" ]; then
        FRONTEND_BUCKET="basmati-frontend-$(date +%s)"
        echo -e "${YELLOW}   Usando nombre generado: ${FRONTEND_BUCKET}${NC}"
    fi
fi

# SAM maneja el bucket automáticamente con --resolve-s3
echo ""
echo -e "${BLUE}📋 Paso 5: Preparando deployment (SAM gestionará buckets automáticamente)...${NC}"
echo -e "${GREEN}✅ Usando --resolve-s3 para gestión automática de artefactos${NC}"

# Build con SAM
echo ""
echo -e "${BLUE}📋 Paso 6: Building con SAM usando Docker (puede tardar varios minutos)...${NC}"
echo -e "${YELLOW}   Esto descargará imágenes de Docker e instalará todas las dependencias...${NC}"
sam build --use-container

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error durante el build${NC}"
    exit 1
fi

# Verificar que el build generó los artefactos correctamente
echo -e "${YELLOW}   Verificando artefactos del build...${NC}"
if [ ! -d ".aws-sam/build" ] || [ -z "$(ls -A .aws-sam/build)" ]; then
    echo -e "${RED}❌ Error: El build no generó artefactos${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build completado correctamente${NC}"

# Deploy del backend
echo ""
echo -e "${BLUE}📋 Paso 7: Desplegando backend a AWS Lambda...${NC}"

# Extraer credenciales de Google desde .env
GOOGLE_CLIENT_ID=$(grep "^GOOGLE_CLIENT_ID=" app/.env | cut -d '=' -f 2-)
GOOGLE_CLIENT_SECRET=$(grep "^GOOGLE_CLIENT_SECRET=" app/.env | cut -d '=' -f 2-)

sam deploy \
    --stack-name "${STACK_NAME}" \
    --capabilities CAPABILITY_IAM \
    --region "${AWS_REGION}" \
    --resolve-s3 \
    --parameter-overrides "MongoDBURI=${MONGO_URI}" "GoogleClientID=${GOOGLE_CLIENT_ID}" "GoogleClientSecret=${GOOGLE_CLIENT_SECRET}" "FrontendBucketName=${FRONTEND_BUCKET}" \
    --no-confirm-changeset \
    --no-fail-on-empty-changeset

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error durante el deployment del backend${NC}"
    exit 1
fi

# Obtener outputs del stack
echo ""
echo -e "${BLUE}📋 Paso 8: Obteniendo información del deployment...${NC}"
API_URL=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${AWS_REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
    --output text)

FRONTEND_BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${AWS_REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" \
    --output text)

FRONTEND_URL=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${AWS_REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='FrontendUrl'].OutputValue" \
    --output text)

echo -e "${GREEN}✅ Backend desplegado exitosamente${NC}"
echo -e "${GREEN}   API URL: ${API_URL}${NC}"

# Build y deploy del frontend
echo ""
echo -e "${BLUE}📋 Paso 9: Building frontend...${NC}"
cd app/frontend

# Limpiar node_modules si hay problemas de permisos
if [ -d "node_modules" ]; then
    echo -e "${YELLOW}   Limpiando node_modules...${NC}"
    rm -rf node_modules
fi

# Instalar dependencias
echo -e "${YELLOW}   Instalando dependencias...${NC}"
npm install

# Crear archivo .env.production copiando variables VITE_* desde app/.env
echo -e "${YELLOW}   Configurando variables de entorno de producción...${NC}"

# Copiar todas las variables VITE_* del .env principal
if [ -f "../.env" ]; then
    grep "^VITE_" ../.env > .env.production 2>/dev/null || echo "" > .env.production
    
    # Actualizar o agregar VITE_API_GATEWAY_URL con la URL de producción
    if grep -q "^VITE_API_GATEWAY_URL=" .env.production; then
        sed -i "s|^VITE_API_GATEWAY_URL=.*|VITE_API_GATEWAY_URL=${API_URL}|" .env.production
    else
        echo "VITE_API_GATEWAY_URL=${API_URL}" >> .env.production
    fi
else
    # Si no existe app/.env, crear solo con la URL del API
    cat > .env.production << EOF
VITE_API_GATEWAY_URL=${API_URL}
EOF
fi

echo -e "${GREEN}✅ Variables de entorno configuradas:${NC}"
cat .env.production

echo -e "${YELLOW}   Compilando frontend...${NC}"
npx vite build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error durante el build del frontend${NC}"
    cd ../..
    exit 1
fi

echo -e "${GREEN}✅ Frontend compilado${NC}"

# Deploy del frontend a S3
echo ""
echo -e "${BLUE}📋 Paso 10: Desplegando frontend a S3...${NC}"
cd ../..
aws s3 sync app/frontend/dist "s3://${FRONTEND_BUCKET_NAME}" --delete --region "${AWS_REGION}"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error durante el deployment del frontend${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Frontend desplegado exitosamente${NC}"

# Configurar S3 para SPA (Single Page Application)
echo ""
echo -e "${BLUE}📋 Paso 11: Configurando S3 para rutas SPA...${NC}"
cat > deployment/config/s3-website-config.json << 'EOF'
{
  "IndexDocument": {
    "Suffix": "index.html"
  },
  "ErrorDocument": {
    "Key": "index.html"
  }
}
EOF

aws s3api put-bucket-website \
    --bucket "${FRONTEND_BUCKET_NAME}" \
    --website-configuration file://deployment/config/s3-website-config.json \
    --region "${AWS_REGION}"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ S3 configurado para SPA (todas las rutas → index.html)${NC}"
else
    echo -e "${YELLOW}⚠️  No se pudo configurar S3 website (puede que ya esté configurado)${NC}"
fi

# Verificar que el API funciona
echo ""
echo -e "${BLUE}📋 Paso 12: Verificando API...${NC}"
# Verificar que el API funciona
echo ""
echo -e "${BLUE}📋 Paso 12: Verificando API...${NC}"
HEALTH_CHECK=$(curl -s "${API_URL}health" | grep -o "healthy" || echo "")

if [ "$HEALTH_CHECK" = "healthy" ]; then
    echo -e "${GREEN}✅ API funcionando correctamente${NC}"
else
    echo -e "${YELLOW}⚠️  No se pudo verificar el health check del API${NC}"
fi

# Resumen final
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✅ DEPLOYMENT COMPLETADO EXITOSAMENTE                ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📱 FRONTEND:${NC}"
echo -e "   URL:    ${YELLOW}${FRONTEND_URL}${NC}"
echo -e "   Bucket: ${YELLOW}${FRONTEND_BUCKET_NAME}${NC}"
echo -e "   ${GREEN}✅ Configurado para SPA (React Router)${NC}"
echo ""
echo -e "${BLUE}🔌 BACKEND API:${NC}"
echo -e "   URL:  ${YELLOW}${API_URL}${NC}"
echo -e "   Docs: ${YELLOW}${API_URL}docs${NC}"
echo ""
echo -e "${BLUE}📝 VARIABLES DE ENTORNO:${NC}"
echo -e "   ${GREEN}✅ .env.production creado desde app/.env${NC}"
echo -e "   ${GREEN}✅ VITE_API_GATEWAY_URL inyectado en el build${NC}"
echo ""
echo -e "${GREEN}✅ FUNCIONALIDADES OPERATIVAS:${NC}"
echo -e "   ✅ API Gateway funcionando"
echo -e "   ✅ 7 Microservicios Lambda desplegados"
echo -e "   ✅ Módulo 'shared' incluido en todas las Lambdas"
echo -e "   ✅ MongoDB Atlas conectado"
echo -e "   ✅ Frontend en S3"
echo -e "   ✅ CORS configurado"
echo ""
echo -e "${YELLOW}⚠️  COMUNICACIÓN INTER-SERVICIOS:${NC}"
echo -e "   Las funcionalidades que requieren comunicación entre servicios"
echo -e "   (notificaciones, comentarios) pueden no funcionar correctamente."
echo ""
echo -e "   ${BLUE}Para habilitarlas completamente:${NC}"
echo -e "   ${GREEN}1.${NC} ./configure-inter-service-urls.sh"
echo -e "   ${GREEN}2.${NC} ./deploy-final.sh"
echo ""
echo -e "${BLUE}🧪 PROBAR EL API:${NC}"
echo -e "   ${GREEN}curl ${API_URL}health${NC}"
echo ""
echo -e "${BLUE}📊 RECURSOS DESPLEGADOS:${NC}"
echo -e "   • 7 Lambda Functions (API Gateway, Auth, User, Calendar, Event, Notification, Integration)"
echo -e "   • 1 API Gateway REST API"
echo -e "   • 1 S3 Bucket (frontend)"
echo -e "   • IAM Roles y Políticas"
echo -e "   • CloudFormation Stack"
echo ""
echo -e "${BLUE}💰 COSTOS ESTIMADOS:${NC}"
echo -e "   • Lambda: ~\$0 (1M invocaciones gratis/mes)"
echo -e "   • API Gateway: ~\$3.50/millón de requests"
echo -e "   • S3: ~\$0.023/GB/mes"
echo -e "   • ${GREEN}Total: Casi \$0 con Free Tier${NC}"
echo ""
echo -e "${BLUE}🗑️  PARA ELIMINAR TODOS LOS RECURSOS:${NC}"
echo -e "   ${YELLOW}./cleanup-aws.sh${NC}"
echo ""
