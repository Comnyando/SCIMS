# PowerShell helper script to run Alembic migrations in Docker container
# Usage: .\scripts\run_migrations.ps1 [command]
# Examples:
#   .\scripts\run_migrations.ps1 upgrade head
#   .\scripts\run_migrations.ps1 current
#   .\scripts\run_migrations.ps1 history

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$AlembicArgs
)

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

# Build the command
if ($AlembicArgs.Count -eq 0) {
    Write-Host "Usage: .\scripts\run_migrations.ps1 <alembic-command> [args...]" -ForegroundColor Yellow
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\scripts\run_migrations.ps1 upgrade head" -ForegroundColor Cyan
    Write-Host "  .\scripts\run_migrations.ps1 current" -ForegroundColor Cyan
    Write-Host "  .\scripts\run_migrations.ps1 history" -ForegroundColor Cyan
    exit 1
}

# Run Alembic command in the backend container
# Use alembic directly (should work after container rebuild with requirements.txt)
$Command = "$DockerCompose exec backend alembic $($AlembicArgs -join ' ')"
Invoke-Expression $Command

