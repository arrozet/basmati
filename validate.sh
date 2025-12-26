#!/bin/bash

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Pre-Deployment Validation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

errors=0
warnings=0

# Función para checks
check() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
        ((errors++))
    fi
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((warnings++))
}

info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# 1. Verificar software
echo -e "${BLUE}Software:${NC}"
command -v aws &> /dev/null
check $? "AWS CLI instalado"

command -v sam &> /dev/null
check $? "SAM CLI instalado"

command -v docker &> /dev/null
check $? "Docker instalado"

docker info &> /dev/null
check $? "Docker corriendo"

command -v node &> /dev/null
check $? "Node.js instalado"

if command -v node &> /dev/null; then
    node_version=$(node -v | cut -d 'v' -f 2 | cut -d '.' -f 1)
    if [ "$node_version" -ge 18 ]; then
        check 0 "Node.js versión >= 18"
    else
        check 1 "Node.js versión >= 18 (actual: v$node_version)"
    fi
fi

echo ""

# 2. Verificar configuración AWS
echo -e "${BLUE}Configuración AWS:${NC}"
aws sts get-caller-identity &> /dev/null
if [ $? -eq 0 ]; then
    check 0 "AWS credenciales configuradas y válidas"
    # Verificar que la región coincida
    configured_region=$(aws configure get region)
    if [ "$configured_region" = "eu-north-1" ]; then
        check 0 "Región AWS configurada correctamente (eu-north-1)"
    else
        warn "Región AWS es $configured_region, se esperaba eu-north-1. Ejecuta: ./setup-aws.sh"
    fi
else
    check 1 "AWS credenciales configuradas"
    echo -e "${YELLOW}   Ejecuta: ./setup-aws.sh${NC}"
fi

echo ""

# 3. Verificar archivos de configuración
echo -e "${BLUE}Configuración del proyecto:${NC}"
[ -f "app/.env" ]
check $? "Archivo app/.env existe"

if [ -f "app/.env" ]; then
    grep -q "MONGO_URI=" app/.env
    check $? "MONGO_URI definido en app/.env"
    
    source app/.env
    if [[ "$MONGO_URI" == *"mongodb+srv://"* ]]; then
        check 0 "MONGO_URI parece ser de Atlas (mongodb+srv://)"
    elif [[ "$MONGO_URI" == *"localhost"* ]] || [[ "$MONGO_URI" == *"127.0.0.1"* ]]; then
        check 1 "MONGO_URI es localhost (debe ser Atlas para Lambda)"
    else
        warn "MONGO_URI no parece ser de Atlas ni localhost"
    fi
fi

[ -f "template.yaml" ]
check $? "template.yaml existe"

echo ""

# 4. Verificar dependencias del backend
echo -e "${BLUE}Backend:${NC}"
backend_ok=true
for service in api-gateway user_service calendar_service event_service notification_service integration_service; do
    if [ -f "app/backend/${service}/requirements.txt" ]; then
        if grep -q "mangum" "app/backend/${service}/requirements.txt"; then
            check 0 "${service}: mangum en requirements.txt"
        else
            check 1 "${service}: mangum NO en requirements.txt"
            backend_ok=false
        fi
        
        if [ -f "app/backend/${service}/lambda_handler.py" ]; then
            check 0 "${service}: lambda_handler.py existe"
        else
            check 1 "${service}: lambda_handler.py NO existe"
            backend_ok=false
        fi
    else
        check 1 "${service}: requirements.txt NO existe"
        backend_ok=false
    fi
done

echo ""

# 5. Verificar frontend
echo -e "${BLUE}Frontend:${NC}"
[ -f "app/frontend/package.json" ]
check $? "package.json existe"

[ -f "app/frontend/vite.config.ts" ]
check $? "vite.config.ts existe"

if [ -d "app/frontend/node_modules" ]; then
    check 0 "node_modules existe"
else
    warn "node_modules no existe (se instalará durante deployment)"
fi

echo ""

# 6. Test build rápido
echo -e "${BLUE}Build test:${NC}"
info "Probando SAM build (puede tardar unos segundos)..."
sam build --use-container &> /tmp/sam_build_test.log
if [ $? -eq 0 ]; then
    check 0 "SAM build exitoso"
    rm -rf .aws-sam
else
    check 1 "SAM build falló (ver /tmp/sam_build_test.log)"
fi

echo ""

# Resumen
echo -e "${BLUE}========================================${NC}"
if [ $errors -eq 0 ]; then
    echo -e "${GREEN}✅ Todo listo para deployment!${NC}"
    echo ""
    echo -e "${GREEN}Ejecuta:${NC} ./deploy.sh"
else
    echo -e "${RED}❌ Se encontraron $errors errores${NC}"
    echo ""
    echo -e "${YELLOW}Soluciona los errores antes de continuar${NC}"
fi

if [ $warnings -gt 0 ]; then
    echo -e "${YELLOW}⚠️  $warnings advertencias encontradas${NC}"
fi
echo -e "${BLUE}========================================${NC}"

exit $errors
