#!/bin/bash
# Deployment SEGURO usando --guided (te pregunta los parámetros)
set -e

echo "=========================================="
echo "🚀 Basmati - Deployment Seguro a AWS"
echo "=========================================="
echo ""

# Verificar AWS CLI
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ Error: AWS CLI no configurado"
    echo "Ejecuta: aws configure"
    exit 1
fi

echo "✅ AWS CLI configurado"
echo ""

# Build
echo "📦 Construyendo imágenes..."
sam build --use-container --cached

echo ""
echo "=========================================="
echo "🔐 Deploy con parámetros INTERACTIVOS"
echo "=========================================="
echo ""
echo "SAM te preguntará cada parámetro de forma segura."
echo "Los valores sensibles (MongoUri, SendGridApiKey) NO se guardarán en archivos."
echo ""
echo "Presiona Enter para continuar..."
read

# Deploy guiado - NO guarda parámetros sensibles
sam deploy \
    --guided \
    --stack-name basmati-prod \
    --region eu-north-1 \
    --capabilities CAPABILITY_IAM \
    --no-confirm-changeset

echo ""
echo "✅ Deployment completado"
