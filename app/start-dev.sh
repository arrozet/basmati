#!/bin/bash

# =============================================================================
# Script de despliegue para DESARROLLO
# Levanta el entorno de desarrollo con hot-reload
# Uso: ./start-dev.sh [--no-cache|-nc]
# =============================================================================

set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  Basmati - Desarrollo${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.dev.yml" ]; then
    echo -e "${RED} Error: No se encuentra docker-compose.dev.yml${NC}"
    echo -e "${YELLOW} Este script debe ejecutarse desde el directorio app/${NC}"
    exit 1
fi

# Verificar que existe .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}  No se encuentra el archivo .env${NC}"
    echo -e "${YELLOW} Copiando .env.example a .env...${NC}"
    cp .env.example .env
    echo -e "${YELLOW} Por favor, edita .env y configura tu contraseña de MongoDB${NC}"
    echo ""
    read -p "Presiona Enter cuando hayas configurado .env..."
fi

# Verificar si se pasó el parámetro --no-cache
NO_CACHE=""
if [ "$1" == "--no-cache" ] || [ "$1" == "-nc" ]; then
    NO_CACHE="--no-cache"
    echo -e "${YELLOW} Modo sin caché activado${NC}"
    echo ""
fi

echo -e "${BLUE} Construyendo imagen de desarrollo...${NC}"
docker-compose -f docker-compose.dev.yml build $NO_CACHE

echo ""
echo -e "${BLUE} Levantando contenedores...${NC}"
docker-compose -f docker-compose.dev.yml up -d

echo ""
echo -e "${GREEN} Entorno de desarrollo iniciado!${NC}"
echo ""
echo -e "${BLUE} Servicios disponibles:${NC}"
echo -e "   • API: ${GREEN}http://localhost:8000${NC}"
echo -e "   • Docs (Swagger): ${GREEN}http://localhost:8000/docs${NC}"
echo -e "   • ReDoc: ${GREEN}http://localhost:8000/redoc${NC}"
echo ""
echo -e "${BLUE}📋 Comandos útiles:${NC}"
echo -e "   • Ver logs: ${YELLOW}docker-compose -f docker-compose.dev.yml logs -f${NC}"
echo -e "   • Detener: ${YELLOW}docker-compose -f docker-compose.dev.yml down${NC}"
echo -e "   • Reiniciar sin caché: ${YELLOW}./start-dev.sh --no-cache${NC}"
echo -e "   • Ejecutar tests: ${YELLOW}docker-compose -f docker-compose.dev.yml exec backend-api pytest tests/ -v${NC}"
echo -e "   • Shell: ${YELLOW}docker-compose -f docker-compose.dev.yml exec backend-api bash${NC}"
echo ""
