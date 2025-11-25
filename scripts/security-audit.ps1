# Security audit script for SCIMS backend (PowerShell)
# Runs dependency vulnerability scans and basic security checks

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "SCIMS Security Audit" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Push-Location backend

Write-Host "1. Checking Python dependencies for vulnerabilities..." -ForegroundColor Yellow
Write-Host ""

# Check if safety is installed
$safetyCheck = python -m safety --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing safety for vulnerability scanning..." -ForegroundColor Yellow
    pip install safety
}

# Run safety check
Write-Host "Running safety check..." -ForegroundColor Yellow
python -m safety check --json
if ($LASTEXITCODE -ne 0) {
    python -m safety check
}

Write-Host ""
Write-Host "2. Checking for known security issues in code..." -ForegroundColor Yellow
Write-Host ""

# Check for common security anti-patterns
Write-Host "Scanning for SQL injection risks..." -ForegroundColor Yellow
$sqlInjection = Select-String -Path "app\*.py" -Recurse -Pattern "execute.*%" | Where-Object { $_.Line -notmatch "# SECURITY:" }
if ($sqlInjection) {
    Write-Host "WARNING: Potential SQL injection risks found (raw string formatting in SQL)" -ForegroundColor Red
} else {
    Write-Host "✓ No obvious SQL injection risks found" -ForegroundColor Green
}

Write-Host ""
Write-Host "Scanning for hardcoded secrets..." -ForegroundColor Yellow
$hardcodedSecrets = Select-String -Path "app\*.py" -Recurse -Pattern "password.*=.*['`"][^'`"]{8,}" | Where-Object { $_.Line -notmatch "# TEST" -and $_.Line -notmatch "hash_password" }
if ($hardcodedSecrets) {
    Write-Host "WARNING: Potential hardcoded passwords found" -ForegroundColor Red
} else {
    Write-Host "✓ No hardcoded passwords found" -ForegroundColor Green
}

Write-Host ""
Write-Host "Scanning for debug mode in production code..." -ForegroundColor Yellow
$debugMode = Select-String -Path "app\*.py" -Recurse -Pattern "debug.*=.*true" -CaseSensitive:$false
if ($debugMode) {
    Write-Host "WARNING: Debug mode may be enabled" -ForegroundColor Red
} else {
    Write-Host "✓ No debug mode found" -ForegroundColor Green
}

Write-Host ""
Write-Host "3. Checking authentication implementation..." -ForegroundColor Yellow
Write-Host ""

# Check for proper password hashing
$passwordHashing = Select-String -Path "app\core\security.py" -Pattern "hash_password|bcrypt|argon2"
if ($passwordHashing) {
    Write-Host "✓ Password hashing is implemented" -ForegroundColor Green
} else {
    Write-Host "WARNING: Password hashing may not be properly implemented" -ForegroundColor Red
}

# Check for JWT token validation
$jwtValidation = Select-String -Path "app\core\security.py" -Pattern "decode_token|verify_token"
if ($jwtValidation) {
    Write-Host "✓ JWT token validation is implemented" -ForegroundColor Green
} else {
    Write-Host "WARNING: JWT token validation may not be properly implemented" -ForegroundColor Red
}

Write-Host ""
Write-Host "4. Checking CORS configuration..." -ForegroundColor Yellow
Write-Host ""

$cors = Select-String -Path "app\main.py" -Pattern "CORSMiddleware"
if ($cors) {
    Write-Host "✓ CORS middleware is configured" -ForegroundColor Green
} else {
    Write-Host "WARNING: CORS middleware may not be configured" -ForegroundColor Red
}

Write-Host ""
Write-Host "5. Checking rate limiting..." -ForegroundColor Yellow
Write-Host ""

$rateLimit = Select-String -Path "app\main.py" -Pattern "RateLimitMiddleware"
if ($rateLimit) {
    Write-Host "✓ Rate limiting middleware is configured" -ForegroundColor Green
} else {
    Write-Host "WARNING: Rate limiting may not be configured" -ForegroundColor Red
}

Write-Host ""
Write-Host "6. Checking security headers..." -ForegroundColor Yellow
Write-Host ""

$securityHeaders = Select-String -Path "app\*.py" -Recurse -Pattern "SecurityHeadersMiddleware|X-Frame-Options|Content-Security-Policy"
if ($securityHeaders) {
    Write-Host "✓ Security headers middleware is configured" -ForegroundColor Green
} else {
    Write-Host "WARNING: Security headers may not be configured" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Security Audit Complete" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "For comprehensive security testing, consider:" -ForegroundColor Yellow
Write-Host "- Running OWASP ZAP or Burp Suite for penetration testing"
Write-Host "- Using bandit for static code analysis: pip install bandit && bandit -r app/"
Write-Host "- Reviewing OWASP Top 10 vulnerabilities"
Write-Host "- Conducting manual security testing"

Pop-Location

