# Running CI Checks Locally

Before pushing to GitHub, you can run the same CI checks locally to catch issues early.

## Prerequisites

Before running the script:
1. **Backend:** Python 3.11+ and pip installed
2. **Frontend:** Node.js 20+ and either pnpm, yarn, or npm installed
3. **Optional:** Docker installed (for Docker build tests)

The script will automatically install missing Python dependencies, but you may want to install frontend dependencies first:
```bash
cd frontend
pnpm install  # or npm install / yarn install
```

## Quick Start

Run all CI checks:
```powershell
.\scripts\ci-local.ps1
```

Run only backend checks:
```powershell
.\scripts\ci-local.ps1 -BackendOnly
```

Run only frontend checks:
```powershell
.\scripts\ci-local.ps1 -FrontendOnly
```

Run only Docker builds:
```powershell
.\scripts\ci-local.ps1 -DockerOnly
```

Skip Docker builds:
```powershell
.\scripts\ci-local.ps1 -SkipDocker
```

## What It Checks

The script runs the same checks as GitHub Actions:

### Backend Checks
1. **Linting (Black)** - Python code formatting
2. **Type Checking (mypy)** - Python type checking
3. **Tests** - pytest test suite with coverage

### Frontend Checks
1. **Linting (ESLint)** - TypeScript/React code linting
2. **Type Checking** - TypeScript type checking
3. **Build** - Production build verification

### Docker Checks
1. **Backend Docker Build** - Multi-stage Docker build
2. **Frontend Docker Build** - Production Docker build

## Manual Checks

If you prefer to run checks manually:

### Backend

```bash
cd backend

# Install dev dependencies (first time)
pip install -r requirements-dev.txt

# Linting
black --check app/
# Or format: black app/

# Type checking
mypy app/ --ignore-missing-imports

# Tests
pytest tests/ -v --cov=app
```

### Frontend

```bash
cd frontend

# Install dependencies (first time)
pnpm install

# Linting
pnpm lint
# Or auto-fix: pnpm lint --fix

# Type checking
pnpm type-check

# Build
pnpm build
```

### Docker

```bash
# Backend
docker build -f backend/Dockerfile --target production -t scims-backend:test backend/

# Frontend
docker build -f frontend/Dockerfile --target production \
  --build-arg VITE_API_URL=http://localhost:8000/api/v1 \
  --build-arg VITE_WS_URL=ws://localhost:8000/ws \
  -t scims-frontend:test frontend/
```

## Troubleshooting

### "Command not found" errors

The script will automatically install missing dependencies, but if you get errors:

**Backend:**
```bash
pip install -r backend/requirements-dev.txt
```

**Frontend:**
```bash
cd frontend
pnpm install
```

### Black formatting issues

Auto-fix formatting:
```bash
cd backend
black app/
```

### ESLint errors

Auto-fix linting issues:
```bash
cd frontend
pnpm lint --fix
```

### TypeScript errors

Check types:
```bash
cd frontend
pnpm type-check
```

Fix type errors in your code.

### Docker build failures

Check Docker is running:
```bash
docker --version
docker ps
```

Ensure Dockerfile syntax is correct and all dependencies are available.

## Pre-commit Hooks (Recommended)

For automatic checks before each commit, install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

This will run checks automatically on `git commit`. See [.pre-commit-install.md](../.pre-commit-install.md) for details.

## Integration with CI

The local script runs the same checks as GitHub Actions. If it passes locally, it should pass in CI (assuming environment differences like dependency versions are accounted for).

## Next Steps

After fixing local CI errors:
1. Commit your changes
2. Push to GitHub
3. CI will run automatically
4. Check GitHub Actions tab for results

