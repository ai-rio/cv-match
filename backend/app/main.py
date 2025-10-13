import logging

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.sentry import get_sentry_config, init_sentry
from app.services.security import SecurityMiddleware

# Initialize Sentry first (before other imports)
init_sentry()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.SECURITY_LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Get Sentry configuration for app title
sentry_config = get_sentry_config()

app = FastAPI(
    title="CV-Match Backend - Brazilian SaaS",
    description="API para plataforma de matching de currículos para o mercado brasileiro",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Custom middleware to handle OPTIONS requests properly
class OptionsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return Response(status_code=200)
        return await call_next(request)


# Add OPTIONS middleware first
app.add_middleware(OptionsMiddleware)

# Add security middleware for LLM endpoints
if settings.ENABLE_RATE_LIMITING:
    logger.info("Security middleware enabled with rate limiting")
    app.add_middleware(SecurityMiddleware, enable_rate_limiting=settings.ENABLE_RATE_LIMITING)
else:
    logger.info("Security middleware enabled without rate limiting")
    app.add_middleware(SecurityMiddleware, enable_rate_limiting=False)

# Set up CORS - Expanded configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", *settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-CSRF-Token",
    ],
    expose_headers=["Content-Type", "Authorization"],
    max_age=600,  # 10 minutes cache for preflight requests
)

# Include API router
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Health check endpoint."""
    sentry_config = get_sentry_config()
    return {
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
        "security_enabled": settings.ENABLE_RATE_LIMITING,
        "sentry_enabled": sentry_config.enabled,
        "market": "brazil",
        "locale": "pt-BR",
    }


@app.get("/health/sentry")
async def sentry_health():
    """Sentry health check endpoint."""
    sentry_config = get_sentry_config()

    # Test Sentry by capturing a test message in development
    if settings.ENVIRONMENT == "development" and sentry_config.enabled:
        sentry_config.add_breadcrumb(
            message="Sentry health check accessed", category="health", level="info"
        )

    return {
        "sentry_status": "enabled" if sentry_config.enabled else "disabled",
        "environment": sentry_config.environment,
        "dsn_configured": bool(sentry_config.dsn),
        "market": "brazil",
        "traces_sample_rate": settings.SENTRY_TRACES_SAMPLE_RATE,
        "profiles_sample_rate": settings.SENTRY_PROFILES_SAMPLE_RATE,
    }


@app.get("/test/sentry-error")
async def test_sentry_error():
    """Test endpoint to trigger a Sentry error for testing (development only)."""
    if settings.ENVIRONMENT != "development":
        return {"error": "This endpoint is only available in development mode"}

    sentry_config = get_sentry_config()

    try:
        # Test exception handling
        raise ValueError("Este é um erro de teste para o Sentry - CV-Match Backend")
    except Exception as e:
        sentry_config.capture_exception(
            e, {"test_endpoint": True, "market": "brazil", "application": "cv-match-backend"}
        )
        return {
            "test_error_triggered": True,
            "error_message": str(e),
            "sentry_enabled": sentry_config.enabled,
            "message": "Erro de teste capturado pelo Sentry",
        }


@app.get("/health/security")
async def security_health():
    """Security health check endpoint."""
    return {
        "security_status": "enabled",
        "rate_limiting": settings.ENABLE_RATE_LIMITING,
        "input_sanitization": True,
        "security_logging": settings.ENABLE_SECURITY_LOGGING,
        "config": {
            "max_prompt_length": settings.MAX_PROMPT_LENGTH,
            "max_text_length": settings.MAX_TEXT_LENGTH,
            "max_query_length": settings.MAX_QUERY_LENGTH,
            "rate_limit_per_user": settings.RATE_LIMIT_PER_USER,
            "rate_limit_per_ip": settings.RATE_LIMIT_PER_IP,
            "block_system_prompts": settings.BLOCK_SYSTEM_PROMPTS,
            "block_role_instructions": settings.BLOCK_ROLE_INSTRUCTIONS,
            "block_json_instructions": settings.BLOCK_JSON_INSTRUCTIONS,
            "block_code_execution": settings.BLOCK_CODE_EXECUTION,
        },
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server in {settings.ENVIRONMENT} mode")
    logger.info(
        f"Security features: Rate limiting={settings.ENABLE_RATE_LIMITING}, "
        f"Input sanitization=enabled, Security logging={settings.ENABLE_SECURITY_LOGGING}"
    )

    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=settings.ENVIRONMENT == "development"
    )
