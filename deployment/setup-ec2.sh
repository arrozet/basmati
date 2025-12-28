#!/bin/bash

##############################################################################
# Basmati - Script de Configuración Inicial de AWS EC2
#
# Este script prepara un servidor EC2 limpio para ejecutar Basmati.
# Instala todas las dependencias necesarias y configura el entorno.
#
# Requisitos:
# - Ubuntu 22.04 LTS o superior
# - Al menos 2GB de RAM
# - Al menos 20GB de disco
#
# Ejecutar como root: sudo bash setup-ec2.sh
##############################################################################

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    local level=$1
    shift
    local message="$@"
    
    case $level in
        INFO) echo -e "${BLUE}[INFO]${NC} $message" ;;
        SUCCESS) echo -e "${GREEN}[SUCCESS]${NC} $message" ;;
        WARNING) echo -e "${YELLOW}[WARNING]${NC} $message" ;;
        ERROR) echo -e "${RED}[ERROR]${NC} $message" ;;
    esac
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log ERROR "Este script debe ejecutarse como root o con sudo"
        exit 1
    fi
}

check_system_requirements() {
    log INFO "Verificando requisitos del sistema..."
    
    # Verificar RAM
    local ram_mb=$(free -m | awk '/^Mem:/{print $2}')
    if [ "$ram_mb" -lt 1800 ]; then
        log WARNING "RAM insuficiente: ${ram_mb}MB (recomendado: 2048MB)"
    fi
    
    # Verificar disco
    local disk_gb=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$disk_gb" -lt 15 ]; then
        log WARNING "Espacio en disco bajo: ${disk_gb}GB (recomendado: 20GB)"
    fi
    
    log SUCCESS "Requisitos verificados"
}

update_system() {
    log INFO "Actualizando sistema..."
    
    apt-get update -qq
    apt-get upgrade -y -qq
    apt-get install -y -qq \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        git \
        htop \
        vim \
        ufw
    
    log SUCCESS "Sistema actualizado"
}

install_docker() {
    log INFO "Instalando Docker..."
    
    if command -v docker &> /dev/null; then
        log INFO "Docker ya está instalado: $(docker --version)"
        return 0
    fi
    
    # Añadir repositorio de Docker
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Habilitar Docker al inicio
    systemctl enable docker
    systemctl start docker
    
    # Añadir usuario actual a grupo docker (si no es root)
    if [ "$SUDO_USER" ]; then
        usermod -aG docker "$SUDO_USER"
        log INFO "Usuario $SUDO_USER añadido al grupo docker"
    fi
    
    log SUCCESS "Docker instalado: $(docker --version)"
}

install_docker_compose() {
    log INFO "Instalando Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        log INFO "Docker Compose ya está instalado: $(docker-compose --version)"
        return 0
    fi
    
    # Instalar docker-compose standalone
    local compose_version="2.24.0"
    curl -SL "https://github.com/docker/compose/releases/download/v${compose_version}/docker-compose-linux-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    
    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    log SUCCESS "Docker Compose instalado: $(docker-compose --version)"
}

configure_firewall() {
    log INFO "Configurando firewall (UFW)..."
    
    # Habilitar UFW
    ufw --force enable
    
    # Permitir SSH (importante para no perder acceso)
    ufw allow 22/tcp comment 'SSH'
    
    # Permitir puertos de la aplicación
    ufw allow 80/tcp comment 'HTTP'
    ufw allow 443/tcp comment 'HTTPS'
    ufw allow 5173/tcp comment 'Frontend Dev'
    ufw allow 8000/tcp comment 'API Gateway'
    
    # Opcional: Permitir puertos de servicios individuales para debugging
    # ufw allow 8001:8006/tcp comment 'Microservices'
    
    ufw reload
    
    log SUCCESS "Firewall configurado"
    log INFO "Puertos abiertos: 22 (SSH), 80 (HTTP), 443 (HTTPS), 5173 (Frontend), 8000 (API Gateway)"
}

setup_directories() {
    log INFO "Creando directorios del proyecto..."
    
    mkdir -p /opt/basmati
    mkdir -p /opt/basmati-backups
    mkdir -p /var/log
    
    # Permisos
    if [ "$SUDO_USER" ]; then
        chown -R "$SUDO_USER:$SUDO_USER" /opt/basmati
        chown -R "$SUDO_USER:$SUDO_USER" /opt/basmati-backups
    fi
    
    touch /var/log/basmati-deploy.log
    chmod 644 /var/log/basmati-deploy.log
    
    log SUCCESS "Directorios creados"
}

configure_docker_daemon() {
    log INFO "Optimizando configuración de Docker..."
    
    cat > /etc/docker/daemon.json <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "default-address-pools": [
    {
      "base": "172.80.0.0/16",
      "size": 24
    }
  ]
}
EOF
    
    systemctl restart docker
    
    log SUCCESS "Docker daemon configurado"
}

setup_swap() {
    log INFO "Configurando memoria swap (recomendado para instancias pequeñas)..."
    
    # Verificar si ya existe swap
    if swapon --show | grep -q "/swapfile"; then
        log INFO "Swap ya está configurado"
        return 0
    fi
    
    # Crear archivo swap de 2GB
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    
    # Hacer permanente
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    
    log SUCCESS "Swap de 2GB configurado"
}

install_monitoring_tools() {
    log INFO "Instalando herramientas de monitoreo..."
    
    apt-get install -y -qq \
        net-tools \
        iotop \
        iftop \
        ncdu
    
    log SUCCESS "Herramientas de monitoreo instaladas"
}

print_next_steps() {
    echo ""
    log INFO "=========================================="
    log SUCCESS "¡Configuración inicial completada!"
    log INFO "=========================================="
    echo ""
    log INFO "Próximos pasos:"
    echo ""
    log INFO "1. Clona el repositorio:"
    log INFO "   cd /opt/basmati"
    log INFO "   git clone <tu-repositorio> ."
    echo ""
    log INFO "2. Copia el archivo .env de producción:"
    log INFO "   scp .env.production user@server:/opt/basmati/app/.env"
    echo ""
    log INFO "3. Ejecuta el despliegue:"
    log INFO "   sudo bash /opt/basmati/deployment/deploy.sh"
    echo ""
    log INFO "4. (Opcional) Configura SSL con Let's Encrypt"
    echo ""
    log WARNING "IMPORTANTE: Si no eres root, cierra sesión y vuelve a entrar"
    log WARNING "para que los cambios del grupo docker tengan efecto"
    echo ""
    log INFO "=========================================="
}

main() {
    log INFO "Iniciando configuración de EC2 para Basmati..."
    
    check_root
    check_system_requirements
    update_system
    install_docker
    install_docker_compose
    configure_docker_daemon
    configure_firewall
    setup_directories
    setup_swap
    install_monitoring_tools
    print_next_steps
    
    log SUCCESS "¡Setup completado!"
}

main "$@"
