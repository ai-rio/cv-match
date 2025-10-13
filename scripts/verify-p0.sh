#!/bin/bash

# P0 Verification Automation Script
# This script automates as much of the P0 verification checklist as possible

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Helper functions
print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED++))
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED++))
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Start verification
print_header "P0 VERIFICATION SCRIPT - CV-Match"
echo "Starting automated verification..."
echo "Date: $(date)"
echo ""

# 1. Infrastructure Health Check
print_header "1️⃣  INFRASTRUCTURE HEALTH CHECK"

# Check Docker services
print_info "Checking Docker services..."
if docker compose ps | grep -q "Up"; then
    print_success "Docker Compose services are running"
    docker compose ps --format "table {{.Name}}\t{{.Status}}"
else
    print_error "Docker Compose services not running properly"
    docker compose ps
fi

# Check backend service
print_info "Testing backend service..."
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
    print_success "Backend health endpoint responding"
    echo "   Response: $HEALTH_RESPONSE"
else
    print_error "Backend health endpoint not responding"
fi

# Check frontend service
print_info "Testing frontend service..."
if curl -s -f http://localhost:3000 > /dev/null 2>&1; then
    print_success "Frontend service responding"
else
    print_warning "Frontend service not responding (may not be running)"
fi

# 2. Database Connectivity
print_header "2️⃣  DATABASE CONNECTIVITY"

print_info "Testing Supabase connection..."
if docker compose exec -T backend python -c "
from app.core.database import get_supabase_client
try:
    client = get_supabase_client()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
" 2>/dev/null; then
    print_success "Database connection successful"
else
    print_error "Database connection failed"
fi

# 3. Backend Services
print_header "3️⃣  BACKEND SERVICES"

print_info "Checking backend service imports..."
if docker compose exec -T backend python -c "
import sys
success = True

services = [
    'app.services.resume_service',
    'app.services.job_service',
    'app.services.score_improvement_service',
    'app.services.text_extraction',
    'app.agent.manager'
]

for service in services:
    try:
        __import__(service)
        print(f'✅ {service}')
    except ImportError as e:
        print(f'❌ {service}: {e}')
        success = False

sys.exit(0 if success else 1)
" 2>/dev/null; then
    print_success "All backend services importable"
else
    print_error "Some backend services failed to import"
fi

# 4. Backend Tests
print_header "4️⃣  BACKEND UNIT TESTS"

print_info "Running backend unit tests..."
cd backend
if docker compose exec -T backend python -m pytest tests/unit/ -v --tb=short 2>&1 | tee /tmp/pytest_output.log; then
    TEST_COUNT=$(grep -c "PASSED" /tmp/pytest_output.log || echo "0")
    print_success "Backend tests passed ($TEST_COUNT tests)"
else
    print_error "Some backend tests failed"
fi
cd ..

# 5. Security Tests
print_header "5️⃣  SECURITY MIDDLEWARE"

print_info "Running security tests..."
cd backend
if docker compose exec -T backend python -m pytest tests/unit/test_security_middleware.py -v 2>&1 | grep -q "passed"; then
    print_success "Security middleware tests passed"
else
    print_error "Security middleware tests failed"
fi
cd ..

# 6. Frontend Build
print_header "6️⃣  FRONTEND BUILD"

print_info "Testing frontend build..."
cd frontend
if bun run build > /tmp/frontend_build.log 2>&1; then
    print_success "Frontend builds successfully"
else
    print_error "Frontend build failed"
    echo "   Check /tmp/frontend_build.log for details"
fi
cd ..

# 7. Internationalization
print_header "7️⃣  INTERNATIONALIZATION"

print_info "Checking i18n configuration..."

# Check next-intl installation
if [ -f frontend/package.json ] && grep -q "next-intl" frontend/package.json; then
    print_success "next-intl installed"
else
    print_error "next-intl not found in package.json"
fi

# Check locale files
PTBR_FILES=$(find frontend/locales/pt-br -name "*.json" 2>/dev/null | wc -l)
EN_FILES=$(find frontend/locales/en -name "*.json" 2>/dev/null | wc -l)

if [ "$PTBR_FILES" -gt 0 ]; then
    print_success "PT-BR locale files found ($PTBR_FILES files)"
else
    print_error "PT-BR locale files missing"
fi

if [ "$EN_FILES" -gt 0 ]; then
    print_success "EN locale files found ($EN_FILES files)"
else
    print_error "EN locale files missing"
fi

# 8. Environment Variables
print_header "8️⃣  ENVIRONMENT CONFIGURATION"

print_info "Checking backend environment variables..."
REQUIRED_BACKEND_VARS=(
    "RESUME_MATCHER_LLM_PROVIDER"
    "RESUME_MATCHER_LLM_MODEL"
    "SUPABASE_URL"
    "SUPABASE_SERVICE_KEY"
)

for var in "${REQUIRED_BACKEND_VARS[@]}"; do
    if grep -q "^$var=" backend/.env 2>/dev/null; then
        print_success "Backend: $var configured"
    else
        print_warning "Backend: $var not found in .env"
    fi
done

print_info "Checking frontend environment variables..."
REQUIRED_FRONTEND_VARS=(
    "NEXT_PUBLIC_DEFAULT_LOCALE"
    "NEXT_PUBLIC_API_URL"
    "NEXT_PUBLIC_SUPABASE_URL"
)

for var in "${REQUIRED_FRONTEND_VARS[@]}"; do
    if grep -q "^$var=" frontend/.env.local 2>/dev/null || grep -q "^$var=" frontend/.env 2>/dev/null; then
        print_success "Frontend: $var configured"
    else
        print_warning "Frontend: $var not found in .env"
    fi
done

# 9. Sentry Integration
print_header "9️⃣  ERROR TRACKING (SENTRY)"

print_info "Testing Sentry integration..."
if docker compose exec -T backend python -c "
import os
if os.getenv('SENTRY_DSN'):
    import sentry_sdk
    print('✅ Sentry configured')
else:
    print('⚠️  SENTRY_DSN not set')
" 2>/dev/null | grep -q "configured"; then
    print_success "Sentry integration configured"
else
    print_warning "Sentry DSN not configured (optional)"
fi

# 10. Performance Check
print_header "🔟 PERFORMANCE BENCHMARKS"

print_info "Testing health endpoint response time..."
START_TIME=$(date +%s%N)
curl -s http://localhost:8000/health > /dev/null 2>&1
END_TIME=$(date +%s%N)
RESPONSE_TIME=$(( (END_TIME - START_TIME) / 1000000 ))

if [ "$RESPONSE_TIME" -lt 100 ]; then
    print_success "Health endpoint response time: ${RESPONSE_TIME}ms (< 100ms target)"
else
    print_warning "Health endpoint response time: ${RESPONSE_TIME}ms (target: < 100ms)"
fi

# Summary Report
print_header "📊 VERIFICATION SUMMARY"

TOTAL_CHECKS=$((PASSED + FAILED + WARNINGS))

echo ""
echo -e "${GREEN}✅ Passed:   $PASSED${NC}"
echo -e "${RED}❌ Failed:   $FAILED${NC}"
echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "   Total:    $TOTAL_CHECKS"
echo ""

# Calculate success rate
SUCCESS_RATE=$((PASSED * 100 / TOTAL_CHECKS))
echo "Success Rate: $SUCCESS_RATE%"
echo ""

# Final recommendation
if [ "$FAILED" -eq 0 ]; then
    if [ "$WARNINGS" -eq 0 ]; then
        echo -e "${GREEN}🎉 All checks passed! Ready to proceed to P1.${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️  All critical checks passed, but there are warnings.${NC}"
        echo -e "${YELLOW}   Review warnings before proceeding to P1.${NC}"
        exit 0
    fi
else
    echo -e "${RED}❌ Some checks failed. Please fix issues before proceeding to P1.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review failed checks above"
    echo "2. Fix the issues"
    echo "3. Re-run this script"
    echo "4. See docs/development/P0-VERIFICATION-CHECKLIST.md for detailed manual verification"
    exit 1
fi
