#!/bin/bash

##############################################################################
# Basmati - Script de Actualización desde Git
#
# Descarga la última versión del repositorio y despliega automáticamente.
#
# Uso: ./update-and-deploy.sh [branch]
# Ejemplo: ./update-and-deploy.sh main
##############################################################################

set -e

DEPLOY_DIR="/opt/basmati"
BRANCH="${1:-main}"

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -d "$DEPLOY_DIR" ]; then
    log "Clonando repositorio..."
    git clone <URL_DEL_REPO> "$DEPLOY_DIR"
fi

cd "$DEPLOY_DIR"

log "Actualizando desde Git (branch: $BRANCH)..."
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

success "Repositorio actualizado"

log "Iniciando despliegue..."
bash deployment/deploy.sh

success "¡Actualización y despliegue completados!"
