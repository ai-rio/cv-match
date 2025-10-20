# Backend Documentation Rules

## BE-DOC-001: API Documentation with OpenAPI (High)
**Rule**: Use FastAPI's automatic OpenAPI documentation with proper descriptions, examples, and response models

### Implementation
```python
# ✅ ALWAYS use proper docstrings for endpoints
from fastapi import APIRouter, HTTPException, status, Query, Path
from typing import List, Optional
from app.schemas.cv import CVCreate, CVResponse, CVUpdate
from app.services.cv_service import CVService

router = APIRouter(prefix="/cvs", tags=["CVs"])

@router.post(
    "/cvs",
    response_model=CVResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new CV",
    description=(
        "Create a CV with validation for candidate name, skills, and experience. "
        "The CV will be associated with the authenticated user."
    ),
    tags=["CVs"],
    responses={
        201: {
            "description": "CV created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "cv-123",
                        "candidate_name": "John Doe",
                        "email": "john@example.com",
                        "skills": [
                            {"name": "Python", "level": "advanced", "years_experience": 5}
                        ],
                        "experience_years": 5,
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-01T12:00:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Invalid data provided",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "candidate_name"],
                                "msg": "ensure this value has at least 1 characters",
                                "type": "value_error.any_str.min_length"
                            }
                        ]
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "email"],
                                "msg": "value is not a valid email address",
                                "type": "value_error.email"
                            }
                        ]
                    }
                }
            }
        }
    },
    openapi_extra={
        "x-operationId": "createCV",
        "x-acl": ["user", "admin"]
    }
)
async def create_cv(
    cv: CVCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> CVResponse:
    """
    Create CV with validation:
    - candidate_name: required, max 100 chars
    - skills: non-empty list with unique names
    - experience_years: >= 0, <= 50
    
    Args:
        cv: CV data to create
        db: Database session
        current_user: Authenticated user
    
    Returns:
        Created CV with assigned ID
        
    Raises:
        HTTPException: If validation fails or user not found
    """
    try:
        service = CVService(db)
        return await service.create(cv, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/cvs/{cv_id}",
    response_model=CVResponse,
    summary="Get CV by ID",
    description="Retrieve a specific CV by its unique identifier",
    tags=["CVs"],
    responses={
        200: {
            "description": "CV retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "cv-123",
                        "candidate_name": "John Doe",
                        "email": "john@example.com",
                        "skills": [
                            {"name": "Python", "level": "advanced", "years_experience": 5}
                        ],
                        "experience_years": 5,
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-01T12:00:00Z"
                    }
                }
            }
        },
        404: {
            "description": "CV not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "CV cv-123 not found"
                    }
                }
            }
        }
    },
    openapi_extra={
        "x-operationId": "getCV",
        "x-acl": ["user", "admin"]
    }
)
async def get_cv(
    cv_id: str = Path(..., description="Unique identifier of the CV", example="cv-123"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> CVResponse:
    """
    Get CV by ID:
    
    Args:
        cv_id: Unique identifier of the CV
        db: Database session
        current_user: Authenticated user
    
    Returns:
        CV data if found
        
    Raises:
        HTTPException: If CV not found or access denied
    """
    service = CVService(db)
    cv = await service.get_by_id(cv_id, current_user.id)
    
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CV {cv_id} not found"
        )
    
    return cv

@router.get(
    "/cvs",
    response_model=List[CVResponse],
    summary="List CVs",
    description="Retrieve a paginated list of CVs with optional filtering",
    tags=["CVs"],
    responses={
        200: {
            "description": "CVs retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "cv-123",
                            "candidate_name": "John Doe",
                            "email": "john@example.com",
                            "skills": [
                                {"name": "Python", "level": "advanced", "years_experience": 5}
                            ],
                            "experience_years": 5,
                            "created_at": "2024-01-01T12:00:00Z",
                            "updated_at": "2024-01-01T12:00:00Z"
                        }
                    ]
                }
            }
        }
    },
    openapi_extra={
        "x-operationId": "listCVs",
        "x-acl": ["user", "admin"]
    }
)
async def list_cvs(
    skip: int = Query(0, ge=0, description="Number of items to skip", example=0),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return", example=100),
    candidate_name: Optional[str] = Query(None, description="Filter by candidate name", example="John"),
    min_experience: Optional[int] = Query(None, ge=0, description="Filter by minimum experience years", example=3),
    max_experience: Optional[int] = Query(None, ge=0, description="Filter by maximum experience years", example=10),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[CVResponse]:
    """
    List CVs with optional filtering:
    
    Args:
        skip: Number of items to skip for pagination
        limit: Maximum number of items to return
        candidate_name: Optional filter by candidate name
        min_experience: Optional filter by minimum experience years
        max_experience: Optional filter by maximum experience years
        db: Database session
        current_user: Authenticated user
    
    Returns:
        List of CVs matching the criteria
    """
    service = CVService(db)
    filters = {}
    
    if candidate_name:
        filters["candidate_name"] = candidate_name
    if min_experience is not None:
        filters["min_experience"] = min_experience
    if max_experience is not None:
        filters["max_experience"] = max_experience
    
    return await service.get_multiple(
        current_user.id,
        skip=skip,
        limit=limit,
        **filters
    )
```

### Rationale
Backend APIs must be self-documenting for frontend developers and consumers.

---

## BE-DOC-002: Service Method Documentation (Medium)
**Rule**: Write comprehensive docstrings for all service methods with parameter descriptions and business logic explanation

### Implementation
```python
# ✅ ALWAYS document service methods thoroughly
# services/cv_service.py
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.cv_repository import CVRepository
from app.schemas.cv import CVCreate, CVResponse, CVUpdate
from app.models.cv import CV

class CVService:
    """
    Service layer for CV business logic operations.
    
    This service handles all CV-related business operations including
    creation, retrieval, updates, and deletion with proper validation
    and business rule enforcement.
    
    Attributes:
        db: Async database session
        repository: CV repository for data access
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize CV service with database session.
        
        Args:
            db: Async database session for database operations
        """
        self.db = db
        self.repository = CVRepository(db)
    
    async def create(self, cv_data: CVCreate, user_id: str) -> CVResponse:
        """
        Create a new CV with business validation.
        
        This method validates the CV data against business rules:
        - Must have at least 3 skills
        - Candidate name must be properly formatted
        - Email must be unique for the user
        - Experience years must be within valid range
        
        Args:
            cv_data: CV creation data with candidate information
            user_id: ID of the user creating the CV
            
        Returns:
            Created CV with assigned ID and timestamps
            
        Raises:
            ValueError: If business validation fails
            DuplicateEmailError: If email already exists for user
            InsufficientSkillsError: If less than 3 skills provided
        """
        # Business validation
        if len(cv_data.skills) < 3:
            raise ValueError("CV must have at least 3 skills")
        
        # Check for duplicate email for this user
        existing_cv = await self.repository.get_by_email_and_user(
            cv_data.email, user_id
        )
        if existing_cv:
            raise ValueError(f"Email {cv_data.email} already exists for this user")
        
        # Create CV model
        cv = CV(
            candidate_name=cv_data.candidate_name.strip().title(),
            email=cv_data.email.lower().strip(),
            skills=cv_data.skills,
            experience_years=cv_data.experience_years,
            user_id=user_id
        )
        
        # Save to database
        created_cv = await self.repository.create(cv)
        
        # Log creation
        logger.info(
            "CV created",
            cv_id=created_cv.id,
            user_id=user_id,
            candidate_name=created_cv.candidate_name
        )
        
        return CVResponse.from_orm(created_cv)
    
    async def get_by_id(self, cv_id: str, user_id: str) -> Optional[CVResponse]:
        """
        Retrieve a CV by ID with user access validation.
        
        This method ensures that users can only access their own CVs
        unless they have admin privileges.
        
        Args:
            cv_id: Unique identifier of the CV
            user_id: ID of the user requesting the CV
            
        Returns:
            CV data if found and accessible
            None if CV doesn't exist
            
        Raises:
            AccessDeniedError: If user doesn't have access to the CV
        """
        cv = await self.repository.get_by_id(cv_id)
        
        if not cv:
            return None
        
        # Check access permissions
        if cv.user_id != user_id:
            # Could check for admin privileges here
            raise ValueError("Access denied to this CV")
        
        return CVResponse.from_orm(cv)
    
    async def update(self, cv_id: str, update_data: CVUpdate, user_id: str) -> CVResponse:
        """
        Update an existing CV with business validation.
        
        This method validates the update data and ensures that:
        - Only the CV owner can update it
        - Email uniqueness is maintained
        - Business rules are enforced
        
        Args:
            cv_id: Unique identifier of the CV to update
            update_data: Partial CV data to update
            user_id: ID of the user requesting the update
            
        Returns:
            Updated CV data
            
        Raises:
            CVNotFoundError: If CV doesn't exist
            AccessDeniedError: If user doesn't own the CV
            ValueError: If business validation fails
        """
        # Get existing CV
        existing_cv = await self.repository.get_by_id(cv_id)
        if not existing_cv:
            raise ValueError(f"CV {cv_id} not found")
        
        # Check ownership
        if existing_cv.user_id != user_id:
            raise ValueError("Access denied to this CV")
        
        # Validate email uniqueness if being updated
        if update_data.email and update_data.email != existing_cv.email:
            email_cv = await self.repository.get_by_email_and_user(
                update_data.email, user_id
            )
            if email_cv:
                raise ValueError(f"Email {update_data.email} already exists for this user")
        
        # Apply updates
        update_dict = update_data.dict(exclude_unset=True)
        
        # Format candidate name if provided
        if "candidate_name" in update_dict:
            update_dict["candidate_name"] = update_dict["candidate_name"].strip().title()
        
        # Format email if provided
        if "email" in update_dict:
            update_dict["email"] = update_dict["email"].lower().strip()
        
        # Update in database
        updated_cv = await self.repository.update(cv_id, update_dict)
        
        # Log update
        logger.info(
            "CV updated",
            cv_id=cv_id,
            user_id=user_id,
            updated_fields=list(update_dict.keys())
        )
        
        return CVResponse.from_orm(updated_cv)
    
    async def delete(self, cv_id: str, user_id: str) -> bool:
        """
        Delete a CV with ownership validation.
        
        This method ensures that only the CV owner can delete it
        and handles proper cleanup of related data.
        
        Args:
            cv_id: Unique identifier of the CV to delete
            user_id: ID of the user requesting the deletion
            
        Returns:
            True if deletion was successful
            
        Raises:
            CVNotFoundError: If CV doesn't exist
            AccessDeniedError: If user doesn't own the CV
        """
        # Get existing CV
        existing_cv = await self.repository.get_by_id(cv_id)
        if not existing_cv:
            raise ValueError(f"CV {cv_id} not found")
        
        # Check ownership
        if existing_cv.user_id != user_id:
            raise ValueError("Access denied to this CV")
        
        # Handle business logic before deletion
        await self._handle_cv_deletion_business_rules(existing_cv)
        
        # Delete from database
        result = await self.repository.delete(cv_id)
        
        # Log deletion
        logger.info(
            "CV deleted",
            cv_id=cv_id,
            user_id=user_id,
            candidate_name=existing_cv.candidate_name
        )
        
        return result
    
    async def _handle_cv_deletion_business_rules(self, cv: CV) -> None:
        """
        Handle business logic before CV deletion.
        
        This private method handles:
        - Archiving CV data for compliance
        - Notifying related services
        - Updating user statistics
        
        Args:
            cv: CV model being deleted
        """
        # Archive CV data for compliance
        await self._archive_cv_data(cv)
        
        # Update user statistics
        user = await self.db.get(User, cv.user_id)
        if user:
            user.cv_count = max(0, user.cv_count - 1)
            await self.db.commit()
        
        # Notify related services
        await self._notify_cv_deletion(cv.id)
    
    async def _archive_cv_data(self, cv: CV) -> None:
        """
        Archive CV data for compliance purposes.
        
        Args:
            cv: CV model to archive
        """
        # Implementation would depend on archiving strategy
        # Could store in separate table or external service
        logger.debug(f"Archiving CV data for {cv.id}")
    
    async def _notify_cv_deletion(self, cv_id: str) -> None:
        """
        Notify related services about CV deletion.
        
        Args:
            cv_id: ID of the deleted CV
        """
        # Implementation would depend on notification strategy
        # Could publish to message queue or call webhooks
        logger.debug(f"Notifying services about CV deletion: {cv_id}")
```

### Rationale
Backend business logic must be documented for maintainability and knowledge transfer.