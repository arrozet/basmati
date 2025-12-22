# 🧪 Eventos de Prueba para SAM Local

Este directorio contiene eventos de ejemplo para probar funciones Lambda localmente.

## Uso

### Con el script test-local.sh
```bash
./test-local.sh
# Selecciona opción 2 (Invocar función específica)
```

### Manual
```bash
# Health check
sam local invoke ApiGatewayFunction -e test-events/health-check.json

# Get users
sam local invoke UserServiceFunction -e test-events/get-users.json

# Create user
sam local invoke UserServiceFunction -e test-events/create-user.json
```

## Estructura de Eventos

Los eventos siguen el formato de AWS Lambda para HTTP API Gateway:

```json
{
  "httpMethod": "GET|POST|PUT|DELETE",
  "path": "/ruta/del/endpoint",
  "headers": {
    "Content-Type": "application/json"
  },
  "queryStringParameters": {
    "param": "value"
  },
  "body": "JSON string (solo para POST/PUT)",
  "isBase64Encoded": false
}
```

## Crear Nuevos Eventos

Copia uno de los archivos existentes y modifica según necesites:

```bash
cp test-events/health-check.json test-events/mi-test.json
nano test-events/mi-test.json
```

## Eventos Disponibles

- `health-check.json` - GET /health
- `get-users.json` - GET /v1/users
- `create-user.json` - POST /v1/users

Añade más según necesites para probar diferentes endpoints.
