# Backend Data Integrity Rules

## BE-DATA-001: Schema-First Validation (Critical)
**Rule**: Define Pydantic schemas with field validators before creating database models to ensure data consistency

### Implementation
```python
# ✅ ALWAYS define schemas before models
# schemas/cv.py
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum

class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class CVCreateSchema(BaseModel):
    candidate_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    skills: List[str] = Field(..., min_length=1)
    experience_years: int = Field(..., ge=0, le=50)
    
    @field_validator('skills')
    @classmethod
    def validate_skills(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError('skills cannot be empty')
        return [s.strip().lower() for s in v if s.strip()]
    
    @field_validator('candidate_name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('candidate_name cannot be empty')
        return v.strip().title()

# Now create the database model based on schema
# models/cv.py
from sqlalchemy import Column, String, Integer, JSON, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CV(Base):
    __tablename__ = "cvs"
    
    id = Column(String, primary_key=True, index=True)
    candidate_name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    skills = Column(JSON, nullable=False)
    experience_years = Column(Integer, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Rationale
Backend data validation is the first line of defense against invalid data.

---

## BE-DATA-002: Database Constraints (Critical)
**Rule**: Use database constraints (NOT NULL, UNIQUE, FOREIGN KEY) and SQLAlchemy models with proper relationships

### Implementation
```python
# ✅ ALWAYS enforce constraints at database level
# models/base.py
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TimestampMixin:
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class BaseModel(Base, TimestampMixin):
    __abstract__ = True
    id = Column(String, primary_key=True, index=True, nullable=False)

# models/cv.py
from sqlalchemy import Column, String, Integer, JSON, Boolean, ForeignKey, text
from sqlalchemy.orm import relationship
from .base import BaseModel

class CV(BaseModel):
    __tablename__ = "cvs"
    
    candidate_name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    skills = Column(JSON, nullable=False)
    experience_years = Column(Integer, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships with foreign key constraints
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="cvs")
    
    matches = relationship("CVMatch", back_populates="cv", cascade="all, delete-orphan")
    
    # Table constraints
    __table_args__ = (
        {"schema": "cv_match"},
        # Check constraints
        CheckConstraint('experience_years >= 0', name='check_experience_positive'),
        CheckConstraint('length(candidate_name) >= 1', name='check_name_not_empty'),
    )

# models/user.py
class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    cvs = relationship("CV", back_populates="user", cascade="all, delete-orphan")
```

### Rationale
Backend database must enforce data integrity at the storage level.

---

## BE-DATA-003: Transaction Management (High)
**Rule**: Implement database transactions with proper commit/rollback handling for multi-step operations

### Implementation
```python
# ✅ ALWAYS use transactions for multi-step operations
# services/cv_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

class CVService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_cv_with_skills(self, cv_data: CVCreateSchema, user_id: str) -> CVResponse:
        """Create CV and associated skills in a single transaction"""
        try:
            # Start transaction (automatically handled by AsyncSession context)
            
            # 1. Create CV
            cv = CV(
                candidate_name=cv_data.candidate_name,
                email=cv_data.email,
                skills=cv_data.skills,
                experience_years=cv_data.experience_years,
                user_id=user_id
            )
            self.db.add(cv)
            
            # 2. Create skill records if needed
            for skill_name in cv_data.skills:
                skill = await self._get_or_create_skill(skill_name)
                cv_skill = CVSkill(cv_id=cv.id, skill_id=skill.id)
                self.db.add(cv_skill)
            
            # 3. Update user statistics
            user = await self.db.get(User, user_id)
            user.cv_count += 1
            
            # Commit all changes
            await self.db.commit()
            await self.db.refresh(cv)
            
            return CVResponse.from_orm(cv)
            
        except Exception as e:
            # Rollback on any error
            await self.db.rollback()
            logger.error(f"Failed to create CV: {e}")
            raise CVCreationError(f"Failed to create CV: {str(e)}")
    
    async def transfer_cv_ownership(self, cv_id: str, from_user_id: str, to_user_id: str) -> bool:
        """Transfer CV ownership with audit trail"""
        try:
            # Get CV with lock to prevent concurrent modifications
            cv = await self.db.execute(
                select(CV).where(CV.id == cv_id).with_for_update()
            )
            cv = cv.scalar_one_or_none()
            
            if not cv or cv.user_id != from_user_id:
                raise CVNotFoundError(f"CV {cv_id} not found or not owned by user")
            
            # Create audit record
            audit = CVOwnershipAudit(
                cv_id=cv_id,
                from_user_id=from_user_id,
                to_user_id=to_user_id,
                transferred_at=datetime.utcnow()
            )
            self.db.add(audit)
            
            # Update CV ownership
            cv.user_id = to_user_id
            
            # Update user statistics
            from_user = await self.db.get(User, from_user_id)
            to_user = await self.db.get(User, to_user_id)
            
            from_user.cv_count -= 1
            to_user.cv_count += 1
            
            await self.db.commit()
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to transfer CV ownership: {e}")
            raise

# Database session dependency with transaction handling
# core/dependencies.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### Rationale
Backend operations involving multiple tables must be atomic to maintain consistency.

---

## BE-DATA-004: Database Migrations (High)
**Rule**: Use database migrations with Alembic to manage schema changes with proper versioning and rollback capabilities

### Implementation
```python
# ✅ ALWAYS use migrations for schema changes
# alembic/env.py
from alembic import context
from sqlalchemy import engine_from_config, pool
from app.db.database import Base
from app.models import *  # Import all models

# Target metadata for autogenerate support
target_metadata = Base.metadata

def run_migrations_online():
    """Run migrations in 'online' mode"""
    connectable = engine_from_config(
        context.config.get_section(context.config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()

# Migration example: migrations/versions/001_add_cv_table.py
"""Add CV table

Revision ID: 001
Revises: 
Create Date: 2024-01-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create cvs table
    op.create_table('cvs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('candidate_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('skills', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('experience_years', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.CheckConstraint('experience_years >= 0', name='check_experience_positive')
    )
    op.create_index(op.f('ix_cvs_candidate_name'), 'cvs', ['candidate_name'], unique=False)
    op.create_index(op.f('ix_cvs_email'), 'cvs', ['email'], unique=True)
    op.create_index(op.f('ix_cvs_experience_years'), 'cvs', ['experience_years'], unique=False)
    op.create_index(op.f('ix_cvs_id'), 'cvs', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_cvs_id'), table_name='cvs')
    op.drop_index(op.f('ix_cvs_experience_years'), table_name='cvs')
    op.drop_index(op.f('ix_cvs_email'), table_name='cvs')
    op.drop_index(op.f('ix_cvs_candidate_name'), table_name='cvs')
    op.drop_table('cvs')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

# Migration management script
# scripts/migrate.py
import asyncio
from alembic.config import Config
from alembic import command

async def run_migrations():
    """Run database migrations"""
    alembic_cfg = Config("alembic.ini")
    
    # Upgrade to latest
    command.upgrade(alembic_cfg, "head")
    print("Migrations completed successfully")

async def rollback_migration(revision: str):
    """Rollback to specific revision"""
    alembic_cfg = Config("alembic.ini")
    command.downgrade(alembic_cfg, revision)
    print(f"Rolled back to revision: {revision}")

if __name__ == "__main__":
    asyncio.run(run_migrations())
```

### Rationale
Backend database schema changes must be managed systematically across environments.

---

## BE-DATA-005: Foreign Key Relationships (Medium)
**Rule**: Implement proper foreign key relationships with cascade options appropriate to business logic

### Implementation
```python
# ✅ ALWAYS define proper relationships with cascade rules
# models/cv.py
from sqlalchemy import Column, String, Integer, ForeignKey, text
from sqlalchemy.orm import relationship
from sqlalchemy.schema import CheckConstraint

class CV(BaseModel):
    __tablename__ = "cvs"
    
    candidate_name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    skills = Column(JSON, nullable=False)
    experience_years = Column(Integer, nullable=False, index=True)
    
    # Foreign key with cascade delete
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="cvs")
    
    # One-to-many relationships
    matches = relationship(
        "CVMatch", 
        back_populates="cv", 
        cascade="all, delete-orphan",  # Delete matches when CV is deleted
        passive_deletes=True  # Use database-level cascade
    )
    
    # Many-to-many relationships
    skill_associations = relationship(
        "CVSkillAssociation",
        back_populates="cv",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        CheckConstraint('experience_years >= 0', name='check_experience_positive'),
    )

# models/match.py
class CVMatch(BaseModel):
    __tablename__ = "cv_matches"
    
    score = Column(Integer, nullable=False)
    match_percentage = Column(Integer, nullable=False)
    
    # Foreign keys with proper cascade behavior
    cv_id = Column(String, ForeignKey("cvs.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    cv = relationship("CV", back_populates="matches")
    job = relationship("Job", back_populates="matches")
    
    # Ensure unique CV-Job combinations
    __table_args__ = (
        UniqueConstraint('cv_id', 'job_id', name='unique_cv_job_match'),
    )

# models/skill.py
class Skill(BaseModel):
    __tablename__ = "skills"
    
    name = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(String(50), nullable=False)
    
    # Many-to-many through association table
    cvs = relationship(
        "CV",
        secondary="cv_skill_associations",
        back_populates="skills",
        passive_deletes=True
    )

# Association table for many-to-many relationships
class CVSkillAssociation(BaseModel):
    __tablename__ = "cv_skill_associations"
    
    proficiency_level = Column(Integer, nullable=False)  # 1-5 scale
    years_experience = Column(Integer, nullable=False)
    
    # Foreign keys with cascade delete
    cv_id = Column(String, ForeignKey("cvs.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(String, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    cv = relationship("CV", back_populates="skill_associations")
    skill = relationship("Skill", back_populates="cvs")
    
    # Ensure unique CV-Skill combinations
    __table_args__ = (
        UniqueConstraint('cv_id', 'skill_id', name='unique_cv_skill'),
        CheckConstraint('proficiency_level BETWEEN 1 AND 5', name='check_proficiency_range'),
        CheckConstraint('years_experience >= 0', name='check_skill_experience_positive'),
    )

# Business logic for cascade operations
# services/cv_service.py
class CVService:
    async def delete_cv(self, cv_id: str, user_id: str) -> bool:
        """Delete CV and all related data with proper cascade handling"""
        try:
            # Get CV with all relationships
            cv = await self.db.execute(
                select(CV).options(
                    selectinload(CV.matches),
                    selectinload(CV.skill_associations)
                ).where(CV.id == cv_id, CV.user_id == user_id)
            )
            cv = cv.scalar_one_or_none()
            
            if not cv:
                raise CVNotFoundError(f"CV {cv_id} not found")
            
            # Business logic before deletion
            await self._handle_cv_deletion_business_rules(cv)
            
            # Delete CV (cascade will handle related records)
            await self.db.delete(cv)
            await self.db.commit()
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete CV: {e}")
            raise
    
    async def _handle_cv_deletion_business_rules(self, cv: CV):
        """Handle business logic before CV deletion"""
        # Archive CV data for compliance
        await self._archive_cv_data(cv)
        
        # Update user statistics
        user = await self.db.get(User, cv.user_id)
        user.cv_count = max(0, user.cv_count - 1)
        
        # Notify related services
        await self._notify_cv_deletion(cv.id)
```

### Rationale
Backend must maintain referential integrity while handling related data operations.