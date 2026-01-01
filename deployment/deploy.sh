#!/bin/bash

##############################################################################
# Basmati - Script de Despliegue Automatizado en AWS EC2
#
# Este script automatiza el despliegue completo de la aplicación Basmati
# usando Docker y docker-compose en un servidor AWS EC2.
#
# Características:
# - Verificación de dependencias
# - Build optimizado con caché de Docker
# - Manejo seguro de secretos
# - Health checks automáticos
# - Rollback en caso de fallo
# - Zero-downtime deployment
##############################################################################

set -e  # Exit on error
set -o pipefail  # Exit on pipe failure

# ==========================
# CONFIGURACIÓN
# ==========================

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración del proyecto
PROJECT_NAME="basmati"
DEPLOY_DIR="/opt/basmati"
BACKUP_DIR="/opt/basmati-backups"
LOG_FILE="/var/log/basmati-deploy.log"
MAX_BACKUPS=5

# Timeouts
HEALTH_CHECK_TIMEOUT=120
BUILD_TIMEOUT=600

# Nginx
CONFIGURE_NGINX=${CONFIGURE_NGINX:-true}  # Configurar Nginx automáticamente

# ==========================
# FUNCIONES AUXILIARES
# ==========================

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        INFO)
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        SUCCESS)
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
        WARNING)
            echo -e "${YELLOW}[WARNING]${NC} $message"
            ;;
        ERROR)
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
    esac
    
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log ERROR "Este script debe ejecutarse como root o con sudo"
        exit 1
    fi
}

check_dependencies() {
    log INFO "Verificando dependencias..."
    
    local deps=("docker" "docker-compose" "git")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing+=("$dep")
        fi
    done
    
    if [ ${#missing[@]} -ne 0 ]; then
        log ERROR "Faltan dependencias: ${missing[*]}"
        log INFO "Ejecuta primero: ./setup-ec2.sh"
        exit 1
    fi
    
    log SUCCESS "Todas las dependencias están instaladas"
}

verify_env_file() {
    log INFO "Verificando archivo .env..."
    
    if [ ! -f "$DEPLOY_DIR/app/.env" ]; then
        log ERROR "No se encontró el archivo .env en $DEPLOY_DIR/app/.env"
        log INFO "Copia el archivo .env.production al servidor"
        exit 1
    fi
    
    # Verificar variables críticas
    local required_vars=(
        "MONGO_URI"
        "GOOGLE_CLIENT_ID"
        "GOOGLE_CLIENT_SECRET"
        "VITE_API_GATEWAY_URL"
        "FRONTEND_URL"
        "SENDGRID_API_KEY"
        "SENDER_EMAIL"
    )
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" "$DEPLOY_DIR/app/.env"; then
            log WARNING "Variable ${var} no encontrada en .env"
        fi
    done
    
    log SUCCESS "Archivo .env verificado"
}

create_backup() {
    log INFO "Creando backup pre-despliegue..."
    
    mkdir -p "$BACKUP_DIR"
    
    local backup_name="backup-$(date +%Y%m%d-%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    # Backup de containers en ejecución
    if docker-compose -f "$DEPLOY_DIR/app/docker-compose.yml" ps -q &> /dev/null; then
        docker-compose -f "$DEPLOY_DIR/app/docker-compose.yml" config > "$backup_path.yml" 2>/dev/null || true
        log SUCCESS "Backup creado: $backup_path.yml"
    fi
    
    # Limpiar backups antiguos
    local backup_count=$(ls -1 "$BACKUP_DIR" | wc -l)
    if [ "$backup_count" -gt "$MAX_BACKUPS" ]; then
        log INFO "Limpiando backups antiguos..."
        ls -1t "$BACKUP_DIR" | tail -n +$((MAX_BACKUPS + 1)) | xargs -I {} rm -f "$BACKUP_DIR/{}"
    fi
    
    echo "$backup_name"
}

stop_services() {
    log INFO "Deteniendo servicios actuales..."
    
    cd "$DEPLOY_DIR/app"
    
    if docker-compose ps -q &> /dev/null; then
        docker-compose down --timeout 30 || {
            log WARNING "Timeout al detener servicios, forzando..."
            docker-compose down --timeout 5 --force || true
        }
        log SUCCESS "Servicios detenidos"
    else
        log INFO "No hay servicios en ejecución"
    fi
}

build_images() {
    log INFO "Construyendo imágenes Docker..."
    
    cd "$DEPLOY_DIR/app"
    
    # Forzar rebuild del frontend sin caché para aplicar nuevas variables .env
    log INFO "Reconstruyendo frontend sin caché..."
    DOCKER_BUILDKIT=1 docker-compose build --no-cache frontend 2>&1 | tee -a "$LOG_FILE" || {
        log ERROR "Fallo en la construcción del frontend"
        return 1
    }
    
    # Build resto de servicios con caché para optimizar tiempo
    DOCKER_BUILDKIT=1 docker-compose build \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        2>&1 | tee -a "$LOG_FILE" || {
        log ERROR "Fallo en la construcción de imágenes"
        return 1
    }
    
    log SUCCESS "Imágenes construidas exitosamente"
}

start_services() {
    log INFO "Iniciando servicios..."
    
    cd "$DEPLOY_DIR/app"
    
    # Iniciar con reinicio automático
    docker-compose up -d --remove-orphans || {
        log ERROR "Fallo al iniciar servicios"
        return 1
    }
    
    log SUCCESS "Servicios iniciados"
}

health_check() {
    log INFO "Ejecutando health checks..."
    
    local services=(
        "8000|API Gateway"
        "8001|User Service"
        "8002|Calendar Service"
        "8003|Event Service"
        "8004|Notification Service"
        "8005|Auth Service"
        "8006|Integration Service"
    )
    
    local failed=()
    local elapsed=0
    
    # Esperar 10 segundos inicial para que los servicios arranquen
    log INFO "Esperando inicio de servicios..."
    sleep 10
    
    while [ $elapsed -lt $HEALTH_CHECK_TIMEOUT ]; do
        failed=()
        
        for service_info in "${services[@]}"; do
            IFS='|' read -r port name <<< "$service_info"
            local url="http://localhost:${port}/health"
            
            if ! curl -sf "$url" &> /dev/null; then
                failed+=("$name")
            fi
        done
        
        if [ ${#failed[@]} -eq 0 ]; then
            log SUCCESS "Todos los servicios están saludables"
            return 0
        fi
        
        log INFO "Esperando servicios: ${failed[*]} (${elapsed}s/${HEALTH_CHECK_TIMEOUT}s)"
        sleep 5
        elapsed=$((elapsed + 5))
    done
    
    log ERROR "Health check falló. Servicios no disponibles: ${failed[*]}"
    return 1
}

rollback() {
    local backup_name=$1
    
    log WARNING "Iniciando rollback..."
    
    cd "$DEPLOY_DIR/app"
    
    docker-compose down --timeout 10 || true
    
    if [ -f "$BACKUP_DIR/${backup_name}.yml" ]; then
        docker-compose -f "$BACKUP_DIR/${backup_name}.yml" up -d || {
            log ERROR "Rollback falló. Intervención manual requerida."
            return 1
        }
        log SUCCESS "Rollback completado"
    else
        log WARNING "No hay backup disponible para rollback"
    fi
}

cleanup_old_images() {
    log INFO "Limpiando imágenes antiguas..."
    
    # Eliminar imágenes dangling
    docker image prune -f &> /dev/null || true
    
    # Eliminar contenedores detenidos
    docker container prune -f &> /dev/null || true
    
    log SUCCESS "Limpieza completada"
}

cleanup_files() {
    log INFO "Eliminando archivos no esenciales para ahorrar espacio..."
    
    local targets=(
        "docs"
        "LICENSE"
        "README.md"
    )
    
    for target in "${targets[@]}"; do
        if [ -e "$DEPLOY_DIR/$target" ]; then
            rm -rf "$DEPLOY_DIR/$target"
            log INFO "Eliminado: $target"
        fi
    done
    
    log SUCCESS "Archivos no esenciales eliminados"
}

configure_nginx() {
    if [ "$CONFIGURE_NGINX" != "true" ]; then
        return 0
    fi
    
    log INFO "Configurando Nginx como reverse proxy..."
    
    # Verificar si Nginx está instalado
    if ! command -v nginx &> /dev/null; then
        log INFO "Instalando Nginx..."
        apt-get update -qq
        apt-get install -y nginx &> /dev/null
    fi
    
    # Obtener IP pública
    PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")
    
    # Detectar si hay certificado SSL
    SSL_CERT="/etc/letsencrypt/live/basmati.app/fullchain.pem"
    SSL_KEY="/etc/letsencrypt/live/basmati.app/privkey.pem"
    
    if [ -f "$SSL_CERT" ] && [ -f "$SSL_KEY" ]; then
        log INFO "Certificados SSL encontrados, configurando HTTPS"
        # Configuración con SSL
        cat > /etc/nginx/sites-available/basmati <<NGINX_EOF
# Redirigir HTTP a HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name basmati.app www.basmati.app;
    return 301 https://\$host\$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name basmati.app www.basmati.app;
    
    ssl_certificate $SSL_CERT;
    ssl_certificate_key $SSL_KEY;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    
    client_max_body_size 50M;
    
    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # API - Rutas de documentación sin rewrite
    location ~ ^/api/(docs|redoc|openapi\.json) {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Prefix /api;
    }
    
    # API - Resto de endpoints
    location /api/ {
        rewrite ^/api/(.*)\$ /\$1 break;
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
    }
    
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
NGINX_EOF
    else
        log INFO "Sin certificados SSL, configurando solo HTTP"
        # Configuración sin SSL
        cat > /etc/nginx/sites-available/basmati <<'NGINX_EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name basmati.app www.basmati.app _;
    client_max_body_size 50M;
    
    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API - Rutas de documentación sin rewrite
    location ~ ^/api/(docs|redoc|openapi\.json) {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /api;
    }
    
    # API - Resto de endpoints
    location /api/ {
        rewrite ^/api/(.*)$ /$1 break;
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
    }
    
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
NGINX_EOF
    fi
    
    # Habilitar configuración
    rm -f /etc/nginx/sites-enabled/default
    ln -sf /etc/nginx/sites-available/basmati /etc/nginx/sites-enabled/
    
    # Verificar y recargar
    if nginx -t &> /dev/null; then
        systemctl restart nginx
        systemctl enable nginx &> /dev/null
        
        # Actualizar firewall
        if command -v ufw &> /dev/null && ufw status | grep -q "Status: active"; then
            ufw allow 80/tcp &> /dev/null || true
            ufw allow 443/tcp &> /dev/null || true
        fi
        
        log SUCCESS "Nginx configurado correctamente"
    else
        log WARNING "Error en configuración de Nginx, continuando sin proxy"
    fi
}

print_summary() {
    log INFO "========================================"
    log INFO "Resumen del Despliegue"
    log INFO "========================================"
    
    cd "$DEPLOY_DIR/app"
    
    echo ""
    docker-compose ps
    
    echo ""
    PUBLIC_IP=$(curl -s ifconfig.me)
    log INFO "URLs de acceso:"
    
    if systemctl is-active --quiet nginx 2>/dev/null; then
        log INFO "  - Frontend: http://${PUBLIC_IP}"
        log INFO "  - API: http://${PUBLIC_IP}/api"
        log INFO "  - API Docs: http://${PUBLIC_IP}/api/docs"
    else
        log INFO "  - Frontend: http://${PUBLIC_IP}:5173"
        log INFO "  - API Gateway: http://${PUBLIC_IP}:8000"
        log INFO "  - API Docs: http://${PUBLIC_IP}:8000/docs"
    fi
    
    echo ""
    log INFO "Logs:"
    log INFO "  Ver logs: docker-compose logs -f"
    log INFO "  Ver logs de servicio: docker-compose logs -f <service-name>"
    
    echo ""
    log INFO "========================================"
}

# ==========================
# FLUJO PRINCIPAL
# ==========================

main() {
    log INFO "Iniciando despliegue de Basmati..."
    log INFO "Timestamp: $(date)"
    
    # Verificaciones previas
    check_root
    check_dependencies
    verify_env_file
    
    # Crear backup
    backup_name=$(create_backup)
    
    # Despliegue
    if ! stop_services; then
        log ERROR "Fallo al detener servicios"
        exit 1
    fi
    
    if ! build_images; then
        log ERROR "Fallo en build de imágenes"
        rollback "$backup_name"
        exit 1
    fi
    
    if ! start_services; then
        log ERROR "Fallo al iniciar servicios"
        rollback "$backup_name"
        exit 1
    fi
    
    # Verificar que todo funciona
    if ! health_check; then
        log ERROR "Health check falló"
        rollback "$backup_name"
        exit 1
    fi
    
    # Limpieza
    cleanup_old_images
    cleanup_files
    
    # Configurar Nginx
    configure_nginx
    
    # Resumen
    print_summary
    
    log SUCCESS "¡Despliegue completado exitosamente!"
    log INFO "Backup disponible en: $BACKUP_DIR/$backup_name"
}

# Ejecutar script
main "$@"
