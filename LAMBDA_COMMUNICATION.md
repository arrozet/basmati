# 🔄 Comunicación entre Servicios Lambda

## ⚠️ Cambio Importante en Variables de Entorno

Para evitar **dependencias circulares** en CloudFormation, las variables de entorno ahora contienen **ARNs de funciones Lambda** en lugar de URLs HTTP.

### Antes (Causa dependencia circular)
```python
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
# https://xxxxx.execute-api.region.amazonaws.com/prod/user
response = httpx.get(f"{USER_SERVICE_URL}/v1/users/{user_id}")
```

### Ahora (Sin dependencia circular)
```python
USER_SERVICE_FUNCTION = os.getenv("USER_SERVICE_FUNCTION")
# arn:aws:lambda:region:account:function:UserServiceFunction

# Opción 1: Invocación directa de Lambda (RECOMENDADO)
import boto3
import json

lambda_client = boto3.client('lambda')
response = lambda_client.invoke(
    FunctionName=USER_SERVICE_FUNCTION,
    InvocationType='RequestResponse',
    Payload=json.dumps({
        'httpMethod': 'GET',
        'path': f'/v1/users/{user_id}',
        'headers': {}
    })
)
result = json.loads(response['Payload'].read())

# Opción 2: Construir URL dinámicamente (SI YA ESTÁ DESPLEGADO)
# Solo funciona después del primer deployment
import os
region = os.getenv('AWS_REGION', 'eu-north-1')
api_id = os.getenv('API_GATEWAY_ID')  # Necesita ser pasado
if api_id:
    user_service_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/prod/user"
```

## 📝 Variables de Entorno por Servicio

### ApiGatewayFunction
```yaml
Environment:
  Variables:
    USER_SERVICE_FUNCTION: arn:aws:lambda:...
    CALENDAR_SERVICE_FUNCTION: arn:aws:lambda:...
    EVENT_SERVICE_FUNCTION: arn:aws:lambda:...
    NOTIFICATION_SERVICE_FUNCTION: arn:aws:lambda:...
    INTEGRATION_SERVICE_FUNCTION: arn:aws:lambda:...
```

### EventServiceFunction
```yaml
Environment:
  Variables:
    NOTIFICATION_SERVICE_FUNCTION: arn:aws:lambda:...
    CALENDAR_SERVICE_FUNCTION: arn:aws:lambda:...
```

### NotificationServiceFunction
```yaml
Environment:
  Variables:
    USER_SERVICE_FUNCTION: arn:aws:lambda:...
```

### IntegrationServiceFunction
```yaml
Environment:
  Variables:
    CALENDAR_SERVICE_FUNCTION: arn:aws:lambda:...
    EVENT_SERVICE_FUNCTION: arn:aws:lambda:...
```

## 🔧 Implementación Recomendada

### 1. Crear Cliente Lambda Helper

`app/backend/shared/lambda_client.py`:
```python
import boto3
import json
import os
from typing import Any, Dict

class LambdaServiceClient:
    """Cliente para invocar otras funciones Lambda directamente"""
    
    def __init__(self):
        self.lambda_client = boto3.client('lambda')
    
    def invoke_service(
        self, 
        function_arn: str, 
        method: str, 
        path: str, 
        body: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Invoca otra función Lambda como si fuera una llamada HTTP
        
        Args:
            function_arn: ARN de la función Lambda a invocar
            method: Método HTTP (GET, POST, etc.)
            path: Ruta del endpoint (ej: /v1/users/123)
            body: Cuerpo de la petición (opcional)
            headers: Headers HTTP (opcional)
        
        Returns:
            Respuesta del servicio
        """
        payload = {
            'httpMethod': method,
            'path': path,
            'headers': headers or {},
            'body': json.dumps(body) if body else None
        }
        
        response = self.lambda_client.invoke(
            FunctionName=function_arn,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        result = json.loads(response['Payload'].read())
        
        # Mangum devuelve un objeto con statusCode y body
        if 'statusCode' in result:
            if result['statusCode'] >= 400:
                raise Exception(f"Service error: {result.get('body', 'Unknown error')}")
            
            # Parse body si es JSON string
            body = result.get('body', '{}')
            if isinstance(body, str):
                try:
                    return json.loads(body)
                except:
                    return {'data': body}
            return body
        
        return result

# Singleton
_lambda_client = None

def get_lambda_client() -> LambdaServiceClient:
    global _lambda_client
    if _lambda_client is None:
        _lambda_client = LambdaServiceClient()
    return _lambda_client
```

### 2. Usar en los Servicios

`app/backend/event_service/services/notification_service.py`:
```python
from shared.lambda_client import get_lambda_client
import os

class NotificationService:
    def __init__(self):
        self.lambda_client = get_lambda_client()
        self.notification_function_arn = os.getenv('NOTIFICATION_SERVICE_FUNCTION')
    
    async def send_comment_notification(self, event_id: str, user_id: str, comment: str):
        """Envía notificación cuando alguien comenta un evento"""
        
        # En lugar de httpx.post(f"{NOTIFICATION_SERVICE_URL}/v1/notifications")
        result = self.lambda_client.invoke_service(
            function_arn=self.notification_function_arn,
            method='POST',
            path='/v1/notifications',
            body={
                'recipient_external_id': user_id,
                'type': 'NEW_COMMENT',
                'title': 'Nuevo comentario',
                'message': f'Comentario en evento {event_id}: {comment}',
                'related_event_id': event_id
            }
        )
        
        return result
```

## 📊 Ventajas de Invocación Lambda Directa

### ✅ Pros
- **Sin latencia de red HTTP**: Comunicación interna de AWS
- **Sin API Gateway costs**: No pagas por llamadas internas
- **Sin dependencias circulares**: CloudFormation puede resolver el stack
- **Más seguro**: No expone endpoints internos

### ⚠️ Cons
- **Acoplamiento fuerte**: Los servicios deben estar en el mismo stack
- **Debugging más complejo**: No se ven en API Gateway logs
- **Cold starts**: Cada Lambda puede tener cold start

## 🔄 Alternativa: Descubrimiento de API Gateway

Si prefieres usar HTTP (menos acoplamiento), puedes obtener la URL del API Gateway dinámicamente:

```python
import boto3
import os

def get_api_gateway_url():
    """Obtiene la URL del API Gateway dinámicamente"""
    # Opción 1: Desde variable de entorno (si se pasa en deployment)
    api_url = os.getenv('API_GATEWAY_URL')
    if api_url:
        return api_url
    
    # Opción 2: Descubrir desde CloudFormation
    cf_client = boto3.client('cloudformation')
    stack_name = os.getenv('STACK_NAME', 'basmati-app')
    region = os.getenv('AWS_REGION', 'eu-north-1')
    
    try:
        response = cf_client.describe_stacks(StackName=stack_name)
        outputs = response['Stacks'][0]['Outputs']
        
        for output in outputs:
            if output['OutputKey'] == 'ApiUrl':
                return output['OutputValue']
    except:
        pass
    
    return None

# Usar
api_url = get_api_gateway_url()
if api_url:
    user_service_url = f"{api_url}/user"
```

## 🎯 Recomendación

**Para este proyecto:** Usa **invocación directa de Lambda** porque:
1. Todos los servicios están en el mismo stack
2. Es más rápido y barato
3. Evita dependencias circulares
4. Es el patrón estándar en serverless

El cliente helper (`lambda_client.py`) hace que el cambio sea transparente para el código de negocio.

## 📝 Checklist de Migración

- [ ] Crear `shared/lambda_client.py` con el cliente helper
- [ ] Actualizar `event_service` para usar Lambda invocation
- [ ] Actualizar `notification_service` para usar Lambda invocation
- [ ] Actualizar `integration_service` para usar Lambda invocation
- [ ] Añadir `boto3` a todos los `requirements.txt` (si no está)
- [ ] Probar localmente con `test-local.sh`
- [ ] Deploy y verificar

## 🧪 Testing Local

Para testing local con SAM, el helper detectará automáticamente que está en local y usará URLs HTTP en lugar de ARNs.
