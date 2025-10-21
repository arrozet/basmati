#!/bin/bash

# =============================================================================
# Script de despliegue para PRODUCCIÓN
# Levanta el entorno de producción optimizado
# =============================================================================

set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}🚀 Basmati - Producción${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Error: No se encuentra docker-compose.yml${NC}"
    echo -e "${YELLOW}💡 Este script debe ejecutarse desde el directorio app/${NC}"
    exit 1
fi

# Verificar que existe .env
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: No se encuentra el archivo .env${NC}"
    echo -e "${YELLOW}📝 Por favor, copia .env.example a .env y configura tus credenciales${NC}"
    echo -e "${YELLOW}   cp .env.example .env${NC}"
    exit 1
fi

# Advertencia de producción
echo -e "${YELLOW}  ADVERTENCIA: Estás a punto de desplegar en modo PRODUCCIÓN${NC}"
echo -e "${YELLOW}   - Sin hot-reload${NC}"
echo -e "${YELLOW}   - Imagen optimizada${NC}"
echo -e "${YELLOW}   - Health checks activados${NC}"
echo ""
read -p "¿Continuar? (s/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${YELLOW}❌ Despliegue cancelado${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE} Construyendo imagen de producción...${NC}"
docker-compose build

echo ""
echo -e "${BLUE} Levantando contenedores...${NC}"
docker-compose up -d

echo ""
echo -e "${GREEN} Entorno de producción iniciado!${NC}"
echo ""
echo -e "${BLUE} Servicios disponibles:${NC}"
echo -e "   • API: ${GREEN}http://localhost:8000${NC}"
echo -e "   • Docs (Swagger): ${GREEN}http://localhost:8000/docs${NC}"
echo -e "   • ReDoc: ${GREEN}http://localhost:8000/redoc${NC}"
echo ""
echo -e "${BLUE} Comandos útiles:${NC}"
echo -e "   • Ver logs: ${YELLOW}docker-compose logs -f${NC}"
echo -e "   • Detener: ${YELLOW}docker-compose down${NC}"
echo -e "   • Ver estado: ${YELLOW}docker-compose ps${NC}"
echo -e "   • Health check: ${YELLOW}curl http://localhost:8000/health${NC}"
echo ""
echo -e "${YELLOW} Recuerda: En producción no hay hot-reload. Para ver cambios, reconstruye la imagen.${NC}"
echo ""
