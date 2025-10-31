# Local CI Check Script
# Runs the same checks as GitHub Actions CI pipeline locally

param(
    [switch]$BackendOnly = $false,
    [switch]$FrontendOnly = $false,
    [switch]$DockerOnly = $false,
    [switch]$SkipDocker = $false
)

$ErrorActionPreference = "Continue"
$failed = @()
$passed = @()

function Write-Status {
    param(
        [string]$Message,
        [string]$Status = "INFO"
    )
    
    $color = switch ($Status) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
        "WARN" { "Yellow" }
        default { "Cyan" }
    }
    
    Write-Host "[$Status] $Message" -ForegroundColor $color
}

function Test-BackendLint {
    Write-Status "Running backend linting (Black)..." "INFO"
    
    Push-Location backend
    try {
        # Check if Black is installed
        $blackCheck = python -m black --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Status "Installing Black..." "WARN"
            pip install black==24.10.0 | Out-Null
        }
        
        # Run Black check
        python -m black --check --diff app/ 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Backend linting passed" "PASS"
            $script:passed += "Backend Lint"
            return $true
        } else {
            Write-Status "Backend linting failed - run 'black app/' to fix" "FAIL"
            $script:failed += "Backend Lint"
            return $false
        }
    } finally {
        Pop-Location
    }
}

function Test-BackendTypeCheck {
    Write-Status "Running backend type checking (mypy)..." "INFO"
    
    Push-Location backend
    try {
        # Check if mypy is installed
        $mypyCheck = python -m mypy --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Status "Installing mypy..." "WARN"
            pip install mypy==1.11.1 | Out-Null
        }
        
        # Run mypy
        python -m mypy app/ --ignore-missing-imports 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Backend type checking passed" "PASS"
            $script:passed += "Backend Type Check"
            return $true
        } else {
            Write-Status "Backend type checking failed" "FAIL"
            $script:failed += "Backend Type Check"
            return $false
        }
    } finally {
        Pop-Location
    }
}

function Test-BackendTests {
    Write-Status "Running backend tests..." "INFO"
    
    Push-Location backend
    try {
        # Install requirements first
        Write-Status "Installing backend dependencies..." "INFO"
        pip install -q -r requirements.txt 2>&1 | Out-Null
        
        # Check if pytest is installed
        $pytestCheck = python -m pytest --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Status "Installing pytest..." "WARN"
            pip install -q pytest pytest-cov pytest-asyncio httpx 2>&1 | Out-Null
        }
        
        # Run tests
        python -m pytest tests/ -v --cov=app 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Backend tests passed" "PASS"
            $script:passed += "Backend Tests"
            return $true
        } else {
            Write-Status "Backend tests failed" "FAIL"
            $script:failed += "Backend Tests"
            return $false
        }
    } finally {
        Pop-Location
    }
}

function Test-FrontendLint {
    Write-Status "Running frontend linting (ESLint)..." "INFO"
    
    Push-Location frontend
    try {
        # Detect package manager
        $pkgMgr = "npm"
        if (Get-Command pnpm -ErrorAction SilentlyContinue) {
            $pkgMgr = "pnpm"
        } elseif (Get-Command yarn -ErrorAction SilentlyContinue) {
            $pkgMgr = "yarn"
        }
        
        # Check if node_modules exists
        if (-not (Test-Path node_modules)) {
            Write-Status "Installing frontend dependencies with $pkgMgr..." "WARN"
            if ($pkgMgr -eq "pnpm") {
                & pnpm install --frozen-lockfile 2>&1 | Out-Null
            } elseif ($pkgMgr -eq "yarn") {
                & yarn install 2>&1 | Out-Null
            } else {
                & npm install 2>&1 | Out-Null
            }
        }
        
        # Run ESLint
        if ($pkgMgr -eq "pnpm") {
            & pnpm lint 2>&1
        } elseif ($pkgMgr -eq "yarn") {
            & yarn lint 2>&1
        } else {
            & npm run lint 2>&1
        }
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Frontend linting passed" "PASS"
            $script:passed += "Frontend Lint"
            return $true
        } else {
            Write-Status "Frontend linting failed" "FAIL"
            $script:failed += "Frontend Lint"
            return $false
        }
    } finally {
        Pop-Location
    }
}

function Test-FrontendTypeCheck {
    Write-Status "Running frontend type checking (TypeScript)..." "INFO"
    
    Push-Location frontend
    try {
        # Detect package manager
        $pkgMgr = "npm"
        if (Get-Command pnpm -ErrorAction SilentlyContinue) {
            $pkgMgr = "pnpm"
        } elseif (Get-Command yarn -ErrorAction SilentlyContinue) {
            $pkgMgr = "yarn"
        }
        
        # Check if node_modules exists
        if (-not (Test-Path node_modules)) {
            Write-Status "Installing frontend dependencies with $pkgMgr..." "WARN"
            if ($pkgMgr -eq "pnpm") {
                & pnpm install --frozen-lockfile 2>&1 | Out-Null
            } elseif ($pkgMgr -eq "yarn") {
                & yarn install 2>&1 | Out-Null
            } else {
                & npm install 2>&1 | Out-Null
            }
        }
        
        # Run TypeScript type check
        if ($pkgMgr -eq "pnpm") {
            & pnpm type-check 2>&1
        } elseif ($pkgMgr -eq "yarn") {
            & yarn type-check 2>&1
        } else {
            & npm run type-check 2>&1
        }
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Frontend type checking passed" "PASS"
            $script:passed += "Frontend Type Check"
            return $true
        } else {
            Write-Status "Frontend type checking failed" "FAIL"
            $script:failed += "Frontend Type Check"
            return $false
        }
    } finally {
        Pop-Location
    }
}

function Test-FrontendBuild {
    Write-Status "Running frontend build..." "INFO"
    
    Push-Location frontend
    try {
        # Detect package manager
        $pkgMgr = "npm"
        if (Get-Command pnpm -ErrorAction SilentlyContinue) {
            $pkgMgr = "pnpm"
        } elseif (Get-Command yarn -ErrorAction SilentlyContinue) {
            $pkgMgr = "yarn"
        }
        
        # Check if node_modules exists
        if (-not (Test-Path node_modules)) {
            Write-Status "Installing frontend dependencies with $pkgMgr..." "WARN"
            if ($pkgMgr -eq "pnpm") {
                & pnpm install --frozen-lockfile 2>&1 | Out-Null
            } elseif ($pkgMgr -eq "yarn") {
                & yarn install 2>&1 | Out-Null
            } else {
                & npm install 2>&1 | Out-Null
            }
        }
        
        # Run build
        $env:VITE_API_URL = "http://localhost:8000/api/v1"
        $env:VITE_WS_URL = "ws://localhost:8000/ws"
        if ($pkgMgr -eq "pnpm") {
            & pnpm build 2>&1
        } elseif ($pkgMgr -eq "yarn") {
            & yarn build 2>&1
        } else {
            & npm run build 2>&1
        }
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Frontend build passed" "PASS"
            $script:passed += "Frontend Build"
            return $true
        } else {
            Write-Status "Frontend build failed" "FAIL"
            $script:failed += "Frontend Build"
            return $false
        }
    } finally {
        Remove-Item Env:\VITE_API_URL -ErrorAction SilentlyContinue
        Remove-Item Env:\VITE_WS_URL -ErrorAction SilentlyContinue
        Pop-Location
    }
}

function Test-DockerBuilds {
    Write-Status "Testing Docker builds..." "INFO"
    
    try {
        # Backend Docker build
        Write-Status "Building backend Docker image..." "INFO"
        docker build -f backend/Dockerfile --target production -t scims-backend:test backend/ 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Backend Docker build passed" "PASS"
            $script:passed += "Docker Backend"
        } else {
            Write-Status "Backend Docker build failed" "FAIL"
            $script:failed += "Docker Backend"
        }
        
        # Frontend Docker build
        Write-Status "Building frontend Docker image..." "INFO"
        docker build -f frontend/Dockerfile --target production --build-arg VITE_API_URL=http://localhost:8000/api/v1 --build-arg VITE_WS_URL=ws://localhost:8000/ws -t scims-frontend:test frontend/ 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Frontend Docker build passed" "PASS"
            $script:passed += "Docker Frontend"
        } else {
            Write-Status "Frontend Docker build failed" "FAIL"
            $script:failed += "Docker Frontend"
        }
    } catch {
        Write-Status "Docker build error: $_" "FAIL"
        $script:failed += "Docker Builds"
    }
}

# Main execution
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Local CI Checks" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not $FrontendOnly -and -not $DockerOnly) {
    Write-Host "--- Backend Checks ---" -ForegroundColor Yellow
    Test-BackendLint
    Test-BackendTypeCheck
    Test-BackendTests
    Write-Host ""
}

if (-not $BackendOnly -and -not $DockerOnly) {
    Write-Host "--- Frontend Checks ---" -ForegroundColor Yellow
    Test-FrontendLint
    Test-FrontendTypeCheck
    Test-FrontendBuild
    Write-Host ""
}

if (-not $SkipDocker -and ($DockerOnly -or (-not $BackendOnly -and -not $FrontendOnly))) {
    Write-Host "--- Docker Checks ---" -ForegroundColor Yellow
    Test-DockerBuilds
    Write-Host ""
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Passed: $($passed.Count)" -ForegroundColor Green
$passed | ForEach-Object { Write-Host "  [PASS] $_" -ForegroundColor Green }
Write-Host ""
Write-Host "Failed: $($failed.Count)" -ForegroundColor Red
$failed | ForEach-Object { Write-Host "  [FAIL] $_" -ForegroundColor Red }
Write-Host ""

if ($failed.Count -eq 0) {
    Write-Host "All checks passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Some checks failed. Please fix the errors above." -ForegroundColor Red
    exit 1
}

