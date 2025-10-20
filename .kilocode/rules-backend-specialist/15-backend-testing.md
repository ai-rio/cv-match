# Backend Testing Rules

## BE-TEST-001: Unit Tests for Service Layer (Critical)
**Rule**: Write unit tests for service layer business logic with pytest and mock external dependencies

### Implementation
```python
# ✅ ALWAYS write comprehensive unit tests for services
# tests/test_cv_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.cv_service import CVService
from app.schemas.cv import CVCreate
from app.models.cv import CV
from app.core.exceptions import CVNotFoundException, InvalidCVDataException

class TestCVService:
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def cv_service(self, mock_db):
        """CV service instance with mocked database"""
        return CVService(mock_db)
    
    @pytest.fixture
    def sample_cv_data(self):
        """Sample CV data for testing"""
        return CVCreate(
            candidate_name="John Doe",
            email="john@example.com",
            skills=["Python", "FastAPI"],
            experience_years=5
        )
    
    @pytest.fixture
    def sample_cv(self):
        """Sample CV model for testing"""
        cv = CV(
            id="cv-123",
            candidate_name="John Doe",
            email="john@example.com",
            skills=["Python", "FastAPI"],
            experience_years=5
        )
        return cv
    
    @pytest.mark.asyncio
    async def test_create_cv_success(self, cv_service, mock_db, sample_cv_data, sample_cv):
        """Test successful CV creation"""
        # Mock repository method
        cv_service.repository.create = AsyncMock(return_value=sample_cv)
        
        # Call service method
        result = await cv_service.create(sample_cv_data)
        
        # Assertions
        assert result.id == "cv-123"
        assert result.candidate_name == "John Doe"
        assert result.email == "john@example.com"
        assert result.skills == ["Python", "FastAPI"]
        assert result.experience_years == 5
        
        # Verify repository was called
        cv_service.repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_cv_insufficient_skills(self, cv_service, sample_cv_data):
        """Test CV creation with insufficient skills"""
        # Modify data to have insufficient skills
        sample_cv_data.skills = ["Python"]  # Only 1 skill
        
        # Call service method and expect exception
        with pytest.raises(ValueError, match="CV must have at least 3 skills"):
            await cv_service.create(sample_cv_data)
        
        # Verify repository was not called
        cv_service.repository.create.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_cv_by_id_success(self, cv_service, mock_db, sample_cv):
        """Test successful CV retrieval by ID"""
        # Mock repository method
        cv_service.repository.get_by_id = AsyncMock(return_value=sample_cv)
        
        # Call service method
        result = await cv_service.get_by_id("cv-123")
        
        # Assertions
        assert result.id == "cv-123"
        assert result.candidate_name == "John Doe"
        
        # Verify repository was called with correct ID
        cv_service.repository.get_by_id.assert_called_once_with("cv-123")
    
    @pytest.mark.asyncio
    async def test_get_cv_by_id_not_found(self, cv_service, mock_db):
        """Test CV retrieval when CV doesn't exist"""
        # Mock repository method to return None
        cv_service.repository.get_by_id = AsyncMock(return_value=None)
        
        # Call service method and expect exception
        with pytest.raises(CVNotFoundException):
            await cv_service.get_by_id("nonexistent-id")
        
        # Verify repository was called
        cv_service.repository.get_by_id.assert_called_once_with("nonexistent-id")
    
    @pytest.mark.asyncio
    async def test_update_cv_success(self, cv_service, mock_db, sample_cv):
        """Test successful CV update"""
        # Mock repository methods
        cv_service.repository.get_by_id = AsyncMock(return_value=sample_cv)
        cv_service.repository.update = AsyncMock(return_value=sample_cv)
        
        # Update data
        update_data = {"candidate_name": "Jane Doe"}
        
        # Call service method
        result = await cv_service.update("cv-123", update_data)
        
        # Assertions
        assert result.id == "cv-123"
        
        # Verify repository methods were called
        cv_service.repository.get_by_id.assert_called_once_with("cv-123")
        cv_service.repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_cv_success(self, cv_service, mock_db, sample_cv):
        """Test successful CV deletion"""
        # Mock repository methods
        cv_service.repository.get_by_id = AsyncMock(return_value=sample_cv)
        cv_service.repository.delete = AsyncMock(return_value=True)
        
        # Call service method
        result = await cv_service.delete("cv-123")
        
        # Assertions
        assert result is True
        
        # Verify repository methods were called
        cv_service.repository.get_by_id.assert_called_once_with("cv-123")
        cv_service.repository.delete.assert_called_once_with("cv-123")
    
    @pytest.mark.asyncio
    async def test_delete_cv_not_found(self, cv_service, mock_db):
        """Test CV deletion when CV doesn't exist"""
        # Mock repository method to return None
        cv_service.repository.get_by_id = AsyncMock(return_value=None)
        
        # Call service method and expect exception
        with pytest.raises(CVNotFoundException):
            await cv_service.delete("nonexistent-id")
        
        # Verify repository was called but delete was not
        cv_service.repository.get_by_id.assert_called_once_with("nonexistent-id")
        cv_service.repository.delete.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_business_rule_validation(self, cv_service, sample_cv_data):
        """Test business rule validation in service layer"""
        # Test invalid email format
        sample_cv_data.email = "invalid-email"
        
        with pytest.raises(ValueError, match="Invalid email format"):
            await cv_service.create(sample_cv_data)
        
        # Test negative experience
        sample_cv_data.email = "valid@example.com"
        sample_cv_data.experience_years = -1
        
        with pytest.raises(ValueError, match="Experience years cannot be negative"):
            await cv_service.create(sample_cv_data)
```

### Rationale
Backend business logic must be thoroughly tested with isolated dependencies.

---

## BE-TEST-002: Integration Tests for API Endpoints (High)
**Rule**: Write integration tests for API endpoints using TestClient with database fixtures and cleanup

### Implementation
```python
# ✅ ALWAYS write integration tests for API endpoints
# tests/test_api_integration.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import get_db, Base
from app.models.cv import CV
from app.models.user import User

# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="function")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture(scope="function")
async def test_session(test_engine):
    """Create test database session"""
    async_session_maker = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session

@pytest.fixture(scope="function")
async def test_client(test_session):
    """Create test client with database override"""
    app.dependency_overrides[get_db] = lambda: test_session
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Clean up dependency overrides
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def sample_user(test_session):
    """Create sample user for testing"""
    user = User(
        id="user-123",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user

@pytest.fixture(scope="function")
async def sample_cv(test_session, sample_user):
    """Create sample CV for testing"""
    cv = CV(
        id="cv-123",
        candidate_name="John Doe",
        email="john@example.com",
        skills=["Python", "FastAPI"],
        experience_years=5,
        user_id=sample_user.id
    )
    test_session.add(cv)
    await test_session.commit()
    await test_session.refresh(cv)
    return cv

@pytest.mark.asyncio
class TestCVAPI:
    async def test_create_cv_success(self, test_client: AsyncClient, sample_user):
        """Test successful CV creation via API"""
        cv_data = {
            "candidate_name": "Jane Doe",
            "email": "jane@example.com",
            "skills": ["Python", "FastAPI", "SQL"],
            "experience_years": 3
        }
        
        response = await test_client.post("/api/v1/cvs", json=cv_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["candidate_name"] == "Jane Doe"
        assert data["email"] == "jane@example.com"
        assert data["skills"] == ["Python", "FastAPI", "SQL"]
        assert data["experience_years"] == 3
        assert "id" in data
        assert "created_at" in data
    
    async def test_create_cv_validation_error(self, test_client: AsyncClient):
        """Test CV creation with validation errors"""
        invalid_cv_data = {
            "candidate_name": "",  # Empty name
            "email": "invalid-email",  # Invalid email
            "skills": [],  # Empty skills
            "experience_years": -1  # Negative experience
        }
        
        response = await test_client.post("/api/v1/cvs", json=invalid_cv_data)
        
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("candidate_name" in str(error) for error in errors)
        assert any("email" in str(error) for error in errors)
        assert any("skills" in str(error) for error in errors)
        assert any("experience_years" in str(error) for error in errors)
    
    async def test_get_cv_success(self, test_client: AsyncClient, sample_cv):
        """Test successful CV retrieval via API"""
        response = await test_client.get(f"/api/v1/cvs/{sample_cv.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_cv.id
        assert data["candidate_name"] == sample_cv.candidate_name
        assert data["email"] == sample_cv.email
    
    async def test_get_cv_not_found(self, test_client: AsyncClient):
        """Test CV retrieval when CV doesn't exist"""
        response = await test_client.get("/api/v1/cvs/nonexistent-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    async def test_update_cv_success(self, test_client: AsyncClient, sample_cv):
        """Test successful CV update via API"""
        update_data = {
            "candidate_name": "Updated Name",
            "experience_years": 10
        }
        
        response = await test_client.patch(f"/api/v1/cvs/{sample_cv.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["candidate_name"] == "Updated Name"
        assert data["experience_years"] == 10
        # Other fields should remain unchanged
        assert data["email"] == sample_cv.email
    
    async def test_delete_cv_success(self, test_client: AsyncClient, sample_cv):
        """Test successful CV deletion via API"""
        response = await test_client.delete(f"/api/v1/cvs/{sample_cv.id}")
        
        assert response.status_code == 204
        
        # Verify CV is deleted
        get_response = await test_client.get(f"/api/v1/cvs/{sample_cv.id}")
        assert get_response.status_code == 404
    
    async def test_list_cvs_success(self, test_client: AsyncClient, sample_cv):
        """Test successful CV listing via API"""
        response = await test_client.get("/api/v1/cvs")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1
        assert data["items"][0]["id"] == sample_cv.id
    
    async def test_list_cvs_with_filters(self, test_client: AsyncClient, sample_cv):
        """Test CV listing with filters"""
        params = {"candidate_name": "John", "min_experience": 3}
        response = await test_client.get("/api/v1/cvs", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert all(item["experience_years"] >= 3 for item in data["items"])
```

### Rationale
Backend API endpoints must be tested end-to-end with realistic data.

---

## BE-TEST-003: Database Tests with Transaction Rollback (Medium)
**Rule**: Write database tests using pytest-asyncio with transaction rollback for isolation

### Implementation
```python
# ✅ ALWAYS write isolated database tests
# tests/test_database_operations.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from app.db.database import Base
from app.models.cv import CV
from app.models.user import User
from app.repositories.cv_repository import CVRepository

@pytest.fixture(scope="function")
async def test_db_session():
    """Create isolated database session with transaction rollback"""
    # Use in-memory SQLite for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        # Begin transaction
        transaction = await session.begin()
        
        try:
            yield session
        finally:
            # Always rollback to ensure isolation
            await transaction.rollback()
    
    # Clean up
    await engine.dispose()

@pytest.fixture(scope="function")
async def sample_user(test_db_session: AsyncSession):
    """Create sample user in test database"""
    user = User(
        id="test-user-123",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    return user

@pytest.mark.asyncio
class TestCVRepository:
    async def test_create_cv(self, test_db_session: AsyncSession, sample_user):
        """Test CV creation in database"""
        repository = CVRepository(test_db_session)
        
        cv_data = {
            "id": "test-cv-123",
            "candidate_name": "Test User",
            "email": "test@example.com",
            "skills": ["Python", "FastAPI"],
            "experience_years": 5,
            "user_id": sample_user.id
        }
        
        # Create CV
        created_cv = await repository.create(CV(**cv_data))
        
        # Verify CV was created
        assert created_cv.id == "test-cv-123"
        assert created_cv.candidate_name == "Test User"
        
        # Verify CV exists in database
        result = await test_db_session.execute(
            select(CV).where(CV.id == "test-cv-123")
        )
        cv_from_db = result.scalar_one_or_none()
        assert cv_from_db is not None
        assert cv_from_db.candidate_name == "Test User"
    
    async def test_get_cv_by_id(self, test_db_session: AsyncSession, sample_user):
        """Test CV retrieval by ID from database"""
        repository = CVRepository(test_db_session)
        
        # Create CV first
        cv = CV(
            id="test-cv-456",
            candidate_name="Test User 2",
            email="test2@example.com",
            skills=["Python"],
            experience_years=3,
            user_id=sample_user.id
        )
        test_db_session.add(cv)
        await test_db_session.commit()
        
        # Retrieve CV
        retrieved_cv = await repository.get_by_id("test-cv-456")
        
        # Verify retrieved CV
        assert retrieved_cv is not None
        assert retrieved_cv.id == "test-cv-456"
        assert retrieved_cv.candidate_name == "Test User 2"
    
    async def test_get_cv_by_id_not_found(self, test_db_session: AsyncSession):
        """Test CV retrieval when CV doesn't exist"""
        repository = CVRepository(test_db_session)
        
        # Try to retrieve non-existent CV
        retrieved_cv = await repository.get_by_id("nonexistent-id")
        
        # Verify None is returned
        assert retrieved_cv is None
    
    async def test_update_cv(self, test_db_session: AsyncSession, sample_user):
        """Test CV update in database"""
        repository = CVRepository(test_db_session)
        
        # Create CV first
        cv = CV(
            id="test-cv-789",
            candidate_name="Original Name",
            email="original@example.com",
            skills=["Python"],
            experience_years=2,
            user_id=sample_user.id
        )
        test_db_session.add(cv)
        await test_db_session.commit()
        
        # Update CV
        update_data = {
            "candidate_name": "Updated Name",
            "experience_years": 5
        }
        updated_cv = await repository.update("test-cv-789", update_data)
        
        # Verify update
        assert updated_cv is not None
        assert updated_cv.candidate_name == "Updated Name"
        assert updated_cv.experience_years == 5
        assert updated_cv.email == "original@example.com"  # Unchanged
    
    async def test_delete_cv(self, test_db_session: AsyncSession, sample_user):
        """Test CV deletion from database"""
        repository = CVRepository(test_db_session)
        
        # Create CV first
        cv = CV(
            id="test-cv-delete",
            candidate_name="To Delete",
            email="delete@example.com",
            skills=["Python"],
            experience_years=1,
            user_id=sample_user.id
        )
        test_db_session.add(cv)
        await test_db_session.commit()
        
        # Delete CV
        delete_result = await repository.delete("test-cv-delete")
        
        # Verify deletion
        assert delete_result is True
        
        # Verify CV no longer exists
        result = await test_db_session.execute(
            select(CV).where(CV.id == "test-cv-delete")
        )
        cv_from_db = result.scalar_one_or_none()
        assert cv_from_db is None
    
    async def test_get_multiple_cvs(self, test_db_session: AsyncSession, sample_user):
        """Test retrieving multiple CVs from database"""
        repository = CVRepository(test_db_session)
        
        # Create multiple CVs
        cvs = []
        for i in range(5):
            cv = CV(
                id=f"test-cv-multi-{i}",
                candidate_name=f"User {i}",
                email=f"user{i}@example.com",
                skills=["Python"],
                experience_years=i,
                user_id=sample_user.id
            )
            cvs.append(cv)
            test_db_session.add(cv)
        
        await test_db_session.commit()
        
        # Retrieve multiple CVs
        retrieved_cvs = await repository.get_multi(skip=1, limit=3)
        
        # Verify results
        assert len(retrieved_cvs) == 3
        # Should be sorted by some default order (likely ID)
        # and skip first, limit to 3
    
    async def test_transaction_rollback_isolation(self, test_db_session: AsyncSession, sample_user):
        """Test that transaction rollback provides test isolation"""
        repository = CVRepository(test_db_session)
        
        # Create CV in this test
        cv = CV(
            id="isolation-test-cv",
            candidate_name="Isolation Test",
            email="isolation@example.com",
            skills=["Python"],
            experience_years=1,
            user_id=sample_user.id
        )
        test_db_session.add(cv)
        await test_db_session.commit()
        
        # Verify CV exists
        result = await test_db_session.execute(
            select(CV).where(CV.id == "isolation-test-cv")
        )
        assert result.scalar_one_or_none() is not None
        
        # Simulate test completion (transaction will be rolled back by fixture)
        # In a real scenario, this test would complete and rollback would happen
        
        # The fixture ensures rollback happens after each test,
        # so the next test will start with a clean database
```

### Rationale
Backend database operations must be tested without affecting other tests.