# 🚀 Guía de Deployment AWS Lambda

Esta guía explica cómo desplegar la aplicación Basmati en AWS Lambda usando SAM (Serverless Application Model).

## 📋 Prerequisitos

### Software Requerido

1. **AWS CLI**
   ```bash
   pip install awscli
   aws configure
   ```

2. **SAM CLI**
   ```bash
   pip install aws-sam-cli
   ```

3. **Docker Desktop**
   - Necesario para builds locales con SAM
   - Descarga desde: https://www.docker.com/products/docker-desktop

4. **Node.js y npm**
   - Para build del frontend
   - Versión recomendada: 18.x o superior

### Configuración AWS

1. Configura tus credenciales de AWS:
   ```bash
   aws configure
   ```
   
2. Asegúrate de tener permisos para:
   - Lambda
   - API Gateway
   - S3
   - CloudFormation
   - IAM (para crear roles)

### Variables de Entorno

El archivo `app/.env` ya contiene todas las credenciales necesarias:

```bash
# Ya configurado en app/.env:
MONGO_URI=mongodb+srv://...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=eu-north-1
# Y más...
```

**No necesitas crear `.env.local`** - el archivo `app/.env` ya existe y será usado automáticamente por los scripts.

## 🚀 Deployment a AWS

### Paso 1: Preparar el proyecto

```bash
# Asegúrate de estar en la raíz del proyecto
cd /ruta/a/basmati
```

### Paso 2: Ejecutar el script de deployment

```bash
./deploy.sh
```

El script hará automáticamente:

1. ✅ Verificar instalación de AWS CLI y SAM CLI
2. ✅ Crear bucket S3 para artefactos SAM (si no existe)
3. ✅ Build de todas las funciones Lambda con SAM
4. ✅ Deploy del stack de CloudFormation
5. ✅ Build del frontend con Vite
6. ✅ Subir el frontend a S3 con static website hosting
7. ✅ Mostrar las URLs finales

### Paso 3: Verificar el deployment

Al finalizar, verás algo como:

```
========================================
✅ Deployment completado!
========================================

📱 Frontend URL: http://basmati-frontend-xyz.s3-website-us-east-1.amazonaws.com
🔌 API URL:      https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/
```

## 🧪 Pruebas Locales con SAM

Para probar las funciones Lambda localmente antes de desplegar:

```bash
./test-local.sh
```

Esto iniciará un servidor local en `http://localhost:3000` que simula API Gateway.

- **API Base:** http://localhost:3000
- **Documentación:** http://localhost:3000/docs

## 📦 Arquitectura del Deployment

### Backend (AWS Lambda)

Cada microservicio se despliega como una función Lambda independiente:

| Servicio | Ruta | Descripción |
|----------|------|-------------|
| API Gateway | `/` | Punto de entrada principal |
| User Service | `/user/*` | Gestión de usuarios |
| Calendar Service | `/calendar/*` | Gestión de calendarios |
| Event Service | `/event/*` | Gestión de eventos |
| Notification Service | `/notification/*` | Sistema de notificaciones |
| Integration Service | `/integration/*` | Integraciones externas |

### Frontend (S3 Static Website)

El frontend se despliega como un sitio web estático en S3:
- Build con Vite
- Variables de entorno configuradas automáticamente
- Public read access

## 💰 Estimación de Costos

### AWS Free Tier (12 meses)

- **Lambda:** 1M invocaciones gratis/mes + 400,000 GB-segundos
- **API Gateway:** 1M llamadas gratis/mes
- **S3:** 5GB almacenamiento gratis
- **Data Transfer:** 15GB salida gratis/mes

### Más allá del Free Tier

Estimación para 10,000 usuarios/mes:
- **Lambda:** ~$5-10/mes
- **API Gateway:** ~$3/mes
- **S3:** ~$1/mes
- **Total:** ~$9-14/mes

> **Nota:** MongoDB Atlas tiene un tier gratuito (M0) con 512MB de almacenamiento.

## 🔧 Troubleshooting

### Error: "SAM CLI no está instalado"

```bash
pip install aws-sam-cli
```

### Error: "Docker no está corriendo"

Inicia Docker Desktop o el daemon de Docker:
```bash
sudo systemctl start docker  # Linux
# O abre Docker Desktop en Mac/Windows
```

### Error: "Bucket name already exists"

El nombre del bucket S3 debe ser único globalmente. El script te pedirá un nombre personalizado.

### Error de build del frontend

Asegúrate de tener las dependencias instaladas:
```bash
cd app/frontend
npm install
```

### Lambda timeout

Si las funciones tardan demasiado, puedes aumentar el timeout en [template.yaml](template.yaml):

```yaml
Globals:
  Function:
    Timeout: 60  # Aumentar de 30 a 60 segundos
```

## 🔄 Actualizar el Deployment

Para actualizar la aplicación después de hacer cambios:

```bash
./deploy.sh
```

SAM detectará los cambios y actualizará solo los recursos modificados.

## 🗑️ Eliminar el Stack

Para eliminar todos los recursos de AWS:

```bash
sam delete --stack-name basmati-app --region us-east-1
```

Luego elimina manualmente el bucket del frontend:
```bash
aws s3 rb s3://tu-bucket-frontend --force
```

## 📚 Recursos Adicionales

- [Documentación de SAM](https://docs.aws.amazon.com/serverless-application-model/)
- [Mangum - ASGI adapter for Lambda](https://mangum.io/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [S3 Static Website Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs de CloudWatch:
   ```bash
   sam logs --stack-name basmati-app --tail
   ```

2. Verifica el estado del stack:
   ```bash
   aws cloudformation describe-stacks --stack-name basmati-app
   ```

3. Revisa la documentación de AGENTS.md para detalles de arquitectura
