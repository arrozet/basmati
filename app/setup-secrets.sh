#!/bin/bash
# Script para almacenar secretos en AWS Secrets Manager
set -e

echo "=========================================="
echo "🔐 Configuración de Secretos en AWS"
echo "=========================================="
echo ""

# Verificar AWS CLI
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ Error: AWS CLI no configurado"
    exit 1
fi

REGION="eu-north-1"

echo "Vamos a almacenar los secretos de forma segura en AWS Secrets Manager"
echo ""

# MongoDB URI
echo "📝 MongoDB URI"
echo "Pega tu MongoDB URI (quedará oculto):"
read -s MONGO_URI
echo ""

# Verificar que no esté vacío
if [ -z "$MONGO_URI" ]; then
    echo "❌ Error: MongoDB URI no puede estar vacío"
    exit 1
fi

# Crear secreto en AWS
echo "💾 Guardando MongoDB URI en AWS Secrets Manager..."
aws secretsmanager create-secret \
    --name basmati/mongo-uri \
    --description "MongoDB Atlas connection URI for Basmati" \
    --secret-string "$MONGO_URI" \
    --region $REGION \
    2>/dev/null || \
aws secretsmanager update-secret \
    --secret-id basmati/mongo-uri \
    --secret-string "$MONGO_URI" \
    --region $REGION

echo "✅ MongoDB URI guardado en: basmati/mongo-uri"
echo ""

# SendGrid API Key (opcional)
echo "📧 SendGrid API Key (opcional, presiona Enter para omitir):"
read -s SENDGRID_KEY
echo ""

if [ ! -z "$SENDGRID_KEY" ]; then
    echo "💾 Guardando SendGrid API Key..."
    aws secretsmanager create-secret \
        --name basmati/sendgrid-key \
        --description "SendGrid API Key for Basmati emails" \
        --secret-string "$SENDGRID_KEY" \
        --region $REGION \
        2>/dev/null || \
    aws secretsmanager update-secret \
        --secret-id basmati/sendgrid-key \
        --secret-string "$SENDGRID_KEY" \
        --region $REGION
    
    echo "✅ SendGrid Key guardado en: basmati/sendgrid-key"
fi

echo ""
echo "=========================================="
echo "✅ Secretos configurados"
echo "=========================================="
echo ""
echo "Ahora puedes hacer deploy con:"
echo "  ./deploy-with-secrets.sh"
echo ""
