# Backend Architecture

## Project Structure

```python
app/
├── api/
│   ├── v1/
│   │   ├── endpoints/
│   │   │   ├── cvs.py
│   │   │   ├── matches.py
│   │   │   └── auth.py
│   │   └── router.py
├── core/
│   ├── config.py
│   ├── security.py
│   └── dependencies.py
├── models/
│   ├── cv.py
│   └── match.py
├── schemas/
│   ├── cv.py
│   └── match.py
├── services/
│   ├── cv_service.py
│   └── matching_service.py
├── db/
│   ├── database.py
│   └── repositories/
└── main.py
```

## Core Development Principles

### Code Quality
- **Concise & readable**: Prioritize clarity over cleverness
- **Type safety**: Type hints on backend
- **DRY principle**: Abstract repeated patterns
- **Fail fast**: Early validation, explicit error handling
- **Performance first**: Async operations, lazy loading, caching

### Architecture Patterns

#### Service Layer Pattern
```python
# services/cv_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

class CVService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, cv_data: CVCreate) -> CVResponse:
        # Business logic for CV creation
        pass
    
    async def get_by_id(self, cv_id: str) -> Optional[CVResponse]:
        # Business logic for CV retrieval
        pass
```

#### Repository Pattern
```python
# db/repositories/cv_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class CVRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, cv: CV) -> CV:
        self.db.add(cv)
        await self.db.commit()
        await self.db.refresh(cv)
        return cv
    
    async def get_by_id(self, cv_id: str) -> Optional[CV]:
        result = await self.db.execute(
            select(CV).where(CV.id == cv_id)
        )
        return result.scalar_one_or_none()
```

### Module Organization

#### Feature-Based Structure
```python
# Each feature has its own module
features/
├── cv_management/
│   ├── endpoints/
│   ├── services/
│   ├── schemas/
│   └── models/
├── matching/
│   ├── endpoints/
│   ├── services/
│   ├── schemas/
│   └── models/
└── auth/
    ├── endpoints/
    ├── services/
    ├── schemas/
    └── models/
```

#### Clean Architecture Layers
```python
# Domain Layer (entities, business rules)
domain/
├── entities/
└── services/

# Application Layer (use cases)
application/
├── use_cases/
└── dto/

# Infrastructure Layer (database, external APIs)
infrastructure/
├── database/
├── external/
└── repositories/

# Presentation Layer (API endpoints)
presentation/
└── api/
```

### Database Design Principles

#### Model Organization
```python
# models/base.py
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TimestampMixin:
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class BaseModel(Base, TimestampMixin):
    __abstract__ = True
    id = Column(String, primary_key=True, index=True)
```

#### Relationship Patterns
```python
# models/cv.py
from sqlalchemy import Column, String, Integer, Relationship
from sqlalchemy.orm import relationship

class CV(BaseModel):
    __tablename__ = "cvs"
    
    candidate_name = Column(String, index=True)
    skills = Column(JSON)  # For PostgreSQL
    experience_years = Column(Integer)
    
    # Relationships
    matches = relationship("CVMatch", back_populates="cv")
    
    def __repr__(self):
        return f"<CV(id={self.id}, name={self.candidate_name})>"
```

## Import Organization

### Standard Import Structure
```python
# Standard library imports first
import os
from typing import List, Optional, AsyncGenerator

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

# Local imports
from app.core.dependencies import get_db
from app.schemas.cv import CVCreate, CVResponse
from app.services.cv_service import CVService
```

### Circular Import Prevention
```python
# Use string annotations for forward references
class CV(Base):
    matches: List["CVMatch"] = relationship("CVMatch")

# Or import inside methods to avoid circular imports
def get_service():
    from app.services.cv_service import CVService
    return CVService()
```

## Configuration Management

### Environment-Based Configuration
```python
# core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    APP_NAME: str = "CV Match API"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "https://yourdomain.com"
    ]
    
    # Redis
    REDIS_URL: Optional[str] = None
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }

settings = Settings()
```

## Logging Setup

### Structured Logging
```python
# core/logging.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    logHandler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)

# Usage in endpoints
logger = logging.getLogger(__name__)

@router.post("/cvs")
async def create_cv(cv: CVCreate, db: AsyncSession = Depends(get_db)):
    logger.info("Creating CV", extra={"candidate_name": cv.candidate_name})
    # ... implementation
```

## Documentation Standards

### API Documentation with OpenAPI
```python
# Use proper docstrings for endpoints
@router.post(
    "/cvs",
    response_model=CVResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new CV",
    description="Create a CV with validation for candidate name, skills, and experience",
    tags=["cvs"],
    responses={
        201: {"description": "CV created successfully"},
        400: {"description": "Invalid data provided"},
        422: {"description": "Validation error"}
    }
)
async def create_cv(
    cv: CVCreate,
    db: AsyncSession = Depends(get_db)
) -> CVResponse:
    """
    Create CV with validation:
    - candidate_name: required, max 100 chars
    - skills: non-empty list
    - experience_years: >= 0, <= 50
    """
    pass
```

---

## 📝 Kilo Code Workflow

### When creating new backend features:
1. **Define Pydantic schemas first** (validation models)
2. **Create database models** (SQLAlchemy models)
3. **Implement repository layer** (data access)
4. **Create service layer** (business logic)
5. **Build API endpoints** (presentation layer)
6. **Write tests** for all layers

### Use these patterns:
```python
# Backend: Feature module structure
api/v1/endpoints/
  feature.py              # Routes
services/
  feature_service.py      # Business logic
schemas/
  feature.py              # Pydantic schemas
models/
  feature.py              # DB models
db/repositories/
  feature_repository.py   # Data access