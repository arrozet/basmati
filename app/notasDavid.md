# Sam
Es el frameowrk de AWS para apps serverless, usamos la CLI para trabajar con ella, para configurar está el yaml.
- Probar localmente
- Se integra bomba con docker
- Automatización CI/CD
- Definir aplicaciones serverless

# Producción

Las imágenes de ECR para que sean seguras deben ser públicas, esto tiene un problema porque las personas pueden acceder a estos secretos de forma sencilla.

- AWS Secret Manager
Esta es mi solución aunque realmente no se si funcionará bien

```bash
aws secretsmanager list-secrets --region eu-north-1 --query 'SecretList[*].[Name,ARN]' --output table
```

VALE ES DE PAGO.
ESTOY HASTA LA POLLA DE AWS
PUTO CALVO DE LOS COJONES EL RETRASADO DEL ANORMAL DE AMAZÓN 