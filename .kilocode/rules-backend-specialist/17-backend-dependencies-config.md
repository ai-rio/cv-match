# Backend Dependencies & Configuration Rules

## BE-DEP-001: Dependency Injection (Medium)
**Rule**: Use dependency injection with FastAPI's Depends system for database sessions, authentication, and services

### Implementation
```python
# ✅ ALWAYS use dependency injection
# core/dependencies.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import async_session_maker
from app.core.config import settings
from app.services.cv_service import CVService

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_cv_service(db: AsyncSession = Depends(get_db)) -> CVService:
    """CV service dependency"""
    return CVService(db)

# Settings dependency
async def get_settings() -> Settings:
    return settings

# Usage in endpoints
@router.get("/cvs/{cv_id}")
async def get_cv(
    cv_id: str,
    cv_service: CVService = Depends(get_cv_service),
    settings: Settings = Depends(get_settings)
):
    return await cv_service.get_by_id(cv_id)

# Custom dependencies with parameters
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    user_id = payload.get("sub")
    
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Role-based dependencies
async def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

# Usage in endpoints with role-based access
@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    return await delete_user_by_id(user_id, db)
```

### Rationale
Backend components should be loosely coupled and easily testable.

---

## BE-DEP-002: Circular Import Prevention (Medium)
**Rule**: Implement circular import prevention strategies using string annotations and local imports

### Implementation
```python
# ✅ ALWAYS prevent circular imports
# Use string annotations for forward references
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

class CV(Base):
    __tablename__ = "cvs"
    
    id = Column(String, primary_key=True)
    matches = relationship("CVMatch", back_populates="cv")  # String reference

# Or import inside methods to avoid circular imports
def get_service():
    from app.services.cv_service import CVService  # Local import
    return CVService()

# Use TYPE_CHECKING for imports only needed for type hints
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.cv import CV
    from app.services.cv_service import CVService

class SomeService:
    def process_cv(self, cv_id: str) -> "CV":  # TYPE_CHECKING import
        # Implementation
        pass

# Separate interface and implementation
# interfaces/cv_service_interface.py
from abc import ABC, abstractmethod

class CVServiceInterface(ABC):
    @abstractmethod
    async def create(self, cv_data: CVCreate) -> CVResponse:
        pass

# services/cv_service.py
class CVService(CVServiceInterface):
    async def create(self, cv_data: CVCreate) -> CVResponse:
        # Implementation
        pass

# Use dependency injection to resolve at runtime
# main.py
from app.interfaces.cv_service_interface import CVServiceInterface
from app.services.cv_service import CVService

app.dependency_overrides[CVServiceInterface] = lambda: CVService(db)
```

### Rationale
Backend modular architecture requires careful dependency management.

---

## BE-CONFIG-001: Configuration Management (High)
**Rule**: Use Pydantic BaseSettings for configuration with environment variable validation and type conversion

### Implementation
```python
# ✅ ALWAYS use BaseSettings for configuration
# core/config.py
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List

class Settings(BaseSettings):
    # App
    APP_NAME: str = Field(..., description="Application name")
    DEBUG: bool = Field(False, description="Enable debug mode")
    API_V1_PREFIX: str = Field("/api/v1", description="API v1 prefix")
    
    # Database
    DATABASE_URL: str = Field(..., description="Database connection string")
    DATABASE_POOL_SIZE: int = Field(20, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(30, description="Database max overflow connections")
    
    # Security
    SECRET_KEY: str = Field(..., min_length=32, description="JWT secret key")
    ALGORITHM: str = Field("HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, description="Access token expiration in minutes")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins"
    )
    
    # Redis
    REDIS_URL: Optional[str] = Field(None, description="Redis connection URL")
    REDIS_MAX_CONNECTIONS: int = Field(10, description="Redis max connections")
    
    # Email
    SMTP_HOST: Optional[str] = Field(None, description="SMTP host")
    SMTP_PORT: int = Field(587, description="SMTP port")
    SMTP_USERNAME: Optional[str] = Field(None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(None, description="SMTP password")
    
    # External APIs
    EXTERNAL_API_KEY: Optional[str] = Field(None, description="External API key")
    EXTERNAL_API_URL: Optional[str] = Field(None, description="External API URL")
    
    # Logging
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    LOG_FORMAT: str = Field("json", description="Log format (json or text)")
    
    # Performance
    REQUEST_TIMEOUT: int = Field(30, description="Request timeout in seconds")
    MAX_REQUEST_SIZE: int = Field(10485760, description="Max request size in bytes")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"  # Ignore extra env vars
    }
    
    @classmethod
    def validate(cls):
        """Validate configuration at startup"""
        settings = cls()
        
        # Validate critical settings
        if len(settings.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        
        if not settings.DATABASE_URL:
            raise ValueError("DATABASE_URL is required")
        
        # Validate origins
        if settings.DEBUG and "localhost" not in settings.ALLOWED_ORIGINS:
            settings.ALLOWED_ORIGINS.append("http://localhost:3000")
        
        return settings

# Create global settings instance
settings = Settings.validate()

# Usage in other modules
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL
SECRET_KEY = settings.SECRET_KEY
```

### Rationale
Backend configuration must be type-safe and validated at startup.

---

## BE-CONFIG-002: Environment-Specific Configuration (Medium)
**Rule**: Implement environment-specific configurations (development, staging, production) with proper defaults

### Implementation
```python
# ✅ ALWAYS implement environment-specific configs
# core/config.py
from enum import Enum
from typing import Dict, Any

class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    # ... other fields from BE-CONFIG-001
    
    ENVIRONMENT: Environment = Field(
        Environment.DEVELOPMENT,
        description="Application environment"
    )
    
    @classmethod
    def get_config_for_environment(cls, env: Environment) -> Dict[str, Any]:
        """Get environment-specific configuration"""
        configs = {
            Environment.DEVELOPMENT: {
                "DEBUG": True,
                "LOG_LEVEL": "DEBUG",
                "DATABASE_POOL_SIZE": 5,
                "REDIS_MAX_CONNECTIONS": 5,
                "REQUEST_TIMEOUT": 60,
                "ALLOWED_ORIGINS": [
                    "http://localhost:3000",
                    "http://localhost:8000"
                ]
            },
            Environment.TESTING: {
                "DEBUG": False,
                "LOG_LEVEL": "WARNING",
                "DATABASE_POOL_SIZE": 1,
                "REDIS_MAX_CONNECTIONS": 1,
                "REQUEST_TIMEOUT": 10,
                "ALLOWED_ORIGINS": ["http://localhost:3000"]
            },
            Environment.STAGING: {
                "DEBUG": False,
                "LOG_LEVEL": "INFO",
                "DATABASE_POOL_SIZE": 10,
                "REDIS_MAX_CONNECTIONS": 10,
                "REQUEST_TIMEOUT": 30,
                "ALLOWED_ORIGINS": [
                    "https://staging.yourdomain.com",
                    "https://admin-staging.yourdomain.com"
                ]
            },
            Environment.PRODUCTION: {
                "DEBUG": False,
                "LOG_LEVEL": "INFO",
                "DATABASE_POOL_SIZE": 20,
                "REDIS_MAX_CONNECTIONS": 20,
                "REQUEST_TIMEOUT": 30,
                "ALLOWED_ORIGINS": [
                    "https://yourdomain.com",
                    "https://admin.yourdomain.com"
                ]
            }
        }
        
        return configs.get(env, configs[Environment.DEVELOPMENT])
    
    @classmethod
    def create_for_environment(cls, env: Environment) -> "Settings":
        """Create settings instance for specific environment"""
        config = cls.get_config_for_environment(env)
        
        # Override with environment-specific values
        return cls(
            **config,
            ENVIRONMENT=env
        )
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == Environment.DEVELOPMENT

# Environment detection and settings creation
def get_settings() -> Settings:
    """Get appropriate settings for current environment"""
    env = Environment(os.getenv("ENVIRONMENT", "development"))
    return Settings.create_for_environment(env)

# Create global settings instance
settings = get_settings()

# Usage in main.py
from app.core.config import settings

if settings.is_development():
    app.add_middleware(DebugMiddleware)

# Setup logging based on environment
import logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Environment-specific database configuration
if settings.ENVIRONMENT == Environment.TESTING:
    # Use in-memory SQLite for testing
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"
elif settings.ENVIRONMENT == Environment.DEVELOPMENT:
    # Use local PostgreSQL
    DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/cvmatch_dev"
else:
    # Use production database
    DATABASE_URL = settings.DATABASE_URL
```

### Rationale
Backend applications must adapt to different deployment environments.