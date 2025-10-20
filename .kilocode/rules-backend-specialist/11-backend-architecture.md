# Backend Architecture Rules

## BE-ARC-001: Layered Architecture (Critical)
**Rule**: Follow layered architecture: API endpoints → Service layer → Repository layer → Database with clear separation of concerns

### Implementation
```python
# ✅ ALWAYS follow layered architecture
# api/v1/endpoints/cvs.py (Presentation Layer)
from fastapi import APIRouter, Depends, HTTPException
from app.services.cv_service import CVService
from app.schemas.cv import CVCreate, CVResponse
from app.core.dependencies import get_db

router = APIRouter(prefix="/cvs", tags=["cvs"])

@router.post("", response_model=CVResponse)
async def create_cv(
    cv: CVCreate,
    db: AsyncSession = Depends(get_db)
) -> CVResponse:
    service = CVService(db)
    return await service.create(cv)

# services/cv_service.py (Business Logic Layer)
from app.repositories.cv_repository import CVRepository
from app.schemas.cv import CVCreate, CVResponse

class CVService:
    def __init__(self, db: AsyncSession):
        self.repository = CVRepository(db)
    
    async def create(self, cv_data: CVCreate) -> CVResponse:
        # Business logic validation
        if len(cv_data.skills) < 3:
            raise ValueError("CV must have at least 3 skills")
        
        # Additional business rules
        cv_model = CV(**cv_data.dict())
        created_cv = await self.repository.create(cv_model)
        return CVResponse.from_orm(created_cv)

# db/repositories/cv_repository.py (Data Access Layer)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.cv import CV

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

### Rationale
Backend architecture must be maintainable, testable, and follow separation of principles.

---

## BE-ARC-002: Dependency Injection (Critical)
**Rule**: Use dependency injection pattern for database sessions, services, and configuration using FastAPI's Depends system

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
```

### Rationale
Backend components should be loosely coupled and easily testable.

---

## BE-ARC-003: Repository Pattern (High)
**Rule**: Implement repository pattern for data access with separate classes for each entity to encapsulate query logic

### Implementation
```python
# ✅ ALWAYS implement repository pattern
# db/repositories/base_repository.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

ModelType = TypeVar("ModelType")

class BaseRepository(ABC, Generic[ModelType]):
    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        self.db = db
        self.model = model
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def get_by_id(self, id: str) -> Optional[ModelType]:
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def update(self, id: str, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        await self.db.execute(
            update(self.model).where(self.model.id == id).values(**obj_in)
        )
        await self.db.commit()
        return await self.get_by_id(id)
    
    async def delete(self, id: str) -> bool:
        result = await self.db.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.db.commit()
        return result.rowcount > 0

# db/repositories/cv_repository.py
from app.models.cv import CV
from app.db.repositories.base_repository import BaseRepository

class CVRepository(BaseRepository[CV]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CV)
    
    async def get_by_email(self, email: str) -> Optional[CV]:
        result = await self.db.execute(
            select(CV).where(CV.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_skill_range(
        self, 
        min_experience: int, 
        max_experience: int
    ) -> List[CV]:
        result = await self.db.execute(
            select(CV).where(
                CV.experience_years.between(min_experience, max_experience)
            )
        )
        return result.scalars().all()
    
    async def search_by_skills(self, skills: List[str]) -> List[CV]:
        # PostgreSQL JSON query example
        result = await self.db.execute(
            select(CV).where(CV.skills.op('@>')(skills))
        )
        return result.scalars().all()
```

### Rationale
Backend data access should be abstracted from business logic for maintainability.

---

## BE-ARC-004: Feature-Based Organization (High)
**Rule**: Organize code in feature-based modules with endpoints, services, schemas, and models grouped by business domain

### Implementation
```python
# ✅ ALWAYS organize by feature
# features/cv_management/
# ├── __init__.py
# ├── endpoints/
# │   ├── __init__.py
# │   └── cvs.py
# ├── services/
# │   ├── __init__.py
# │   └── cv_service.py
# ├── schemas/
# │   ├── __init__.py
# │   └── cv.py
# ├── models/
# │   ├── __init__.py
# │   └── cv.py
# └── repositories/
#     ├── __init__.py
#     └── cv_repository.py

# features/cv_management/endpoints/cvs.py
from fastapi import APIRouter, Depends
from features.cv_management.services.cv_service import CVService
from features.cv_management.schemas.cv import CVCreate, CVResponse
from app.core.dependencies import get_db

router = APIRouter(prefix="/cvs", tags=["cvs"])

@router.post("", response_model=CVResponse)
async def create_cv(
    cv: CVCreate,
    db: AsyncSession = Depends(get_db)
) -> CVResponse:
    service = CVService(db)
    return await service.create(cv)

# features/cv_management/services/cv_service.py
from features.cv_management.repositories.cv_repository import CVRepository
from features.cv_management.schemas.cv import CVCreate, CVResponse

class CVService:
    def __init__(self, db: AsyncSession):
        self.repository = CVRepository(db)
    
    async def create(self, cv_data: CVCreate) -> CVResponse:
        # Implementation
        pass

# Main router aggregation
# api/v1/router.py
from fastapi import APIRouter
from features.cv_management.endpoints.cvs import router as cv_router
from features.matching.endpoints.matches import router as match_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(cv_router)
api_router.include_router(match_router)
```

### Rationale
Backend code organization should reflect business domains for maintainability.

---

## BE-ARC-005: Pydantic Schema Design (Medium)
**Rule**: Use Pydantic models for request/response schemas with proper field validation, serialization, and documentation

### Implementation
```python
# ✅ ALWAYS design comprehensive Pydantic schemas
# features/cv_management/schemas/cv.py
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional
from datetime import datetime
from enum import Enum

class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class SkillSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    level: SkillLevel
    years_experience: int = Field(..., ge=0, le=50)

class CVBase(BaseModel):
    candidate_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    phone: Optional[str] = Field(None, regex=r'^\+?1?\d{9,15}$')
    skills: List[SkillSchema] = Field(..., min_length=1)
    experience_years: int = Field(..., ge=0, le=50)
    education: Optional[str] = Field(None, max_length=500)
    summary: Optional[str] = Field(None, max_length=1000)
    
    @field_validator('skills')
    @classmethod
    def validate_skills(cls, v: List[SkillSchema]) -> List[SkillSchema]:
        if not v:
            raise ValueError('skills cannot be empty')
        
        # Check for duplicate skills
        skill_names = [skill.name.lower() for skill in v]
        if len(skill_names) != len(set(skill_names)):
            raise ValueError('duplicate skills are not allowed')
        
        return v
    
    @field_validator('candidate_name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('candidate_name cannot be empty')
        return v.strip().title()

class CVCreate(CVBase):
    """Schema for creating CV"""
    pass

class CVUpdate(BaseModel):
    """Schema for partial updates"""
    candidate_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    phone: Optional[str] = Field(None, regex=r'^\+?1?\d{9,15}$')
    skills: Optional[List[SkillSchema]] = None
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    education: Optional[str] = Field(None, max_length=500)
    summary: Optional[str] = Field(None, max_length=1000)

class CVResponse(CVBase):
    """Schema for API responses"""
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    model_config = ConfigDict(from_attributes=True)

class CVListResponse(BaseModel):
    """Schema for paginated CV list"""
    items: List[CVResponse]
    total: int
    page: int
    size: int
    pages: int

# Usage in endpoints with automatic documentation
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
async def create_cv(cv: CVCreate, db: AsyncSession = Depends(get_db)):
    """Create CV with validation:
    - candidate_name: required, max 100 chars
    - skills: non-empty list with unique names
    - experience_years: >= 0, <= 50
    """
    # Implementation
    pass
```

### Rationale
Backend APIs need clear contracts and automatic documentation generation.