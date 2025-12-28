# Índice de Documentación de Despliegue

Documentación completa para desplegar Basmati en AWS EC2 con Docker.

## 📄 Archivos de Documentación

### Guías Principales

1. **[README.md](./README.md)** - Guía principal de despliegue
   - Instalación rápida
   - Configuración paso a paso
   - Comandos útiles
   - Troubleshooting básico

2. **[DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)** - Lista de verificación completa
   - Checklist pre-despliegue
   - Pasos detallados
   - Post-despliegue
   - Contactos de emergencia

3. **[SECURITY.md](./SECURITY.md)** - Guía de seguridad
   - Mejores prácticas
   - Configuración segura
   - Gestión de secretos
   - Incident response

4. **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Resolución de problemas
   - Problemas comunes y soluciones
   - Comandos de debug
   - Procedimientos de recuperación

## 🔧 Scripts de Despliegue

### Scripts Principales

- **`setup-ec2.sh`** - Configuración inicial del servidor EC2
  - Instala Docker y dependencias
  - Configura firewall
  - Optimiza sistema
  - **Ejecutar una sola vez** al preparar el servidor

- **`deploy.sh`** - Script principal de despliegue
  - Build de imágenes
  - Despliegue con health checks
  - Rollback automático en caso de error
  - **Ejecutar cada vez que despliegues**

- **`pre-deployment-check.sh`** - Verificación pre-despliegue
  - Verifica dependencias
  - Valida configuración
  - Comprueba recursos
  - **Ejecutar antes del primer despliegue**

### Scripts Auxiliares

- **`quick-deploy.sh`** - Despliegue rápido para desarrollo
  - Sin health checks extensivos
  - Para testing rápido
  - **NO usar en producción**

- **`update-and-deploy.sh`** - Actualización desde Git
  - Pull de última versión
  - Despliegue automático
  - Para CI/CD manual

- **`monitor.sh`** - Monitor de servicios
  - Estado de contenedores
  - Health checks
  - Uso de recursos

- **`setup-nginx.sh`** - Configuración de Nginx + SSL
  - Reverse proxy
  - Certificados Let's Encrypt
  - **Opcional**: Solo si usas dominio

## 📝 Archivos de Configuración

- **`.env.production.template`** - Template de variables de entorno
  - Copiar a `.env` y completar valores
  - Variables requeridas documentadas
  - Nunca commitear `.env` real

- **`docker-compose.prod.yml`** - Configuración de producción
  - Health checks
  - Restart policies
  - Límites de recursos
  - Usar con: `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d`

## 🚀 Flujo de Despliegue Completo

### Primera Vez (Setup Inicial)

```bash
# 1. Conectar al servidor EC2
ssh -i key.pem ubuntu@IP_SERVIDOR

# 2. Ejecutar setup (una sola vez)
cd /opt
sudo git clone <repo-url> basmati
cd basmati
sudo bash deployment/setup-ec2.sh

# 3. Configurar variables de entorno
cd /opt/basmati/app
sudo cp ../deployment/.env.production.template .env
sudo nano .env  # Completar valores

# 4. Verificar configuración
sudo bash /opt/basmati/deployment/pre-deployment-check.sh

# 5. Desplegar
sudo bash /opt/basmati/deployment/deploy.sh

# 6. (Opcional) Configurar SSL
sudo bash /opt/basmati/deployment/setup-nginx.sh tu-dominio.com
```

### Actualizaciones

```bash
# Opción 1: Manual
cd /opt/basmati
sudo git pull origin main
sudo bash deployment/deploy.sh

# Opción 2: Script automático
sudo bash /opt/basmati/deployment/update-and-deploy.sh main
```

### Monitoreo

```bash
# Ver estado
bash /opt/basmati/deployment/monitor.sh

# Ver logs
cd /opt/basmati/app
docker-compose logs -f

# Ver logs de servicio específico
docker-compose logs -f api-gateway
```

## 📊 Arquitectura de Despliegue

```
┌─────────────────────────────────────────────────────────┐
│                     AWS EC2 Instance                    │
│                    (Ubuntu 22.04)                       │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │              Docker Network (bridge)               │ │
│  │                                                      │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │ │
│  │  │  Frontend   │  │ API Gateway │  │   User     │ │ │
│  │  │  (Vite)     │  │  (FastAPI)  │  │  Service   │ │ │
│  │  │  :5173      │  │   :8000     │  │   :8001    │ │ │
│  │  └─────────────┘  └─────────────┘  └────────────┘ │ │
│  │                           │                         │ │
│  │  ┌──────────────────┬─────┴───┬──────────────────┐ │ │
│  │  │                  │         │                  │ │ │
│  │  │  Calendar   Event   Notification   Auth      │ │ │
│  │  │  Service    Service    Service     Service   │ │ │
│  │  │  :8002      :8003      :8004        :8005    │ │ │
│  │  │                                    Integration│ │ │
│  │  │                                     Service   │ │ │
│  │  │                                      :8006    │ │ │
│  │  └────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  Nginx (Opcional - con SSL)                             │
│  ├─ :80/:443 → Frontend (:5173)                         │
│  └─ api.domain :80/:443 → API Gateway (:8000)           │
└─────────────────────────────────────────────────────────┘
                    │              │
                    ▼              ▼
          ┌──────────────┐  ┌──────────────┐
          │  MongoDB     │  │   AWS S3     │
          │   Atlas      │  │   Bucket     │
          │  (Cloud)     │  │  (Uploads)   │
          └──────────────┘  └──────────────┘
```

## 🔐 Seguridad

Ver [SECURITY.md](./SECURITY.md) para detalles completos.

Resumen de mejores prácticas:
- ✅ Variables sensibles en `.env` (no commitear)
- ✅ JWT secrets fuertes (32+ bytes)
- ✅ MongoDB whitelist configurado
- ✅ Firewall (UFW) habilitado
- ✅ SSL/HTTPS con Let's Encrypt
- ✅ Contenedores con límites de recursos
- ✅ Backups automáticos
- ✅ Logs rotados

## 🆘 Ayuda Rápida

### Problemas Comunes

1. **Health check falla:**
   ```bash
   docker-compose logs | grep -i error
   ```

2. **MongoDB no conecta:**
   - Verificar IP en whitelist de Atlas
   - Verificar MONGO_URI en .env

3. **CORS errors:**
   - Verificar FRONTEND_URL en .env
   - Verificar configuración CORS en API Gateway

4. **SSL no funciona:**
   - Verificar DNS propagado: `nslookup tu-dominio.com`
   - Verificar certificados: `sudo certbot certificates`

Ver [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) para soluciones detalladas.

## 📞 Soporte

- Issues: GitHub Issues del repositorio
- Logs: `/var/log/basmati-deploy.log`
- Documentación: Este directorio (`/deployment/`)

## 🔄 Changelog

### v1.0.0 (2024-12-28)
- Setup inicial de scripts de despliegue
- Configuración de EC2
- Documentación completa
- Scripts de monitoreo y mantenimiento
