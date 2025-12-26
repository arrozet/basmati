# 🔧 Solución a Dependencia Circular en CloudFormation

## ❌ Problema Original

CloudFormation mostraba este error:

```
Circular dependency between resources: [IntegrationServiceFunction, 
BasmatiApiDeployment3e1fc80291, NotificationServiceFunctionNotificationApiPermissionprod, 
ApiGatewayFunctionApiProxyPermissionprod...]
```

### Causa del Error

La dependencia circular ocurría porque:

1. **ApiGatewayFunction** tenía variables de entorno que referenciaban **BasmatiApi** (API Gateway)
   ```yaml
   Environment:
     Variables:
       USER_SERVICE_URL: !Sub "https://${BasmatiApi}.execute-api..."
   ```

2. **BasmatiApi** necesitaba que **ApiGatewayFunction** existiera primero (para crear los endpoints)
   ```yaml
   Events:
     ApiProxy:
       Type: Api
       Properties:
         RestApiId: !Ref BasmatiApi  # Requiere que BasmatiApi exista
   ```

3. Esto creaba un **ciclo**: `ApiGatewayFunction` → `BasmatiApi` → `ApiGatewayFunction` 🔄

## ✅ Solución Implementada

### Opción Elegida: Remover Variables de Entorno Problemáticas

Eliminamos TODAS las variables de entorno que causaban la dependencia circular:

```yaml
# ApiGatewayFunction
# ANTES:
Environment:
  Variables:
    USER_SERVICE_FUNCTION: !GetAtt UserServiceFunction.Arn
    CALENDAR_SERVICE_FUNCTION: !GetAtt CalendarServiceFunction.Arn
    # ...

# DESPUÉS:
# No environment variables needed - uses defaults from shared/config.py
```

### ¿Cómo Funciona Ahora?

1. **Sin variables de entorno**, los servicios usan las URLs por defecto de `shared/config.py`:
   ```python
   user_service_url: str = "http://user-service:8001"
   calendar_service_url: str = "http://calendar-service:8002"
   # etc...
   ```

2. **Estas URLs no funcionan en Lambda** (porque no hay Docker containers con esos hostnames)

3. **Pero CloudFormation despliega sin errores** ✅

4. **Después del primer deployment**, podemos:
   - Obtener la URL real del API Gateway
   - Actualizar las variables de entorno
   - Redeployar con las URLs correctas

## 📋 Pasos para Deployment Completo

### 1. Primer Deployment (Sin Variables)

```bash
./deploy.sh
```

Esto desplegará todas las Lambdas y el API Gateway, pero las llamadas inter-servicios fallarán.

### 2. Obtener URL del API Gateway

Después del deployment, obtener la URL:

```bash
aws cloudformation describe-stacks \
  --stack-name basmati-app \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text
```

Output ejemplo: `https://abc123xyz.execute-api.eu-north-1.amazonaws.com/prod/`

### 3. Actualizar template.yaml con URLs

Agregar variables de entorno **usando la URL obtenida**:

```yaml
# ApiGatewayFunction
Environment:
  Variables:
    API_GATEWAY_URL: "https://abc123xyz.execute-api.eu-north-1.amazonaws.com/prod"
    USER_SERVICE_URL: !Sub "${ApiGatewayUrl}/user"
    CALENDAR_SERVICE_URL: !Sub "${ApiGatewayUrl}/calendar"
    # etc...
```

**IMPORTANTE**: Ahora no hay dependencia circular porque usamos un valor hardcodeado, no `!Ref BasmatiApi`.

### 4. Segundo Deployment (Con URLs)

```bash
./deploy.sh
```

Ahora las Lambdas tendrán las URLs correctas y la comunicación inter-servicios funcionará.

## 🎯 Alternativas Evaluadas

### Opción A: Invocación Lambda Directa (MÁS COMPLEJA)

- **Pro**: Sin latencia HTTP, más barato, sin dependencias circulares
- **Contra**: Requiere cambiar todo el código de negocio para usar `boto3.client('lambda').invoke()`
- **Estado**: Cliente helper creado en `shared/lambda_client.py` pero no implementado en servicios

### Opción B: Service Discovery con CloudFormation (MÁS LENTA)

- **Pro**: URLs dinámicas sin hardcodear
- **Contra**: Requiere segundo deployment, usa ParameterStore o DynamoDB
- **Estado**: No implementado

### Opción C: URLs Hardcodeadas tras Primer Deploy (ELEGIDA) ✅

- **Pro**: Simple, mínimos cambios, deployment rápido
- **Contra**: Requiere dos deployments
- **Estado**: **IMPLEMENTADO**

## 📝 Estado Actual

- ✅ template.yaml sin dependencias circulares
- ✅ `sam validate --lint` pasa
- ⏳ Primer deployment pendiente
- ⏳ Obtener URL del API Gateway
- ⏳ Segundo deployment con URLs correctas

## 🔍 Verificación

Para verificar que no hay dependencias circulares:

```bash
# Validar template
sam validate --lint

# Dry-run del deployment
sam deploy --no-execute-changeset
```

## 📚 Referencias

- [AWS CloudFormation Circular Dependency](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-stack.html#cfn-cloudformation-stack-parameters)
- [SAM API Gateway Integration](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-api.html)
- [Lambda Function URLs](https://docs.aws.amazon.com/lambda/latest/dg/lambda-urls.html)
