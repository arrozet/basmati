# 🚀 Deployment a AWS Lambda - Proceso Completo

## 📋 Resumen Ejecutivo

El deployment se realiza en **DOS FASES** para evitar dependencias circulares en CloudFormation:

1. **Fase 1**: Deployment inicial sin comunicación inter-servicios
2. **Fase 2**: Configurar URLs y redeployar para habilitar comunicación

---

## 🎯 Fase 1: Deployment Inicial

### Prerrequisitos

```bash
# Verificar credenciales AWS
aws sts get-caller-identity

# Verificar región
aws configure get region  # Debe ser: eu-north-1

# Verificar MongoDB URI en app/.env
grep "^MONGO_URI=" app/.env
```

### Ejecutar Deployment

```bash
./deploy.sh
```

Este script:
- ✅ Crea bucket S3 para artefactos SAM
- ✅ Construye todas las funciones Lambda
- ✅ Despliega stack de CloudFormation
- ✅ Construye y sube el frontend a S3
- ⚠️ **NO habilita comunicación inter-servicios aún**

### Output Esperado

```
========================================
✅ Deployment completado!
========================================

📱 Frontend URL: http://basmati-frontend-xxx.s3-website.eu-north-1.amazonaws.com
🔌 API URL:      https://abc123xyz.execute-api.eu-north-1.amazonaws.com/prod/

⚠️  IMPORTANTE: Comunicación entre servicios
Este es el PRIMER deployment. Las llamadas inter-servicios
(ej: Event Service → Notification Service) NO funcionarán aún.

Para habilitar comunicación entre servicios:
  1. Guarda esta URL del API Gateway: https://abc123xyz...
  2. Lee CIRCULAR_DEPENDENCY_FIX.md para instrucciones
  3. Actualiza template.yaml con la URL del API Gateway
  4. Ejecuta ./deploy.sh de nuevo
```

### ✅ ¿Qué Funciona Después de Fase 1?

- Frontend estático en S3
- Todos los endpoints del API Gateway responden
- Operaciones que NO requieren comunicación entre servicios:
  - `POST /user/v1/users` - Crear usuario
  - `GET /calendar/v1/calendars` - Listar calendarios
  - `GET /event/v1/events` - Listar eventos
  - Autenticación básica

### ❌ ¿Qué NO Funciona Después de Fase 1?

- Operaciones que requieren comunicación entre servicios:
  - Crear evento con notificación automática
  - Enviar comentarios (requiere NotificationService)
  - Integraciones externas (Google Calendar, Email)
  - Verificación de permisos entre servicios

---

## 🔧 Fase 2: Configurar Comunicación Inter-Servicios

### Opción A: Script Automático (RECOMENDADO)

```bash
./configure-inter-service-urls.sh
```

Este script:
1. Obtiene la URL del API Gateway del stack desplegado
2. Crea backup de `template.yaml`
3. Actualiza `template.yaml` con las URLs correctas
4. Muestra comando para redeployar

### Opción B: Manual

1. **Obtener URL del API Gateway**:
   ```bash
   aws cloudformation describe-stacks \
     --stack-name basmati-app \
     --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
     --output text
   ```

2. **Editar `template.yaml`**:
   
   Buscar cada función con comentario:
   ```yaml
   # No environment variables needed - uses defaults from shared/config.py
   ```
   
   Reemplazar con:
   ```yaml
   Environment:
     Variables:
       API_GATEWAY_URL: "https://tu-url-aqui.execute-api.eu-north-1.amazonaws.com/prod"
       USER_SERVICE_URL: !Sub "${API_GATEWAY_URL}/user"
       CALENDAR_SERVICE_URL: !Sub "${API_GATEWAY_URL}/calendar"
       # etc...
   ```

3. **Redeployar**:
   ```bash
   ./deploy.sh
   ```

### ✅ ¿Qué Funciona Después de Fase 2?

- ✅ **TODO**: Comunicación inter-servicios completa
- ✅ Notificaciones cuando se crea un evento
- ✅ Comentarios con notificaciones
- ✅ Integraciones con servicios externos
- ✅ Verificación de permisos cross-service

---

## 📊 Arquitectura del Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                      AWS CloudFormation                      │
│                    Stack: basmati-app                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ crea
                              ▼
         ┌────────────────────────────────────────────┐
         │         API Gateway (BasmatiApi)           │
         │  https://xxx.execute-api.region.aws.com    │
         └────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
         ┌──────────┐  ┌──────────┐  ┌──────────┐
         │  Lambda  │  │  Lambda  │  │  Lambda  │
         │   User   │  │ Calendar │  │  Event   │
         │ Service  │  │ Service  │  │ Service  │
         └──────────┘  └──────────┘  └──────────┘
                │             │             │
                └─────────────┼─────────────┘
                              │
                              ▼
                     ┌────────────────┐
                     │  MongoDB Atlas │
                     │  (MONGO_URI)   │
                     └────────────────┘

         ┌────────────────────────────────────────────┐
         │         S3 Static Website Hosting          │
         │    Frontend: React + Vite (dist/)          │
         │  http://bucket.s3-website.region.aws.com   │
         └────────────────────────────────────────────┘
```

### Flujo de Comunicación (Fase 2)

```
User Request
    │
    ▼
API Gateway (/event/v1/events)
    │
    ▼
EventServiceFunction
    │
    ├─► HTTP GET → API Gateway (/calendar/v1/calendars/{id})
    │                    │
    │                    ▼
    │             CalendarServiceFunction → MongoDB
    │
    ├─► HTTP POST → API Gateway (/notification/v1/notifications)
    │                    │
    │                    ▼
    │             NotificationServiceFunction → MongoDB
    │
    ▼
MongoDB (Event created)
```

---

## 🛠️ Comandos Útiles

### Verificar Deployment

```bash
# Ver logs de CloudFormation
sam logs -n ApiGatewayFunction --stack-name basmati-app -t

# Ver estado del stack
aws cloudformation describe-stacks --stack-name basmati-app

# Listar funciones Lambda
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `basmati`)]'

# Test endpoint
curl https://YOUR-API-URL/user/health
```

### Testing

```bash
# Test local (antes de deploy)
./test-local.sh

# Test producción
curl -X POST https://YOUR-API-URL/user/v1/users \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test123!"}'
```

### Troubleshooting

```bash
# Ver logs de una función específica
./logs.sh ApiGatewayFunction

# Validar template
sam validate --lint

# Ver errores de CloudFormation
aws cloudformation describe-stack-events \
  --stack-name basmati-app \
  --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`]'
```

### Rollback

```bash
# Eliminar stack completo
./cleanup-aws.sh

# Restaurar template desde backup
cp template.yaml.backup-TIMESTAMP template.yaml
```

---

## 💰 Costos Estimados

### Con Lambda + S3 (ACTUAL)

- **Lambda**: ~$0.20/millón requests + $0.0000166667/GB-segundo
- **API Gateway**: ~$3.50/millón requests
- **S3**: ~$0.023/GB almacenado + $0.004/10,000 GET requests
- **CloudFormation**: GRATIS
- **MongoDB Atlas**: Depende de tu plan (Free tier: $0)

**Estimado mensual (100,000 requests/mes)**: ~$1-2 USD

### Con Docker (ANTERIOR)

- **EC2 t3.medium**: ~$30/mes (24/7)
- **ECS Fargate**: ~$15-40/mes según configuración

**Ahorro**: ~90% 🎉

---

## 📚 Documentos Relacionados

- [CIRCULAR_DEPENDENCY_FIX.md](CIRCULAR_DEPENDENCY_FIX.md) - Explicación del problema de dependencia circular
- [LAMBDA_COMMUNICATION.md](LAMBDA_COMMUNICATION.md) - Alternativas de comunicación entre Lambdas
- [DEPLOYMENT.md](DEPLOYMENT.md) - Documentación técnica completa
- [SECURITY.md](SECURITY.md) - Gestión segura de credenciales
- [QUICKSTART.md](QUICKSTART.md) - Guía rápida de inicio

---

## ❓ FAQ

### ¿Por qué dos deployments?

CloudFormation no permite referencias circulares. En el primer deployment, las funciones Lambda y el API Gateway se crean sin referencias mutuas. En el segundo, agregamos las URLs hardcodeadas.

### ¿Puedo hacer un solo deployment?

Técnicamente sí, usando invocación directa de Lambda (ver [LAMBDA_COMMUNICATION.md](LAMBDA_COMMUNICATION.md)), pero requiere cambiar el código de los servicios.

### ¿Qué pasa si elimino y recreo el stack?

La URL del API Gateway cambiará. Deberás ejecutar `./configure-inter-service-urls.sh` de nuevo para actualizar las URLs.

### ¿Funciona con MongoDB local?

No, las funciones Lambda necesitan acceso a MongoDB Atlas (nube). Para desarrollo local, usa `./test-local.sh` con Docker.

### ¿Cómo actualizo el código de un servicio?

1. Edita el código en `app/backend/SERVICE_NAME/`
2. Ejecuta `./deploy.sh` (solo rebuild y redeploy, no necesita configurar URLs de nuevo)

### ¿Puedo usar mi propio dominio?

Sí, necesitas:
1. Certificado SSL en AWS Certificate Manager
2. Configurar Route 53 o tu DNS
3. Agregar Custom Domain en API Gateway

---

## ✅ Checklist de Deployment

### Pre-Deployment
- [ ] Credenciales AWS configuradas (`aws configure`)
- [ ] Usuario AWS tiene permisos (CloudFormation, Lambda, S3, API Gateway, IAM)
- [ ] Región configurada (eu-north-1)
- [ ] `MONGO_URI` configurado en `app/.env`
- [ ] SAM CLI instalado (`sam --version`)
- [ ] Node.js y npm instalados

### Fase 1
- [ ] Ejecutado `./deploy.sh`
- [ ] Stack CloudFormation creado exitosamente
- [ ] API Gateway URL obtenida
- [ ] Frontend accesible en S3

### Fase 2
- [ ] Ejecutado `./configure-inter-service-urls.sh`
- [ ] Template actualizado con URLs
- [ ] Re-ejecutado `./deploy.sh`
- [ ] Verificadas llamadas inter-servicios

### Post-Deployment
- [ ] Endpoints de health responding
- [ ] Frontend cargando correctamente
- [ ] CORS configurado
- [ ] Logs de Lambda sin errores
- [ ] Variables de entorno verificadas

---

## 🎊 ¡Listo!

Ahora tienes Basmati corriendo en AWS Lambda con costos mínimos. 🚀

Para soporte, revisa los logs con `./logs.sh FUNCTION_NAME` o consulta la documentación técnica.
