#!/bin/bash

# Script para ejecutar tests del backend API
# Uso: cd tests && ./run_tests.sh [opciones]

set -e

echo " Ejecutando tests de Basmati Backend API..."
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar si estamos en el directorio de tests
if [ ! -f "test_database.py" ]; then
    echo "❌ Error: Este script debe ejecutarse desde el directorio backend-api/tests"
    echo "💡 Uso: cd tests && ./run_tests.sh"
    exit 1
fi

# Verificar si pytest está instalado
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW} pytest no está instalado. Instalando dependencias...${NC}"
    pip install -r ../requirements-dev.txt
fi

# Ejecutar tests según argumentos
if [ "$1" == "coverage" ]; then
    echo -e "${BLUE}📊 Ejecutando tests con coverage...${NC}"
    pytest --cov=.. --cov-report=html --cov-report=term -v
    echo ""
    echo -e "${GREEN} Reporte de coverage generado en htmlcov/index.html${NC}"
elif [ "$1" == "verbose" ]; then
    echo -e "${BLUE}📝 Ejecutando tests en modo verbose...${NC}"
    pytest -v -s
elif [ "$1" == "quick" ]; then
    echo -e "${BLUE} Ejecutando tests rápidos...${NC}"
    pytest -x
else
    echo -e "${BLUE} Ejecutando todos los tests...${NC}"
    pytest -v
fi

echo ""
echo -e "${GREEN} Tests completados!${NC}"
