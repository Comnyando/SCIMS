# CI/CD Setup Guide

This document explains the CI/CD pipeline and how to use it.

## Overview

The project uses GitHub Actions for continuous integration. The pipeline runs on every push and pull request to `main` and `develop` branches.

## CI Pipeline Jobs

### Backend Jobs

1. **Backend Linting (Black)**
   - Checks Python code formatting
   - Runs: `black --check --diff app/`

2. **Backend Type Checking (mypy)**
   - Type checks Python code
   - Runs: `mypy app/ --ignore-missing-imports`

3. **Backend Tests**
   - Runs pytest test suite
   - Generates coverage reports
   - Uploads coverage to Codecov (if configured)

### Frontend Jobs

1. **Frontend Linting (ESLint)**
   - Lints TypeScript/React code
   - Runs: `pnpm lint`

2. **Frontend Type Checking**
   - Type checks TypeScript code
   - Runs: `pnpm exec tsc --noEmit`

3. **Frontend Build**
   - Builds the production bundle
   - Verifies the build succeeds
   - Runs: `pnpm build`

### Docker Jobs

1. **Docker Backend Build**
   - Builds backend Docker image
   - Tests multi-stage build process

2. **Docker Frontend Build**
   - Builds frontend Docker image
   - Tests production build

3. **Docker Compose Build Test**
   - Tests full docker-compose build
   - Verifies all services can be built together

## Running Checks Locally

### Backend

```bash
cd backend

# Install dev dependencies
pip install -r requirements-dev.txt

# Format code
black app/

# Lint code
ruff check app/

# Type check
mypy app/

# Run tests
pytest tests/
```

### Frontend

```bash
cd frontend

# Install dependencies
pnpm install

# Lint
pnpm lint

# Type check
pnpm type-check

# Build
pnpm build
```

## Pre-commit Hooks

Pre-commit hooks run automatically before each commit. See [.pre-commit-install.md](../.pre-commit-install.md) for setup instructions.

### Manual Run

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files
pre-commit run
```

## CI Workflow Configuration

The CI workflow is defined in `.github/workflows/ci.yml`. Key features:

- Runs on push to `main` and `develop` branches
- Runs on pull requests to `main` and `develop`
- Uses caching for faster builds
- Jobs can fail without blocking (some use `continue-on-error: true` during setup)

## GitHub Secrets (Optional)

You can configure these secrets in GitHub for enhanced functionality:

- `VITE_API_URL` - Frontend API URL (defaults to localhost)
- `VITE_WS_URL` - WebSocket URL (defaults to localhost)

## Troubleshooting

### CI Job Fails

1. **Linting failures:**
   - Run the linter locally: `black app/` or `pnpm lint`
   - Fix issues and commit

2. **Type checking failures:**
   - Run type checker locally: `mypy app/` or `pnpm type-check`
   - Fix type errors

3. **Test failures:**
   - Run tests locally: `pytest tests/`
   - Check test output for failures

4. **Docker build failures:**
   - Test build locally: `docker compose build`
   - Check Dockerfile syntax

### Pre-commit Hooks Not Running

```bash
# Reinstall hooks
pre-commit install --hook-type pre-commit

# Run manually to verify
pre-commit run --all-files
```

## Next Steps

- [ ] Configure Codecov integration (optional)
- [ ] Set up deployment workflows
- [ ] Add security scanning
- [ ] Configure branch protection rules to require CI passes

