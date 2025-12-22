#!/bin/bash
# Deploy de Basmati - Parámetros por línea de comandos (SIN guardarlos en archivos)
set -e

echo "=========================================="
echo "🚀 Basmati - Deploy a AWS Lambda"
echo "=========================================="
echo ""

# Verificar AWS CLI
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI no configurado. Ejecuta: aws configure"
    exit 1
fi

AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION="eu-north-1"
echo "✅ AWS Cuenta: $AWS_ACCOUNT"
echo "   Región: $AWS_REGION"
echo ""

# Solicitar MongoDB URI de forma segura
echo "🔐 Ingresa MongoDB URI (quedará oculto al escribir):"
echo "   Formato: mongodb+srv://usuario:password@cluster.mongodb.net/basmati"
read -s MONGO_URI
echo ""

if [ -z "$MONGO_URI" ]; then
    echo "❌ MongoDB URI es requerido"
    exit 1
fi

# Bucket S3 (debe ser único)
echo "📦 Nombre del bucket S3 para imágenes:"
echo "   (debe ser único globalmente, ej: basmati-TUNOMBRE-2025)"
read -p "Bucket S3: " S3_BUCKET

if [ -z "$S3_BUCKET" ]; then
    S3_BUCKET="basmati-uploads-$AWS_ACCOUNT"
    echo "   Usando: $S3_BUCKET"
fi

# SendGrid (opcional)
echo ""
echo "📧 SendGrid API Key (opcional, presiona Enter para omitir):"
read -s SENDGRID_KEY
echo ""

if [ -z "$SENDGRID_KEY" ]; then
    SENDGRID_KEY=""
    echo "   ⚠️  Emails deshabilitados"
fi

# Build
echo ""
echo "📦 Construyendo imágenes Docker..."
sam build --use-container --cached

if [ $? -ne 0 ]; then
    echo "❌ Error en build"
    exit 1
fi

echo ""
echo "=========================================="
echo "🚀 Desplegando a AWS..."
echo "=========================================="
echo ""

# Deploy
sam deploy \
    --stack-name basmati-prod \
    --region $AWS_REGION \
    --capabilities CAPABILITY_IAM \
    --resolve-s3 \
    --resolve-image-repos \
    --parameter-overrides \
        MongoUri="$MONGO_URI" \
        DevUser1Email=amcgil@uma.es \
        DevUser2Email=rubenoliva@uma.es \
        DevUser3Email=daily_digest_test@example.com \
        AwsS3BucketName=$S3_BUCKET \
        SendGridApiKey="$SENDGRID_KEY" \
        SenderEmail=amcgil@uma.es \
        FrontendUrl=https://placeholder.com

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Error en deployment"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT EXITOSO"
echo "=========================================="
echo ""

# Obtener URL del API
API_URL=$(aws cloudformation describe-stacks \
    --stack-name basmati-prod \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text)

echo "🌐 URL de tu API:"
echo "   $API_URL"
echo ""
echo "Prueba tu API:"
echo "   curl $API_URL/health"
echo ""
echo "Ver logs:"
echo "   sam logs -n UserServiceFunction --stack-name basmati-prod --tail"
echo ""
