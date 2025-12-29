# ========================================
# Build Stage
# ========================================
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* pnpm-lock.yaml* ./

# Install dependencies (use npm since pnpm might not be available)
RUN npm install

# Copy source code
COPY . .

# Build arguments - estas variables se inyectan en el build
ARG VITE_API_GATEWAY_URL
ARG VITE_DEV_USER_1_EMAIL
ARG VITE_DEV_USER_2_EMAIL

# Exportar como ENV para que Vite las lea durante el build
ENV VITE_API_GATEWAY_URL=$VITE_API_GATEWAY_URL
ENV VITE_DEV_USER_1_EMAIL=$VITE_DEV_USER_1_EMAIL
ENV VITE_DEV_USER_2_EMAIL=$VITE_DEV_USER_2_EMAIL

# Build de producción (Vite embebe las variables en el JS)
RUN npm run build

# ========================================
# Production Stage
# ========================================
FROM nginx:alpine

# Copiar los archivos compilados
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuración personalizada de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

