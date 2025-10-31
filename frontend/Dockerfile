# =============================================================================
# Stage 1: Dependencies
# =============================================================================
FROM node:20-alpine as dependencies

WORKDIR /app

# Install pnpm (using npm as fallback since corepack can be unreliable in Alpine)
RUN npm install -g pnpm@9.12.2 && \
    pnpm --version

# Copy package files
COPY package.json ./

# Install dependencies (create lockfile if it doesn't exist)
RUN pnpm install

# =============================================================================
# Stage 2: Build (for production)
# =============================================================================
FROM node:20-alpine as build

WORKDIR /app

# Install pnpm (using npm as fallback since corepack can be unreliable in Alpine)
RUN npm install -g pnpm@9.12.2 && \
    pnpm --version

# Copy package files first
COPY package.json ./

# Install dependencies fresh for build stage
RUN pnpm install

# Copy source code (explicitly copy files to avoid issues)
COPY index.html vite.config.ts tsconfig.json tsconfig.node.json ./
COPY src ./src
COPY public ./public

# Build the application
RUN pnpm build

# =============================================================================
# Stage 3: Production (serve static files with nginx)
# =============================================================================
FROM nginx:alpine as production

# Copy built files from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration for SPA
RUN echo 'server { \
    listen 80; \
    server_name _; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

# =============================================================================
# Stage 4: Development (used by docker-compose)
# =============================================================================
FROM node:20-alpine as development

WORKDIR /app

# Install pnpm (using npm as fallback since corepack can be unreliable in Alpine)
RUN npm install -g pnpm@9.12.2 && \
    pnpm --version

# Copy package files
COPY package.json ./

# Install dependencies (create lockfile if it doesn't exist)
RUN pnpm install

# Copy source code (excluding node_modules which is already installed)
COPY index.html ./
COPY vite.config.ts ./
COPY tsconfig.json tsconfig.node.json ./
COPY src ./src
COPY public ./public

EXPOSE 5173

CMD ["pnpm", "dev", "--host", "0.0.0.0"]
