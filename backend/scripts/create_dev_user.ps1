# PowerShell helper script to create developer user in Docker container
# Usage: .\scripts\create_dev_user.ps1

# Get the backend directory
$BackendDir = Split-Path -Parent $PSScriptRoot

# Change to project root (one level up from backend)
$ProjectRoot = Split-Path -Parent $BackendDir
Set-Location $ProjectRoot

# Check if Docker is available
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Docker is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Use docker compose (try new syntax first, fallback to docker-compose)
$DockerCompose = "docker compose"
if (-not (docker compose version 2>$null)) {
    $DockerCompose = "docker-compose"
}

Write-Host "Creating developer user..." -ForegroundColor Cyan
Write-Host ""

# Run the script in the backend container
$Command = "$DockerCompose exec backend python -m scripts.create_dev_user"
Invoke-Expression $Command

