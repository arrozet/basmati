# 🔧 Fix: Módulo shared no encontrado en Lambda

## ❌ Error Encontrado

Después del primer deployment, las funciones Lambda fallaban con:

```json
{
  "errorMessage": "Unable to import module 'lambda_handler': No module named 'shared'",
  "errorType": "Runtime.ImportModuleError"
}
```

## 🔍 Causa del Problema

SAM empaqueta cada `CodeUri` de forma **independiente**. 

En `template.yaml`:
```yaml
ApiGatewayFunction:
  CodeUri: app/backend/api-gateway/  # Solo empaqueta este directorio
```

El código de `api-gateway/main.py` importa:
```python
from shared.config import Settings  # ❌ 'shared' no está en api-gateway/
```

El directorio `shared/` está en `app/backend/shared/`, pero **no se incluye** en el paquete de Lambda.

## ✅ Solución Aplicada

### Opción 1: Copiar shared a cada servicio (IMPLEMENTADA)

```bash
cd /home/drlk/basmati/app/backend
for service in api-gateway user_service calendar_service event_service notification_service integration_service; do
    cp -r shared "$service/"
done
```

Ahora cada servicio tiene su propia copia de `shared/`:
```
app/backend/
├── api-gateway/
│   ├── shared/          ← Copia
│   ├── main.py
│   └── lambda_handler.py
├── user_service/
│   ├── shared/          ← Copia
│   ├── main.py
│   └── lambda_handler.py
└── shared/              ← Original
```

### Ventajas y Desventajas

**✅ Pros:**
- Simple y directo
- Funciona inmediatamente
- No require cambios en template.yaml

**⚠️ Contras:**
- Duplicación de código
- Si actualizas `shared/`, debes copiar de nuevo
- Mayor tamaño de deployment

## 🔄 Alternativas

### Opción 2: Lambda Layers (MÁS LIMPIO)

Crear un Lambda Layer con el código compartido:

```yaml
# template.yaml
Resources:
  SharedLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: basmati-shared
      Description: Código compartido entre servicios
      ContentUri: app/backend/shared/
      CompatibleRuntimes:
        - python3.11
  
  ApiGatewayFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: app/backend/api-gateway/
      Layers:
        - !Ref SharedLayer  # Agregar layer
```

**Pro**: Sin duplicación, updates centralizados  
**Contra**: Requiere cambios en template y redeploy

### Opción 3: Symlinks en build

Crear symlinks antes del build:

```bash
cd app/backend/api-gateway && ln -s ../shared shared
```

**Pro**: No duplica archivos localmente  
**Contra**: SAM puede no seguir symlinks correctamente

## 📋 Pasos de Re-deployment

Después del fix:

```bash
# 1. Copiar shared a todos los servicios
cd /home/drlk/basmati/app/backend
for service in api-gateway user_service calendar_service event_service notification_service integration_service; do
    cp -r shared "$service/"
done

# 2. Rebuild
cd /home/drlk/basmati
sam build --use-container

# 3. Redeploy
./deploy.sh
```

## 🎯 Recomendación Futura

**Migrar a Lambda Layers** para evitar duplicación:

1. Crear layer con `shared/`
2. Actualizar `template.yaml`
3. Redeploy
4. Eliminar copias de `shared/` en cada servicio

Esto mantiene el código DRY y facilita actualizaciones.

## ✅ Estado Actual

- ✅ `shared/` copiado a todos los servicios
- ✅ Build completado
- 🔄 Redeploy en progreso
- ⏳ Pruebas pendientes

## 🧪 Verificación

Después del redeploy:

```bash
curl https://e37x0pucbh.execute-api.eu-north-1.amazonaws.com/prod/health

# Debería retornar:
# {"status": "healthy", "service": "api-gateway"}
```
