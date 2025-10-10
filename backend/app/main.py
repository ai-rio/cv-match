import logging

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.services.security import SecurityMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.SECURITY_LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Full Stack App Backend",
    description="API for the Full Stack Application",
    version="0.1.0",
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
    return {
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "version": "0.1.0",
        "security_enabled": settings.ENABLE_RATE_LIMITING,
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
