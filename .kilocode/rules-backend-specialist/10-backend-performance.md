# Backend Performance Rules

## BE-PER-001: Async Operations (Critical)
**Rule**: Use async/await for all I/O operations including database queries, external API calls, and file operations

### Implementation
```python
# ✅ ALWAYS use async for I/O operations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

async def get_cv_by_id(db: AsyncSession, cv_id: str) -> Optional[CV]:
    result = await db.execute(
        select(CV).where(CV.id == cv_id)
    )
    return result.scalar_one_or_none()

async def fetch_external_data(api_url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)
        response.raise_for_status()
        return response.json()

async def process_file_upload(file_path: str) -> dict:
    async with aiofiles.open(file_path, 'rb') as f:
        content = await f.read()
    return await parse_content(content)

# ✅ Concurrent operations with asyncio
import asyncio

async def process_multiple_cvs(cv_ids: List[str], db: AsyncSession):
    tasks = [get_cv_by_id(db, cv_id) for cv_id in cv_ids]
    return await asyncio.gather(*tasks)
```

### Rationale
Backend systems are I/O-bound; async operations maximize throughput and scalability.

---

## BE-PER-002: Database Connection Pooling (Critical)
**Rule**: Implement database connection pooling with asyncpg for PostgreSQL and use AsyncSession for SQLAlchemy operations

### Implementation
```python
# ✅ ALWAYS use connection pooling
# db/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

# Development with simple pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Production with optimized pooling
production_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=20,          # Number of connections to keep open
    max_overflow=30,       # Additional connections beyond pool_size
    pool_pre_ping=True,    # Validate connections before use
    pool_recycle=3600,     # Recycle connections after 1 hour
)

async_session_maker = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Dependency for getting DB session
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
Backend database connections are expensive resources; pooling ensures efficient reuse.

---

## BE-PER-003: Redis Caching (High)
**Rule**: Implement Redis caching for expensive operations like database queries, API responses, and computed results with proper TTL

### Implementation
```python
# ✅ ALWAYS implement caching for expensive operations
import redis.asyncio as redis
import json
from functools import wraps
from typing import Optional, Any

# Redis connection
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def cache_result(key_prefix: str, ttl: int = 3600):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await redis_client.setex(
                cache_key, 
                ttl, 
                json.dumps(result, default=str)
            )
            return result
        return wrapper
    return decorator

# Usage examples
@cache_result("cv_by_id", ttl=1800)  # 30 minutes
async def get_cv_by_id_cached(cv_id: str) -> Optional[dict]:
    cv = await cv_service.get_by_id(cv_id)
    return cv.dict() if cv else None

@cache_result("matching_results", ttl=900)  # 15 minutes
async def compute_matching_score(cv_id: str, job_id: str) -> dict:
    return await matching_service.calculate_score(cv_id, job_id)

# Cache invalidation
async def invalidate_cv_cache(cv_id: str):
    pattern = f"*:{cv_id}*"
    keys = await redis_client.keys(pattern)
    if keys:
        await redis_client.delete(*keys)
```

### Rationale
Backend performance is critical for response times; caching reduces redundant processing.

---

## BE-PER-004: Database Optimization (High)
**Rule**: Use database indexes strategically on frequently queried columns and foreign keys; analyze query performance with EXPLAIN

### Implementation
```python
# ✅ ALWAYS optimize database queries
from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped, mapped_column

class CV(Base):
    __tablename__ = "cvs"
    
    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    candidate_name: Mapped[str] = mapped_column(index=True)  # Frequently searched
    email: Mapped[str] = mapped_column(unique=True, index=True)
    skills: Mapped[dict] = mapped_column(JSON)
    experience_years: Mapped[int] = mapped_column(index=True)
    created_at: Mapped[datetime] = mapped_column(index=True)
    
    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_cv_experience_skills', 'experience_years', text('skills')),
        Index('idx_cv_name_created', 'candidate_name', 'created_at'),
    )

# Query optimization examples
async def get_cvs_by_skill_range(
    db: AsyncSession, 
    min_experience: int, 
    max_experience: int
):
    # ✅ Use indexed columns in WHERE clause
    query = select(CV).where(
        CV.experience_years.between(min_experience, max_experience)
    ).order_by(CV.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

# Query analysis
async def analyze_query_performance(db: AsyncSession):
    # ✅ Use EXPLAIN ANALYZE for slow queries
    explain_query = text("""
        EXPLAIN ANALYZE 
        SELECT * FROM cvs 
        WHERE experience_years > 5 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    
    result = await db.execute(explain_query)
    return result.fetchall()

# Bulk operations for performance
async def bulk_insert_cvs(db: AsyncSession, cvs_data: List[dict]):
    # ✅ Use bulk_insert_mappings for better performance
    await db.execute(
        insert(CV), 
        cvs_data
    )
    await db.commit()
```

### Rationale
Backend database performance impacts overall system responsiveness.

---

## BE-PER-005: Background Tasks (Medium)
**Rule**: Implement background tasks for heavy processing using FastAPI BackgroundTasks or Celery with Redis broker

### Implementation
```python
# ✅ ALWAYS use background tasks for heavy operations
from fastapi import BackgroundTasks
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Simple background tasks with FastAPI
@router.post("/process-cv/{cv_id}")
async def process_cv_endpoint(
    cv_id: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(process_cv_heavy, cv_id)
    return {"status": "processing", "cv_id": cv_id}

async def process_cv_heavy(cv_id: str):
    """Heavy processing that shouldn't block response"""
    try:
        # Simulate heavy processing
        await asyncio.sleep(10)
        
        # Update CV status
        await update_cv_processing_status(cv_id, "completed")
        
        # Send notification
        await send_completion_notification(cv_id)
        
    except Exception as e:
        logger.error(f"Error processing CV {cv_id}: {e}")
        await update_cv_processing_status(cv_id, "failed")

# For more complex tasks, use Celery
from celery import Celery

celery_app = Celery(
    "cv_processor",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

@celery_app.task(bind=True)
def process_cv_with_celery(self, cv_id: str):
    """Heavy processing with Celery for better scalability"""
    try:
        # Update progress
        self.update_state(state="PROGRESS", meta={"current": 0, "total": 100})
        
        # Process CV in chunks
        for i in range(10):
            await process_cv_chunk(cv_id, chunk=i)
            self.update_state(
                state="PROGRESS", 
                meta={"current": (i + 1) * 10, "total": 100}
            )
        
        return {"status": "completed", "cv_id": cv_id}
        
    except Exception as exc:
        self.update_state(
            state="FAILURE",
            meta={"error": str(exc)}
        )
        raise

# Task monitoring
@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "state": task.state,
        "result": task.result if task.state == "SUCCESS" else None,
        "error": str(task.info) if task.state == "FAILURE" else None
    }
```

### Rationale
Backend should remain responsive for user requests while processing long-running tasks.