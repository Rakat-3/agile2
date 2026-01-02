FROM node:20-slim

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (will run inside container)
RUN npm install

# Copy source (though we might volume mount it later, this is good for build)
COPY . .

# Expose Vite default port
EXPOSE 5173

# Run dev server with --host to allow external access
CMD ["npm", "run", "dev", "--", "--host"]
