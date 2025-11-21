FROM node:18-alpine

WORKDIR /app

# Copy package files first for better caching
COPY package.json ./
# In case package-lock.json doesn't exist yet (using npm install without lock file if needed, or just copy if exists)
COPY package.json package-lock.jso[n] ./

RUN npm install

# Copy the rest of the frontend code
COPY . .

# Expose Vite default port
EXPOSE 5173

# Run dev server accessible from outside the container
CMD ["npm", "run", "dev", "--", "--host"]

