FROM python:3.11-slim

WORKDIR /app

# Copiar shared primero (necesario para las dependencias)
COPY shared ./shared
COPY notification_service/requirements.txt ./requirements.txt

# Instalar dependencias incluyendo shared como editable
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e ./shared && \
    pip install --no-cache-dir -r requirements.txt

# Copiar la aplicación del servicio
COPY notification_service ./

EXPOSE 8004

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
