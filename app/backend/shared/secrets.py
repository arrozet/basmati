"""Gestión de secretos desde AWS Secrets Manager"""
import json
import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional


class SecretsManager:
    """Cliente para obtener secretos de AWS Secrets Manager"""
    
    def __init__(self, region_name: str = "eu-north-1"):
        self.region_name = region_name
        self._client = None
    
    @property
    def client(self):
        """Inicializa el cliente de Secrets Manager de forma lazy"""
        if self._client is None:
            self._client = boto3.client('secretsmanager', region_name=self.region_name)
        return self._client
    
    def get_secret(self, secret_name: str) -> Optional[str]:
        """
        Obtiene un secreto de AWS Secrets Manager
        
        Args:
            secret_name: Nombre del secreto en Secrets Manager
            
        Returns:
            El valor del secreto como string, o None si hay error
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            
            # El secreto puede estar en SecretString o SecretBinary
            if 'SecretString' in response:
                return response['SecretString']
            else:
                # Si es binario, decodificamos
                import base64
                return base64.b64decode(response['SecretBinary']).decode('utf-8')
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                print(f"Secreto no encontrado: {secret_name}")
            elif error_code == 'InvalidRequestException':
                print(f"Request inválido para secreto: {secret_name}")
            elif error_code == 'InvalidParameterException':
                print(f"Parámetro inválido para secreto: {secret_name}")
            else:
                print(f"Error obteniendo secreto {secret_name}: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado obteniendo secreto {secret_name}: {e}")
            return None


# Instancia global singleton
_secrets_manager = None


def get_secrets_manager() -> SecretsManager:
    """Obtiene la instancia global de SecretsManager"""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


def get_mongo_uri() -> Optional[str]:
    """
    Obtiene el URI de MongoDB desde Secrets Manager o variable de entorno
    
    Orden de prioridad:
    1. Variable de entorno MONGO_URI (para desarrollo local)
    2. Secrets Manager: basmati/mongo-uri (para producción en AWS)
    
    Returns:
        URI de MongoDB o None si no está configurado
    """
    # Primero intenta desde variable de entorno (desarrollo local)
    mongo_uri = os.environ.get('MONGO_URI')
    if mongo_uri:
        return mongo_uri
    
    # Si no está en env var, intenta desde Secrets Manager (producción)
    secrets_manager = get_secrets_manager()
    return secrets_manager.get_secret('basmati/mongo-uri')


def get_sendgrid_api_key() -> Optional[str]:
    """
    Obtiene la API Key de SendGrid desde Secrets Manager o variable de entorno
    
    Orden de prioridad:
    1. Variable de entorno SENDGRID_API_KEY (para desarrollo local)
    2. Secrets Manager: basmati/sendgrid-key (para producción en AWS)
    
    Returns:
        API Key de SendGrid o None si no está configurado
    """
    # Primero intenta desde variable de entorno (desarrollo local)
    api_key = os.environ.get('SENDGRID_API_KEY')
    if api_key:
        return api_key
    
    # Si no está en env var, intenta desde Secrets Manager (producción)
    secrets_manager = get_secrets_manager()
    return secrets_manager.get_secret('basmati/sendgrid-key')
