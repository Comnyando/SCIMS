# Installation Guide

Complete guide for installing and setting up SCIMS for development or production.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Docker Installation (Recommended)](#docker-installation-recommended)
- [Local Development Installation](#local-development-installation)
- [Production Installation](#production-installation)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

1. **Docker & Docker Compose** (v2.0+)
   - **Windows:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - **macOS:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - **Linux:** [Docker Engine](https://docs.docker.com/engine/install/) + [Docker Compose](https://docs.docker.com/compose/install/)

2. **Git**
   - Download from [git-scm.com](https://git-scm.com/downloads)

### Optional (for local development without Docker)

- **Python 3.11+** for backend development
- **Node.js 20+** and **pnpm 9+** for frontend development
- **PostgreSQL 15+** if running database locally
- **Redis 7+** if running Redis locally

## Docker Installation (Recommended)

This is the easiest way to get started and ensures a consistent environment.

### Step 1: Clone the Repository

```bash
git clone https://github.com/Comnyando/SCIMS.git
cd SCIMS
```

### Step 2: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your preferred settings (optional for development)
# Default values work for local development
```

### Step 3: Start the Application

```bash
# Start all services
docker compose up --build

# Or start in detached mode (background)
docker compose up --build -d
```

### Step 4: Verify Installation

Once all containers are running, verify access:

- **Frontend:** http://localhost
- **Backend API:** http://localhost/api/v1
- **API Docs:** http://localhost/api/docs
- **Health Check:** http://localhost/api/v1/health

### Step 5: View Logs (if needed)

```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f nginx
```

## Local Development Installation

For development without Docker, you'll need to run services individually.

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment:**
   ```bash
   cp ../.env.example .env
   # Edit .env with local database and Redis URLs
   ```

5. **Ensure PostgreSQL and Redis are running:**
   - PostgreSQL should be accessible
   - Redis should be accessible

6. **Run database migrations (when available):**
   ```bash
   alembic upgrade head
   ```

7. **Start the backend:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install pnpm (if not installed):**
   ```bash
   npm install -g pnpm
   # Or
   corepack enable
   corepack prepare pnpm@latest --activate
   ```

3. **Install dependencies:**
   ```bash
   pnpm install
   ```

4. **Set up environment:**
   ```bash
   # Create .env.local file
   echo "VITE_API_URL=http://localhost:8000/api/v1" > .env.local
   echo "VITE_WS_URL=ws://localhost:8000/ws" >> .env.local
   ```

5. **Start the frontend:**
   ```bash
   pnpm dev
   ```

The frontend will be available at `http://localhost:5173`

### Database Setup (Local PostgreSQL)

If running PostgreSQL locally:

1. **Install PostgreSQL 15+**

2. **Create database:**
   ```sql
   CREATE DATABASE scims;
   CREATE USER scims WITH PASSWORD 'scims';
   GRANT ALL PRIVILEGES ON DATABASE scims TO scims;
   ```

3. **Update `.env`:**
   ```env
   DATABASE_URL=postgresql+psycopg://scims:scims@localhost:5432/scims
   ```

### Redis Setup (Local Redis)

If running Redis locally:

1. **Install Redis 7+**

2. **Start Redis:**
   ```bash
   # Linux/macOS
   redis-server

   # Windows (using WSL or Docker)
   # Or download from: https://github.com/microsoftarchive/redis/releases
   ```

3. **Update `.env`:**
   ```env
   REDIS_URL=redis://localhost:6379/0
   CELERY_BROKER_URL=redis://localhost:6379/1
   ```

## Production Installation

For production deployment, see the production Docker Compose configuration.

### Step 1: Prepare Environment

```bash
# Copy and configure environment file
cp .env.example .env

# Generate secure secrets
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))"

# Update .env with:
# - Secure SECRET_KEY and JWT_SECRET
# - Production database credentials
# - Production CORS origins
# - ENVIRONMENT=production
```

### Step 2: Start Production Services

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

### Step 3: Set Up SSL (Optional)

For HTTPS in production:

1. Configure SSL certificates in `nginx/ssl/`
2. Update `nginx/default.conf` with SSL settings
3. Restart nginx: `docker compose restart nginx`

See [Nginx SSL Configuration](../deployment/ssl.md) for details.

## Verification

### Health Checks

1. **Backend Health:**
   ```bash
   curl http://localhost/api/v1/health
   # Should return: {"status": "healthy"}
   ```

2. **Frontend:**
   - Open http://localhost in browser
   - Should see the SCIMS application

3. **Database Connection:**
   ```bash
   docker compose exec backend python -c "from app.database import engine; print('DB Connected' if engine else 'DB Error')"
   ```

4. **Redis Connection:**
   ```bash
   docker compose exec redis redis-cli ping
   # Should return: PONG
   ```

### Service Status

```bash
# Check all services are running
docker compose ps

# Should show all services as "Up"
```

## Troubleshooting

### Port Already in Use

If you get port conflicts:

1. **Check what's using the port:**
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/macOS
   lsof -i :8000
   ```

2. **Change ports in `.env`:**
   ```env
   BACKEND_PORT=8001
   FRONTEND_PORT=5174
   NGINX_HTTP_PORT=8080
   ```

### Docker Build Failures

```bash
# Clean Docker cache and rebuild
docker compose down
docker system prune -a
docker compose build --no-cache
docker compose up
```

### Database Connection Issues

1. **Verify PostgreSQL is running:**
   ```bash
   docker compose ps db
   ```

2. **Check database logs:**
   ```bash
   docker compose logs db
   ```

3. **Verify connection string in `.env`**

### Frontend Not Loading

1. **Check frontend logs:**
   ```bash
   docker compose logs frontend
   ```

2. **Verify environment variables:**
   ```bash
   docker compose exec frontend env | grep VITE_
   ```

3. **Check Nginx configuration:**
   ```bash
   docker compose exec nginx nginx -t
   ```

### Permission Issues (Linux/macOS)

If you encounter permission issues with Docker volumes:

```bash
# Fix ownership
sudo chown -R $USER:$USER .
```

## Next Steps

After successful installation:

1. Review the [Backend README](../../backend/README.md) for backend-specific setup
2. Review the [Frontend README](../../frontend/README.md) for frontend-specific setup
3. Check the [Implementation Roadmap](../../planning/implementation-roadmap.md) for development tasks
4. Explore the [API Documentation](http://localhost/api/docs) when the backend is running

## Getting Help

If you encounter issues not covered here:

1. Check the logs: `docker compose logs -f`
2. Review the [Architecture Documentation](../../planning/architecture.md)
3. Open an issue on GitHub with:
   - Your operating system
   - Docker version: `docker --version`
   - Error messages from logs
   - Steps to reproduce

