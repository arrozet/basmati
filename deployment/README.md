# Guía de Despliegue en AWS EC2

Despliegue automatizado de Basmati con Docker y Nginx.

## 🚀 Instalación Rápida

### 1. Setup Inicial del Servidor

```bash
ssh -i basmati-ssh-keys.pem ubuntu@IP_SERVIDOR
cd /opt
sudo git clone https://github.com/arrozet/basmati.git
cd basmati
sudo bash deployment/setup-ec2.sh
```

### 2. Configurar Variables

```bash
cd /opt/basmati/app
sudo cp ../deployment/.env.production.template .env
sudo nano .env  # Completar valores
```

**Variables críticas:**
- `MONGO_URI` - Connection string de MongoDB Atlas
- `GOOGLE_CLIENT_ID/SECRET` - Credenciales OAuth
- `AWS_ACCESS_KEY_ID/SECRET` - Credenciales AWS S3
- `SENDGRID_API_KEY` - API key de SendGrid
- `JWT_SECRET_KEY` - Generar con: `openssl rand -hex 32`

### 3. Desplegar

```bash
cd /opt/basmati
sudo bash deployment/deploy.sh
```

El script automáticamente:
- ✅ Crea backup
- ✅ Build de imágenes (con caché)
- ✅ Inicia servicios
- ✅ Health checks
- ✅ Configura Nginx como reverse proxy
- ✅ Rollback si falla

**URLs finales:**
- Frontend: `http://TU_IP`
- API: `http://TU_IP/api`
- Docs: `http://TU_IP/api/docs`

## 📦 Estructura Simplificada

```
deployment/
├── setup-ec2.sh              # Setup inicial (ejecutar 1 vez)
├── deploy.sh                 # Despliegue completo + Nginx
├── monitor.sh                # Monitor de servicios
├── diagnose-deployment-failure.sh  # Debug
├── .env.production.template  # Template de variables
├── docker-compose.prod.yml   # Config producción
├── README.md                 # Esta guía
└── TROUBLESHOOTING.md        # Resolución de problemas
```

## 🔧 Comandos Útiles

```bash
# Actualizar y redesplegar
cd /opt/basmati
sudo git pull origin main
sudo bash deployment/deploy.sh

# Ver estado
bash deployment/monitor.sh

# Ver logs
docker-compose logs -f
docker-compose logs -f api-gateway

# Diagnosticar problemas
sudo bash deployment/diagnose-deployment-failure.sh

# Reiniciar servicio
docker-compose restart api-gateway
```

## 🔍 Troubleshooting Rápido

### Health Checks Fallan

1. **Ejecutar diagnóstico:**
   ```bash
   sudo bash deployment/diagnose-deployment-failure.sh
   ```

2. **Causa más común (80%):** IP no en MongoDB whitelist
   ```bash
   # Obtener IP
   curl ifconfig.me
   # Añadir en MongoDB Atlas → Network Access
   ```

3. **Ver logs:**
   ```bash
   docker-compose logs | grep -i error
   ```

Ver [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) para más detalles.

## ⚙️ Configuración Avanzada

### Desactivar Nginx

Si no quieres usar Nginx:
```bash
CONFIGURE_NGINX=false sudo bash deployment/deploy.sh
```

### SSL con Dominio

1. Apuntar dominio a IP del servidor
2. Editar `/etc/nginx/sites-available/basmati` y añadir configuración SSL
3. Obtener certificado: `sudo certbot --nginx -d tu-dominio.com`

## 📊 Arquitectura

```
EC2 Ubuntu 22.04
  ├─ Nginx :80 (reverse proxy)
  │   ├─ / → Frontend :5173
  │   └─ /api → API Gateway :8000
  │
  ├─ Docker Network
  │   ├─ frontend (React + Vite)
  │   ├─ api-gateway (FastAPI)
  │   ├─ auth-service
  │   ├─ user-service
  │   ├─ calendar-service
  │   ├─ event-service
  │   ├─ notification-service
  │   └─ integration-service
  │
  └─ External Services
      ├─ MongoDB Atlas
      ├─ AWS S3
      └─ SendGrid
```

## 🔒 Seguridad

- Variables sensibles en `.env` (no commitear)
- JWT secrets fuertes (32+ bytes)
- MongoDB IP whitelist
- Firewall UFW habilitado
- Contenedores con límites de recursos
- Logs rotados automáticamente

**Recomendaciones adicionales:**
```bash
# Fail2ban para SSH
sudo apt install fail2ban
sudo systemctl enable fail2ban

# Actualizaciones automáticas
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 📝 Requisitos del Servidor

- **Tipo:** t2.medium o superior
- **RAM:** Mínimo 4GB
- **Disco:** Mínimo 20GB
- **OS:** Ubuntu 22.04 LTS
- **Puertos:** 22 (SSH), 80 (HTTP), 443 (HTTPS)

---

**Tiempo total de despliegue:** 3-7 minutos  
**Versión:** 1.0.0
