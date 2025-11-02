#!/bin/bash
# Helper script to create developer user in Docker container
# Usage: ./scripts/create_dev_user.sh

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

echo "Creating developer user..."
echo ""

# Run the script in the backend container
$DOCKER_COMPOSE exec backend python -m scripts.create_dev_user

