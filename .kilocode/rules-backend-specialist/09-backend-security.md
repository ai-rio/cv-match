# Backend Security Rules

## BE-SEC-001: Input Validation (Critical)
**Rule**: NEVER trust client input - ALWAYS validate on server side using Pydantic schemas with field validators before processing any data

### Implementation
```python
# ✅ ALWAYS validate with Pydantic schemas
from pydantic import BaseModel, Field, field_validator
from typing import List

class CVCreate(BaseModel):
    candidate_name: str = Field(..., min_length=1, max_length=100)
    skills: List[str] = Field(..., min_length=1)
    experience_years: int = Field(..., ge=0, le=50)
    
    @field_validator('skills')
    @classmethod
    def validate_skills(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError('skills cannot be empty')
        return [s.strip().lower() for s in v if s.strip()]

@router.post("/cvs")
async def create_cv(cv: CVCreate, db: AsyncSession = Depends(get_db)):
    # Input is already validated by Pydantic
    service = CVService(db)
    return await service.create(cv)
```

### Rationale
Backend is the authoritative source for data validation; client validation can be bypassed.

---

## BE-SEC-002: Authentication & Authorization (Critical)
**Rule**: Implement proper authentication and authorization using JWT tokens with HTTPBearer security scheme and role-based access control

### Implementation
```python
# ✅ ALWAYS implement proper auth
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

@router.get("/admin/users")
async def get_users(
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_all_users(db)
```

### Rationale
Backend must enforce access controls and verify user identity for protected resources.

---

## BE-SEC-003: Environment Variables & Secrets (Critical)
**Rule**: Store secrets in environment variables with proper validation using Pydantic BaseSettings; NEVER commit .env files

### Implementation
```python
# ✅ ALWAYS use BaseSettings for secrets
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Security
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = Field(..., description="Database connection string")
    
    # External APIs
    EXTERNAL_API_KEY: str = Field(..., description="External service API key")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"  # Ignore extra env vars
    }

settings = Settings()

# Usage
SECRET_KEY = settings.SECRET_KEY  # Type-safe and validated
```

### Rationale
Backend handles sensitive data like database credentials, API keys, and JWT secrets.

---

## BE-SEC-004: Rate Limiting (Critical)
**Rule**: Implement rate limiting on public endpoints using slowapi with Redis backend to prevent abuse and DDoS attacks

### Implementation
```python
# ✅ ALWAYS implement rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/auth/login")
@limiter.limit("5/minute")  # 5 attempts per minute
async def login(request: Request, credentials: LoginSchema):
    return await authenticate_user(credentials)

@router.post("/upload")
@limiter.limit("10/hour")  # 10 uploads per hour
async def upload_file(request: Request, file: UploadFile):
    return await process_file_upload(file)

@router.get("/public/data")
@limiter.limit("100/minute")  # 100 requests per minute
async def get_public_data(request: Request):
    return await get_data()
```

### Rationale
Backend APIs are publicly accessible and require protection against excessive requests.

---

## BE-SEC-005: CORS Configuration (High)
**Rule**: Configure CORS properly with explicit allowed origins, methods, and headers; avoid wildcard origins in production

### Implementation
```python
# ✅ ALWAYS configure CORS properly
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Specific domains only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Explicit methods
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Requested-With"
    ],  # Explicit headers
)

# core/config.py
class Settings(BaseSettings):
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "https://yourdomain.com"
    ]
    
    @classmethod
    def get_prod_origins(cls):
        if settings.DEBUG:
            return ["http://localhost:3000"]
        return ["https://yourdomain.com"]
```

### Rationale
Backend APIs must be accessible only to authorized frontend domains.

---

## BE-SEC-006: Error Handling (High)
**Rule**: Implement comprehensive error handling with custom exception classes and global exception handlers that sanitize error messages

### Implementation
```python
# ✅ ALWAYS implement proper error handling
# core/exceptions.py
from fastapi import HTTPException, status

class CVNotFoundException(HTTPException):
    def __init__(self, cv_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CV not found"
        )

class InvalidCVDataException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

# Global exception handler
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid data provided", "type": "validation_error"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# In endpoints
@router.get("/cvs/{cv_id}")
async def get_cv(cv_id: str, db: AsyncSession = Depends(get_db)):
    try:
        cv = await cv_service.get_by_id(cv_id)
        if not cv:
            raise CVNotFoundException(cv_id)
        return cv
    except Exception as e:
        logger.error(f"Error getting CV {cv_id}: {e}")
        raise
```

### Rationale
Backend errors should not leak sensitive information while providing useful feedback.