#!/bin/bash

##############################################################################
# Basmati - Verificación Pre-Despliegue
#
# Verifica que todo está listo antes de desplegar en producción.
#
# Uso: ./pre-deployment-check.sh
##############################################################################

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

error() {
    echo -e "${RED}❌ ERROR:${NC} $1"
    ((ERRORS++))
}

warning() {
    echo -e "${YELLOW}⚠️  WARNING:${NC} $1"
    ((WARNINGS++))
}

success() {
    echo -e "${GREEN}✅${NC} $1"
}

info() {
    echo -e "${BLUE}ℹ️${NC}  $1"
}

check_file_exists() {
    local file=$1
    local name=$2
    
    if [ -f "$file" ]; then
        success "$name existe"
        return 0
    else
        error "$name no encontrado: $file"
        return 1
    fi
}

check_env_var() {
    local var_name=$1
    local optional=${2:-false}
    
    if grep -q "^${var_name}=" /opt/basmati/app/.env 2>/dev/null; then
        local value=$(grep "^${var_name}=" /opt/basmati/app/.env | cut -d'=' -f2-)
        
        # Check if it's a placeholder
        if [[ "$value" == *"tu-"* ]] || [[ "$value" == *"TU_"* ]] || [[ "$value" == "" ]]; then
            if [ "$optional" = true ]; then
                warning "$var_name está vacío o es placeholder (opcional)"
            else
                error "$var_name está vacío o es placeholder"
            fi
        else
            success "$var_name configurado"
        fi
    else
        if [ "$optional" = true ]; then
            warning "$var_name no encontrado (opcional)"
        else
            error "$var_name no encontrado en .env"
        fi
    fi
}

echo "╔════════════════════════════════════════════════════════╗"
echo "║   Basmati - Verificación Pre-Despliegue              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# ====================
# Verificar Sistema
# ====================
info "Verificando sistema..."
echo ""

if command -v docker &> /dev/null; then
    success "Docker instalado: $(docker --version | cut -d' ' -f3)"
else
    error "Docker no está instalado"
fi

if command -v docker-compose &> /dev/null; then
    success "Docker Compose instalado: $(docker-compose --version | cut -d' ' -f4)"
else
    error "Docker Compose no está instalado"
fi

if systemctl is-active --quiet docker; then
    success "Docker daemon corriendo"
else
    error "Docker daemon no está corriendo"
fi

echo ""

# ====================
# Verificar Archivos
# ====================
info "Verificando archivos del proyecto..."
echo ""

check_file_exists "/opt/basmati/app/.env" "Archivo .env"
check_file_exists "/opt/basmati/app/docker-compose.yml" "docker-compose.yml"
check_file_exists "/opt/basmati/deployment/deploy.sh" "Script de despliegue"

echo ""

# ====================
# Verificar Variables
# ====================
info "Verificando variables de entorno..."
echo ""

# Críticas
check_env_var "MONGO_URI"
check_env_var "DATABASE_NAME"
check_env_var "FRONTEND_URL"
check_env_var "VITE_API_GATEWAY_URL"

echo ""
info "Variables OAuth:"
check_env_var "GOOGLE_CLIENT_ID"
check_env_var "GOOGLE_CLIENT_SECRET"
check_env_var "GOOGLE_REDIRECT_URI"
check_env_var "JWT_SECRET_KEY"

echo ""
info "Variables AWS:"
check_env_var "AWS_ACCESS_KEY_ID"
check_env_var "AWS_SECRET_ACCESS_KEY"
check_env_var "AWS_REGION"
check_env_var "AWS_S3_BUCKET_NAME"

echo ""
info "Variables SendGrid:"
check_env_var "SENDGRID_API_KEY"
check_env_var "SENDER_EMAIL"

echo ""
info "Variables opcionales:"
check_env_var "TEAMUP_API_KEY" true
check_env_var "GOOGLE_CALENDAR_API_KEY" true

echo ""

# ====================
# Verificar Conectividad
# ====================
info "Verificando conectividad..."
echo ""

if ping -c 1 8.8.8.8 &> /dev/null; then
    success "Conectividad a Internet"
else
    error "Sin conectividad a Internet"
fi

if ping -c 1 mongodb.net &> /dev/null; then
    success "DNS resuelve MongoDB"
else
    warning "No se puede resolver mongodb.net"
fi

echo ""

# ====================
# Verificar Puertos
# ====================
info "Verificando puertos disponibles..."
echo ""

ports=(5173 8000 8001 8002 8003 8004 8005 8006)
for port in "${ports[@]}"; do
    if ! netstat -tuln 2>/dev/null | grep -q ":${port} "; then
        success "Puerto $port disponible"
    else
        warning "Puerto $port ya está en uso"
    fi
done

echo ""

# ====================
# Verificar Firewall
# ====================
info "Verificando firewall..."
echo ""

if command -v ufw &> /dev/null; then
    if ufw status | grep -q "Status: active"; then
        success "UFW está activo"
        
        if ufw status | grep -q "8000"; then
            success "Puerto 8000 (API Gateway) abierto"
        else
            warning "Puerto 8000 no está abierto en UFW"
        fi
    else
        warning "UFW no está activo"
    fi
else
    warning "UFW no está instalado"
fi

echo ""

# ====================
# Verificar Recursos
# ====================
info "Verificando recursos del sistema..."
echo ""

# RAM
ram_mb=$(free -m | awk '/^Mem:/{print $2}')
if [ "$ram_mb" -ge 3800 ]; then
    success "RAM: ${ram_mb}MB (suficiente)"
elif [ "$ram_mb" -ge 1800 ]; then
    warning "RAM: ${ram_mb}MB (mínimo, puede ser lento)"
else
    error "RAM: ${ram_mb}MB (insuficiente, mínimo 2GB)"
fi

# Disco
disk_gb=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$disk_gb" -ge 15 ]; then
    success "Disco disponible: ${disk_gb}GB"
elif [ "$disk_gb" -ge 10 ]; then
    warning "Disco disponible: ${disk_gb}GB (espacio bajo)"
else
    error "Disco disponible: ${disk_gb}GB (insuficiente)"
fi

echo ""

# ====================
# Resumen
# ====================
echo "════════════════════════════════════════════════════════"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ TODO LISTO PARA DESPLIEGUE${NC}"
    echo ""
    echo "Ejecuta: sudo bash /opt/basmati/deployment/deploy.sh"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  HAY ${WARNINGS} ADVERTENCIAS${NC}"
    echo ""
    echo "Puedes continuar pero revisa las advertencias."
    echo "Ejecuta: sudo bash /opt/basmati/deployment/deploy.sh"
    exit 0
else
    echo -e "${RED}❌ HAY ${ERRORS} ERRORES QUE DEBEN CORREGIRSE${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}   Y ${WARNINGS} ADVERTENCIAS${NC}"
    fi
    echo ""
    echo "Corrige los errores antes de desplegar."
    exit 1
fi
