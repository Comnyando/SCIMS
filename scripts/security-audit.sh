#!/bin/bash
# Security audit script for SCIMS backend
# Runs dependency vulnerability scans and basic security checks

set -e

echo "=========================================="
echo "SCIMS Security Audit"
echo "=========================================="
echo ""

cd backend || exit 1

echo "1. Checking Python dependencies for vulnerabilities..."
echo ""

# Check if safety is installed
if ! command -v safety &> /dev/null; then
    echo "Installing safety for vulnerability scanning..."
    pip install safety
fi

# Run safety check
echo "Running safety check..."
safety check --json || safety check

echo ""
echo "2. Checking for known security issues in code..."
echo ""

# Check for common security anti-patterns
echo "Scanning for SQL injection risks..."
if grep -r "execute.*%" app/ --include="*.py" | grep -v "# SECURITY:"; then
    echo "WARNING: Potential SQL injection risks found (raw string formatting in SQL)"
else
    echo "✓ No obvious SQL injection risks found"
fi

echo ""
echo "Scanning for hardcoded secrets..."
if grep -ri "password.*=.*['\"][^'\"]\{8,\}" app/ --include="*.py" | grep -v "# TEST" | grep -v "hash_password"; then
    echo "WARNING: Potential hardcoded passwords found"
else
    echo "✓ No hardcoded passwords found"
fi

echo ""
echo "Scanning for debug mode in production code..."
if grep -ri "debug.*=.*true" app/ --include="*.py" -i; then
    echo "WARNING: Debug mode may be enabled"
else
    echo "✓ No debug mode found"
fi

echo ""
echo "3. Checking authentication implementation..."
echo ""

# Check for proper password hashing
if grep -r "hash_password\|bcrypt\|argon2" app/core/security.py; then
    echo "✓ Password hashing is implemented"
else
    echo "WARNING: Password hashing may not be properly implemented"
fi

# Check for JWT token validation
if grep -r "decode_token\|verify_token" app/core/security.py; then
    echo "✓ JWT token validation is implemented"
else
    echo "WARNING: JWT token validation may not be properly implemented"
fi

echo ""
echo "4. Checking CORS configuration..."
echo ""

if grep -r "CORSMiddleware" app/main.py; then
    echo "✓ CORS middleware is configured"
else
    echo "WARNING: CORS middleware may not be configured"
fi

echo ""
echo "5. Checking rate limiting..."
echo ""

if grep -r "RateLimitMiddleware" app/main.py; then
    echo "✓ Rate limiting middleware is configured"
else
    echo "WARNING: Rate limiting may not be configured"
fi

echo ""
echo "6. Checking security headers..."
echo ""

if grep -r "SecurityHeadersMiddleware\|X-Frame-Options\|Content-Security-Policy" app/; then
    echo "✓ Security headers middleware is configured"
else
    echo "WARNING: Security headers may not be configured"
fi

echo ""
echo "=========================================="
echo "Security Audit Complete"
echo "=========================================="
echo ""
echo "For comprehensive security testing, consider:"
echo "- Running OWASP ZAP or Burp Suite for penetration testing"
echo "- Using bandit for static code analysis: pip install bandit && bandit -r app/"
echo "- Reviewing OWASP Top 10 vulnerabilities"
echo "- Conducting manual security testing"

