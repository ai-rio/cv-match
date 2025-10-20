# Backend Type Safety Rules

## BE-TYPE-001: Strict Type Hints (Critical)
**Rule**: Use strict type hints for all function parameters, return values, and variables; avoid 'any' type completely

### Implementation
```python
# ✅ ALWAYS use explicit type hints
from typing import List, Optional, Dict, Any, Union, Callable, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

# Function with complete type hints
async def create_cv(
    db: AsyncSession,
    cv_data: Dict[str, Any],
    user_id: str
) -> Optional[CV]:
    """Create a new CV with proper type annotations"""
    # Implementation
    pass

# Service method with proper typing
class CVService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
    
    async def get_by_id(self, cv_id: str) -> Optional[CV]:
        """Get CV by ID with proper return type"""
        result = await self.db.execute(
            select(CV).where(CV.id == cv_id)
        )
        return result.scalar_one_or_none()
    
    async def get_multiple(
        self, 
        cv_ids: List[str]
    ) -> List[CV]:
        """Get multiple CVs with proper parameter and return types"""
        result = await self.db.execute(
            select(CV).where(CV.id.in_(cv_ids))
        )
        return result.scalars().all()

# Repository with complete typing
class CVRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
    
    async def create(self, cv: CV) -> CV:
        """Create CV with explicit types"""
        self.db.add(cv)
        await self.db.commit()
        await self.db.refresh(cv)
        return cv
    
    async def update(
        self, 
        cv_id: str, 
        update_data: Dict[str, Any]
    ) -> Optional[CV]:
        """Update CV with proper type hints"""
        await self.db.execute(
            update(CV).where(CV.id == cv_id).values(**update_data)
        )
        await self.db.commit()
        return await self.get_by_id(cv_id)

# ❌ NEVER DO: Missing type hints
def process_data(data):  # NO type hints
    return data.strip()

# ❌ NEVER DO: Using 'any' type
def process_data(data: any) -> any:  # NO 'any' type
    return data.strip()

# ✅ ALWAYS DO: Proper type hints
def process_data(data: str) -> str:
    return data.strip()
```

### Rationale
Backend Python code benefits from static type checking and IDE support.

---

## BE-TYPE-002: Pydantic Models (High)
**Rule**: Use Pydantic BaseModel for all data structures with proper field types and validation rules

### Implementation
```python
# ✅ ALWAYS use Pydantic for data structures
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Enum for type safety
class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

# Base model with common fields
class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=False
    )

# Request schemas
class SkillCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    level: SkillLevel
    years_experience: int = Field(..., ge=0, le=50)

class CVCreate(BaseModel):
    candidate_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    skills: List[SkillCreate] = Field(..., min_length=1)
    experience_years: int = Field(..., ge=0, le=50)
    
    @field_validator('skills')
    @classmethod
    def validate_skills(cls, v: List[SkillCreate]) -> List[SkillCreate]:
        if not v:
            raise ValueError('skills cannot be empty')
        
        # Check for duplicate skills
        skill_names = [skill.name.lower() for skill in v]
        if len(skill_names) != len(set(skill_names)):
            raise ValueError('duplicate skills are not allowed')
        
        return v

# Response schemas
class SkillResponse(BaseModel):
    id: str
    name: str
    level: SkillLevel
    years_experience: int
    created_at: datetime

class CVResponse(BaseModel):
    id: str
    candidate_name: str
    email: str
    skills: List[SkillResponse]
    experience_years: int
    created_at: datetime
    updated_at: datetime

# Update schemas with optional fields
class CVUpdate(BaseModel):
    candidate_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    skills: Optional[List[SkillCreate]] = None
    experience_years: Optional[int] = Field(None, ge=0, le=50)

# Internal data structures
class CVProcessingResult(BaseModel):
    cv_id: str
    processing_status: str
    matched_jobs: List[str]
    confidence_score: float
    processing_time_ms: int

# Generic response wrapper
class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None

# Usage in endpoints
@router.post("/cvs", response_model=APIResponse[CVResponse])
async def create_cv(
    cv: CVCreate,
    db: AsyncSession = Depends(get_db)
) -> APIResponse[CVResponse]:
    try:
        service = CVService(db)
        created_cv = await service.create(cv)
        return APIResponse(
            success=True,
            data=CVResponse.from_orm(created_cv),
            message="CV created successfully"
        )
    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            message="Failed to create CV"
        )
```

### Rationale
Backend data structures need runtime validation and serialization capabilities.

---

## BE-TYPE-003: Internal Data Structures (Medium)
**Rule**: Use TypedDict or dataclasses for internal data structures when Pydantic is not appropriate

### Implementation
```python
# ✅ Use TypedDict for internal data transfer
from typing import TypedDict, NotRequired
from dataclasses import dataclass
from datetime import datetime

# TypedDict for simple data structures
class CVSearchFilters(TypedDict):
    """Type-safe search filters"""
    candidate_name: NotRequired[str]
    min_experience: NotRequired[int]
    max_experience: NotRequired[int]
    skills: NotRequired[List[str]]
    is_active: NotRequired[bool]

class MatchingResult(TypedDict):
    """Type-safe matching result"""
    cv_id: str
    job_id: str
    score: float
    matched_skills: List[str]
    missing_skills: List[str]

class EmailNotificationData(TypedDict):
    """Type-safe email notification data"""
    recipient_email: str
    subject: str
    template_name: str
    template_data: Dict[str, Any]

# Dataclasses for more complex internal structures
@dataclass
class CVProcessingContext:
    """Context for CV processing operations"""
    cv_id: str
    user_id: str
    processing_start: datetime
    request_id: str
    priority: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'cv_id': self.cv_id,
            'user_id': self.user_id,
            'processing_start': self.processing_start.isoformat(),
            'request_id': self.request_id,
            'priority': self.priority
        }

@dataclass
class CacheKey:
    """Type-safe cache key generation"""
    prefix: str
    identifier: str
    version: str = "v1"
    
    def __str__(self) -> str:
        return f"{self.prefix}:{self.version}:{self.identifier}"

# Generic type-safe repository interface
class GenericRepository(Generic[T, K]):
    """Type-safe generic repository interface"""
    
    async def get_by_id(self, id: K) -> Optional[T]:
        """Get entity by ID"""
        raise NotImplementedError
    
    async def create(self, entity: T) -> T:
        """Create new entity"""
        raise NotImplementedError
    
    async def update(self, id: K, updates: Dict[str, Any]) -> Optional[T]:
        """Update entity"""
        raise NotImplementedError
    
    async def delete(self, id: K) -> bool:
        """Delete entity"""
        raise NotImplementedError

# Type-safe service interfaces
class MatchingServiceInterface(Protocol):
    """Protocol for matching service"""
    
    async def calculate_match_score(
        self, 
        cv_id: str, 
        job_id: str
    ) -> MatchingResult:
        """Calculate match score between CV and job"""
        ...
    
    async def find_best_matches(
        self, 
        cv_id: str, 
        limit: int = 10
    ) -> List[MatchingResult]:
        """Find best matching jobs for CV"""
        ...

# Type-safe dependency injection
def get_matching_service() -> MatchingServiceInterface:
    """Get type-safe matching service instance"""
    return MatchingService()

# Usage with proper typing
async def process_cv_matching(
    cv_id: str,
    matching_service: MatchingServiceInterface = Depends(get_matching_service)
) -> List[MatchingResult]:
    """Process CV matching with type safety"""
    return await matching_service.find_best_matches(cv_id)

# Type-safe configuration
class DatabaseConfig(TypedDict):
    """Database configuration with type safety"""
    url: str
    pool_size: int
    max_overflow: int
    pool_timeout: int
    echo: bool

class RedisConfig(TypedDict):
    """Redis configuration with type safety"""
    url: str
    max_connections: int
    retry_on_timeout: bool
    socket_timeout: int

# Type-safe event handlers
class EventHandler(Generic[T]):
    """Type-safe event handler"""
    
    def __init__(self, handler: Callable[[T], None]):
        self.handler = handler
    
    async def handle(self, event: T) -> None:
        """Handle event with type safety"""
        try:
            if asyncio.iscoroutinefunction(self.handler):
                await self.handler(event)
            else:
                self.handler(event)
        except Exception as e:
            logger.error(f"Error handling event {event}: {e}")

# Usage example
cv_created_handler = EventHandler[CV](lambda cv: print(f"CV created: {cv.id}"))
```

### Rationale
Backend internal data structures benefit from type safety without overhead.