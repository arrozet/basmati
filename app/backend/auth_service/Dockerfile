FROM python:3.11-slim

WORKDIR /app

# Copiar archivos de dependencias
COPY auth_service/requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del servicio
COPY auth_service/ ./auth_service/
COPY shared/ ./shared/

# Exponer puerto
EXPOSE 8005

# Configurar PYTHONPATH para imports
ENV PYTHONPATH=/app/auth_service:/app

# Comando de inicio
CMD ["uvicorn", "auth_service.main:app", "--host", "0.0.0.0", "--port", "8005", "--reload"]
