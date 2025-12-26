"""
Cliente para comunicación entre servicios Lambda
Soporta invocación directa de Lambda (producción) y HTTP (desarrollo local)
"""
import boto3
import json
import os
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class LambdaServiceClient:
    """Cliente para invocar otras funciones Lambda directamente"""
    
    def __init__(self):
        self.lambda_client = boto3.client('lambda') if self._is_lambda_environment() else None
        self.is_local = not self._is_lambda_environment()
        
    def _is_lambda_environment(self) -> bool:
        """Detecta si estamos corriendo en Lambda o localmente"""
        return 'AWS_LAMBDA_FUNCTION_NAME' in os.environ
    
    def invoke_service(
        self, 
        function_arn_or_url: str, 
        method: str, 
        path: str, 
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Invoca otra función Lambda o hace una llamada HTTP según el entorno
        
        Args:
            function_arn_or_url: ARN de Lambda (prod) o URL HTTP (local)
            method: Método HTTP (GET, POST, PUT, DELETE, etc.)
            path: Ruta del endpoint (ej: /v1/users/123)
            body: Cuerpo de la petición (opcional)
            headers: Headers HTTP (opcional)
        
        Returns:
            Respuesta del servicio parseada
            
        Raises:
            Exception: Si hay error en la invocación
        """
        if self.is_local or function_arn_or_url.startswith('http'):
            # Modo local: usar HTTP
            return self._invoke_http(function_arn_or_url, method, path, body, headers)
        else:
            # Modo producción: usar Lambda invocation
            return self._invoke_lambda(function_arn_or_url, method, path, body, headers)
    
    def _invoke_lambda(
        self,
        function_arn: str,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]],
        headers: Optional[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Invoca Lambda function directamente"""
        logger.info(f"Invoking Lambda: {function_arn} {method} {path}")
        
        # Construir payload en formato API Gateway event
        payload = {
            'httpMethod': method,
            'path': path,
            'headers': headers or {},
            'queryStringParameters': {},
            'body': json.dumps(body) if body else None
        }
        
        try:
            response = self.lambda_client.invoke(
                FunctionName=function_arn,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            # Leer respuesta
            result = json.loads(response['Payload'].read())
            
            # Verificar errores de Lambda
            if 'FunctionError' in response:
                error_msg = result.get('errorMessage', 'Unknown Lambda error')
                logger.error(f"Lambda error: {error_msg}")
                raise Exception(f"Lambda invocation error: {error_msg}")
            
            # Mangum devuelve un objeto con statusCode y body
            if 'statusCode' in result:
                status_code = result['statusCode']
                
                if status_code >= 400:
                    error_body = result.get('body', 'Unknown error')
                    logger.error(f"Service returned error {status_code}: {error_body}")
                    raise Exception(f"Service error ({status_code}): {error_body}")
                
                # Parse body si es JSON string
                body_content = result.get('body', '{}')
                if isinstance(body_content, str):
                    try:
                        return json.loads(body_content)
                    except json.JSONDecodeError:
                        return {'data': body_content}
                return body_content
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to invoke Lambda {function_arn}: {str(e)}")
            raise
    
    def _invoke_http(
        self,
        base_url: str,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]],
        headers: Optional[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Hace llamada HTTP (para desarrollo local)"""
        try:
            import httpx
        except ImportError:
            raise ImportError("httpx is required for HTTP calls. Install it with: pip install httpx")
        
        # Si base_url es un ARN, no podemos hacer HTTP (error de configuración)
        if base_url.startswith('arn:aws:lambda:'):
            raise Exception(
                f"Cannot make HTTP call to Lambda ARN: {base_url}. "
                "Set proper HTTP URLs for local development."
            )
        
        url = f"{base_url.rstrip('/')}{path}"
        logger.info(f"HTTP request: {method} {url}")
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.request(
                    method=method,
                    url=url,
                    json=body if body else None,
                    headers=headers or {}
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise Exception(f"HTTP error ({e.response.status_code}): {e.response.text}")
        except Exception as e:
            logger.error(f"Failed to make HTTP request to {url}: {str(e)}")
            raise


# Singleton pattern
_lambda_client: Optional[LambdaServiceClient] = None


def get_lambda_client() -> LambdaServiceClient:
    """Obtiene instancia singleton del cliente Lambda"""
    global _lambda_client
    if _lambda_client is None:
        _lambda_client = LambdaServiceClient()
    return _lambda_client


# Helper functions para casos de uso comunes
def invoke_get(service_arn_or_url: str, path: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Helper para GET request"""
    return get_lambda_client().invoke_service(service_arn_or_url, 'GET', path, headers=headers)


def invoke_post(
    service_arn_or_url: str, 
    path: str, 
    body: Dict[str, Any], 
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Helper para POST request"""
    return get_lambda_client().invoke_service(service_arn_or_url, 'POST', path, body=body, headers=headers)


def invoke_put(
    service_arn_or_url: str, 
    path: str, 
    body: Dict[str, Any], 
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Helper para PUT request"""
    return get_lambda_client().invoke_service(service_arn_or_url, 'PUT', path, body=body, headers=headers)


def invoke_delete(
    service_arn_or_url: str, 
    path: str, 
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Helper para DELETE request"""
    return get_lambda_client().invoke_service(service_arn_or_url, 'DELETE', path, headers=headers)
