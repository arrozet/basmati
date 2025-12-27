# 🚀 Deployment de Basmati a AWS Lambda

Esta carpeta contiene todo lo necesario para desplegar la aplicación Basmati en AWS Lambda.

## 📁 Estructura

```
deployment/
├── scripts/
│   ├── deploy-final.sh          # Script principal de deployment
│   ├── cleanup-aws.sh            # Eliminar todos los recursos de AWS
│   └── logs.sh                   # Ver logs de las funciones Lambda
├── config/
│   ├── template.yaml             # Template SAM de CloudFormation
│   └── s3-website-config.json    # Configuración de S3 para SPA
└── README.md                     # Este archivo
```

## 🎯 Script Principal: deploy-final.sh

### ¿Qué hace?

1. **Preparación**
   - Valida configuración (`.env`, credenciales AWS)
   - Copia módulo `shared/` a todos los servicios
   - Configura bucket S3 para frontend

2. **Backend**
   - Build con SAM
   - Deploy de 7 funciones Lambda:
     - API Gateway
     - Auth Service (OAuth Google/Facebook)
     - User Service
     - Calendar Service
     - Event Service
     - Notification Service
     - Integration Service

3. **Frontend**
   - Copia variables `VITE_*` desde `app/.env` a `app/frontend/.env.production`
   - Build con Vite
   - Deploy a S3
   - Configura S3 para SPA (todas las rutas → index.html)

4. **Verificación**
   - Health check del API Gateway
   - Muestra URLs de acceso

### Uso

```bash
# Desde la raíz del proyecto
./deployment/scripts/deploy-final.sh

# O desde cualquier lugar
cd /ruta/a/basmati
./deployment/scripts/deploy-final.sh
```

### Requisitos Previos

1. **AWS CLI configurado**
   ```bash
   aws configure
   # Configurar: Access Key ID, Secret Access Key, Región (eu-north-1)
   ```

2. **Archivo app/.env configurado**
   ```bash
   # Debe contener:
   - MONGO_URI
   - VITE_API_GATEWAY_URL (se actualizará automáticamente)
   - GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
   - SENDGRID_API_KEY
   ```

3. **Python 3.11+ y Node.js instalados**

### Variables de Entorno

El script usa las siguientes variables del `app/.env`:

- `MONGO_URI`: Conexión a MongoDB Atlas
- `VITE_API_GATEWAY_URL`: URL del API Gateway (se actualiza tras deployment)
- Todas las variables `VITE_*` se copian automáticamente al frontend

## 🗑️ cleanup-aws.sh

Elimina **TODOS** los recursos desplegados en AWS:

```bash
./deployment/scripts/cleanup-aws.sh
```

**⚠️ ADVERTENCIA**: Esto es **irreversible**. Eliminará:
- Stack de CloudFormation completo
- Todas las funciones Lambda
- Buckets S3 y su contenido
- API Gateway
- Roles IAM

## 📊 logs.sh

Ver logs de las funciones Lambda:

```bash
./deployment/scripts/logs.sh
```

Opciones:
1. Ver lista de funciones Lambda
2. Ver logs de una función específica
3. Ver logs de todas las funciones

## 🔧 Configuración: template.yaml

Template SAM de CloudFormation que define:

- **7 Lambda Functions** (Python 3.12, 512MB RAM, 30s timeout)
- **API Gateway REST API** con CORS habilitado
- **S3 Bucket** para frontend con static website hosting
- **IAM Roles** con permisos necesarios

### Modificar Configuración

```yaml
# En deployment/config/template.yaml

Globals:
  Function:
    Timeout: 30          # Cambiar timeout
    MemorySize: 512      # Cambiar memoria
    Runtime: python3.12  # Cambiar runtime
```

## 📋 Flujo de Deployment Completo

```
┌─────────────────────────────────────────────────────────┐
│ 1. Preparación                                          │
│    - Validar configuración                              │
│    - Copiar shared/ a servicios                         │
├─────────────────────────────────────────────────────────┤
│ 2. Build Backend                                        │
│    - SAM Build (empaqueta Lambdas)                      │
├─────────────────────────────────────────────────────────┤
│ 3. Deploy Backend                                       │
│    - CloudFormation Stack                               │
│    - 7 Lambda Functions                                 │
│    - API Gateway                                        │
│    - S3 Bucket                                          │
├─────────────────────────────────────────────────────────┤
│ 4. Configurar Frontend                                  │
│    - Copiar VITE_* desde app/.env                       │
│    - Actualizar VITE_API_GATEWAY_URL                    │
│    - Crear .env.production                              │
├─────────────────────────────────────────────────────────┤
│ 5. Build Frontend                                       │
│    - npm install                                        │
│    - vite build (inyecta variables en JS)               │
├─────────────────────────────────────────────────────────┤
│ 6. Deploy Frontend                                      │
│    - Subir dist/ a S3                                   │
│    - Configurar S3 para SPA                             │
├─────────────────────────────────────────────────────────┤
│ 7. Verificación                                         │
│    - Health check API                                   │
│    - Mostrar URLs                                       │
└─────────────────────────────────────────────────────────┘
```

## 🐛 Troubleshooting

### Error: "No module named 'shared'"

El módulo `shared/` no se copió correctamente. Solución:

```bash
cd app/backend
for service in api-gateway auth_service user_service calendar_service event_service notification_service integration_service; do
    cp -r shared "$service/"
done
```

### Error: "CORS"

Frontend apunta a `localhost:8000` en lugar del API Gateway.

```bash
# Verificar app/frontend/.env.production
cat app/frontend/.env.production
# Debe contener:
VITE_API_GATEWAY_URL=https://xxxxx.execute-api.eu-north-1.amazonaws.com/prod
```

Si no existe, el script lo creará automáticamente en el próximo deployment.

### Error 404 en rutas (/login, /dashboard)

S3 no está configurado para SPA. Ejecuta:

```bash
aws s3api put-bucket-website \
    --bucket basmati-frontend-XXXXXXXXXX \
    --website-configuration file://deployment/config/s3-website-config.json
```

O re-ejecuta `deploy-final.sh` (lo hace automáticamente).

### Build lento

SAM usa containers Docker por defecto. Si no tienes Docker:

```bash
# Editar deployment/scripts/deploy-final.sh
# Cambiar: sam build --use-container
# Por:     sam build
```

## 💰 Costos Estimados

Con **AWS Free Tier**:

- **Lambda**: Gratis (1M invocaciones/mes, 400K GB-segundos)
- **API Gateway**: ~$3.50/millón de requests (primeros 333M gratis primer año)
- **S3**: ~$0.023/GB/mes (5GB gratis primer año)
- **CloudFormation**: Gratis

**Total estimado**: **~$0/mes** dentro del Free Tier

## 📚 Recursos Desplegados

Después del deployment, se crean estos recursos en AWS:

| Recurso | Cantidad | Descripción |
|---------|----------|-------------|
| Lambda Functions | 7 | API Gateway, Auth, User, Calendar, Event, Notification, Integration |
| API Gateway | 1 | REST API con rutas para cada servicio |
| S3 Bucket | 1 | Frontend estático con website hosting |
| IAM Roles | 7 | Uno por cada función Lambda |
| CloudWatch Logs | 7 | Log groups para cada Lambda |
| CloudFormation Stack | 1 | Gestiona todos los recursos |

## 🔐 Seguridad

- **Credenciales**: Se usan desde `aws configure`, no hardcodeadas
- **Secrets**: MongoDB URI pasado como parámetro seguro (NoEcho)
- **.gitignore**: Archivos sensibles excluidos (.env, .aws-sam/)
- **IAM**: Permisos mínimos necesarios por función

## 📖 Más Información

- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [AWS Lambda Pricing](https://aws.amazon.com/lambda/pricing/)
- [S3 Static Website Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
