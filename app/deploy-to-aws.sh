#!/bin/bash
# Script de deployment a AWS Lambda - Paso a paso
# Ejecutar: ./deploy-to-aws.sh

set -e  # Detener si hay errores

echo "=========================================="
echo "🚀 Basmati - Deployment a AWS Lambda"
echo "=========================================="
echo ""

# Verificar que existe samconfig.toml
if [ ! -f "samconfig.toml" ]; then
    echo "❌ Error: No existe samconfig.toml"
    echo ""
    echo "Pasos para crear samconfig.toml:"
    echo "  1. Copia el archivo ejemplo:"
    echo "     cp samconfig.toml.example samconfig.toml"
    echo ""
    echo "  2. Edita samconfig.toml y cambia:"
    echo "     - MongoUri (tu conexión a MongoDB Atlas)"
    echo "     - AwsS3BucketName (nombre único para tu bucket)"
    echo "     - SendGridApiKey (si usas emails)"
    echo ""
    exit 1
fi

echo "✅ samconfig.toml encontrado"
echo ""

# Verificar AWS CLI configurado
echo "📋 Verificando credenciales AWS..."
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ Error: AWS CLI no configurado"
    echo ""
    echo "Configura tus credenciales AWS:"
    echo "  aws configure"
    echo ""
    echo "Necesitarás:"
    echo "  - AWS Access Key ID"
    echo "  - AWS Secret Access Key"
    echo "  - Región por defecto: eu-north-1"
    echo ""
    exit 1
fi

AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region || echo "eu-north-1")
echo "✅ AWS configurado"
echo "   Cuenta: $AWS_ACCOUNT"
echo "   Región: $AWS_REGION"
echo ""

# Paso 1: Build
echo "=========================================="
echo "📦 PASO 1: Construyendo imágenes Docker"
echo "=========================================="
echo ""
sam build --use-container --cached

echo ""
echo "✅ Build completado"
echo ""

# Paso 2: Validar template
echo "=========================================="
echo "🔍 PASO 2: Validando template"
echo "=========================================="
echo ""
sam validate

echo ""
echo "✅ Template válido"
echo ""

# Paso 3: Deploy
echo "=========================================="
echo "🚀 PASO 3: Desplegando a AWS"
echo "=========================================="
echo ""
echo "IMPORTANTE:"
echo "  - SAM creará repositorios ECR automáticamente"
echo "  - Las imágenes Docker se subirán a ECR"
echo "  - Se creará el stack de CloudFormation"
echo "  - Te pedirá confirmación antes de aplicar"
echo ""
echo "Presiona Enter para continuar o Ctrl+C para cancelar..."
read

# Primera vez: deploy guiado
if ! aws cloudformation describe-stacks --stack-name basmati-prod > /dev/null 2>&1; then
    echo "🆕 Primera vez - usando deploy guiado"
    sam deploy --guided
else
    echo "♻️  Actualizando stack existente"
    sam deploy
fi

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETADO"
echo "=========================================="
echo ""

# Obtener outputs
echo "📋 Información del deployment:"
echo ""
aws cloudformation describe-stacks \
    --stack-name basmati-prod \
    --query 'Stacks[0].Outputs' \
    --output table

echo ""
echo "🌐 URL de tu API:"
API_URL=$(aws cloudformation describe-stacks \
    --stack-name basmati-prod \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text)
echo "   $API_URL"
echo ""
echo "Prueba tu API:"
echo "   curl $API_URL/health"
echo ""
echo "=========================================="
echo "📝 Próximos pasos:"
echo "=========================================="
echo "1. Prueba el endpoint de health:"
echo "   curl $API_URL/health"
echo ""
echo "2. Revisa los logs en CloudWatch:"
echo "   sam logs -n UserServiceFunction --stack-name basmati-prod --tail"
echo ""
echo "3. Despliega el frontend a S3/CloudFront"
echo ""
echo "4. Actualiza FrontendUrl en samconfig.toml con la URL de CloudFront"
echo ""
echo "=========================================="
