#!/bin/bash
# Helper script to run Alembic migrations in Docker container
# Usage: ./scripts/run_migrations.sh [command]
# Examples:
#   ./scripts/run_migrations.sh upgrade head
#   ./scripts/run_migrations.sh current
#   ./scripts/run_migrations.sh history

cd "$(dirname "$0")/.." || exit 1

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    exit 1
fi

# Use docker compose (newer) or docker-compose (older)
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

# Run Alembic command in the backend container
$DOCKER_COMPOSE exec backend alembic "$@"

