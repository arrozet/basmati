#!/bin/bash

##############################################################################
# Basmati - Configuración de Nginx con SSL (Let's Encrypt)
#
# Script para configurar un reverse proxy con Nginx y certificados SSL
# automáticos usando Let's Encrypt.
#
# Requisitos:
# - Dominio apuntando a la IP del servidor
# - Puertos 80 y 443 abiertos
#
# Uso: sudo bash setup-nginx.sh tu-dominio.com
##############################################################################

set -e

DOMAIN=$1
API_SUBDOMAIN="api.${DOMAIN}"
EMAIL=$2

if [ -z "$DOMAIN" ]; then
    echo "Uso: sudo bash setup-nginx.sh tu-dominio.com [email]"
    exit 1
fi

if [ -z "$EMAIL" ]; then
    EMAIL="admin@${DOMAIN}"
fi

echo "🌐 Configurando Nginx para:"
echo "  - Frontend: https://${DOMAIN}"
echo "  - API: https://${API_SUBDOMAIN}"
echo ""

# Instalar Nginx y Certbot
apt-get update
apt-get install -y nginx certbot python3-certbot-nginx

# Crear configuración de Nginx
cat > /etc/nginx/sites-available/basmati <<EOF
# Frontend
server {
    listen 80;
    server_name ${DOMAIN};

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}

# API Gateway
server {
    listen 80;
    server_name ${API_SUBDOMAIN};

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
        
        if (\$request_method = 'OPTIONS') {
            return 204;
        }
    }
}
EOF

# Habilitar sitio
ln -sf /etc/nginx/sites-available/basmati /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Verificar configuración
nginx -t

# Recargar Nginx
systemctl reload nginx

echo "✅ Nginx configurado"

# Obtener certificados SSL
echo "🔒 Obteniendo certificados SSL..."
certbot --nginx \
    -d "${DOMAIN}" \
    -d "${API_SUBDOMAIN}" \
    --email "${EMAIL}" \
    --agree-tos \
    --non-interactive \
    --redirect

echo ""
echo "✅ ¡SSL configurado!"
echo ""
echo "🌐 Tu aplicación está disponible en:"
echo "  - https://${DOMAIN}"
echo "  - https://${API_SUBDOMAIN}"
echo ""
echo "📝 Recuerda actualizar el archivo .env con las nuevas URLs:"
echo "  FRONTEND_URL=https://${DOMAIN}"
echo "  VITE_API_GATEWAY_URL=https://${API_SUBDOMAIN}"
echo "  GOOGLE_REDIRECT_URI=https://${API_SUBDOMAIN}/v1/auth/google/callback"
echo ""
echo "🔄 Y luego ejecuta: sudo bash /opt/basmati/deployment/deploy.sh"
