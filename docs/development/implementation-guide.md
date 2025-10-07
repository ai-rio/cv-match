# Resume-Matcher Implementation Guide

## Quick Start Implementation

This guide provides step-by-step instructions for integrating Resume-Matcher functionality into your CV-Match platform.

## Prerequisites

- Access to Resume-Matcher codebase at `/home/carlos/projects/Resume-Matcher`
- Your CV-Match project should be fully set up and running
- Supabase CLI configured and working
- Node.js and Python development environments

## Step 1: Backend Services Integration

### 1.1 Copy Core Services

```bash
# Create services directory if it doesn't exist
mkdir -p /home/carlos/projects/cv-match/backend/app/services

# Copy core matching and processing services
cp /home/carlos/projects/Resume-Matcher/apps/backend/app/services/score_improvement_service.py \
   /home/carlos/projects/cv-match/backend/app/services/
cp /home/carlos/projects/Resume-Matcher/apps/backend/app/services/resume_service.py \
   /home/carlos/projects/cv-match/backend/app/services/
cp /home/carlos/projects/Resume-Matcher/apps/backend/app/services/job_service.py \
   /home/carlos/projects/cv-match/backend/app/services/

# Copy SaaS infrastructure services
cp /home/carlos/projects/Resume-Matcher/apps/backend/app/services/usage_limit_service.py \
   /home/carlos/projects/cv-match/backend/app/services/
cp /home/carlos/projects/Resume-Matcher/apps/backend/app/services/payment_verification.py \
   /home/carlos/projects/cv-match/backend/app/services/
cp /home/carlos/projects/Resume-Matcher/apps/backend/app/services/stripe_service.py \
   /home/carlos/projects/cv-match/backend/app/services/

# Copy exceptions module
cp /home/carlos/projects/Resume-Matcher/apps/backend/app/services/exceptions.py \
   /home/carlos/projects/cv-match/backend/app/services/
```

### 1.2 Copy Agent System (LLM Abstraction)

```bash
# Create agent directory
mkdir -p /home/carlos/projects/cv-match/backend/app/agent

# Copy agent components
cp -r /home/carlos/projects/Resume-Matcher/apps/backend/app/agent/* \
   /home/carlos/projects/cv-match/backend/app/agent/
```

### 1.3 Copy Schemas and Prompts

```bash
# Copy schemas
mkdir -p /home/carlos/projects/cv-match/backend/app/schemas
cp -r /home/carlos/projects/Resume-Matcher/apps/backend/app/schemas/* \
   /home/carlos/projects/cv-match/backend/app/schemas/

# Copy prompts
mkdir -p /home/carlos/projects/cv-match/backend/app/prompt
cp -r /home/carlos/projects/Resume-Matcher/apps/backend/app/prompt/* \
   /home/carlos/projects/cv-match/backend/app/prompt/
```

### 1.4 Update Dependencies

Add these to your `/home/carlos/projects/cv-match/backend/requirements.txt`:

```txt
markitdown==0.1.2
numpy>=1.24.0
markdown>=3.4.0
pydantic>=2.0.0
```

### 1.5 Update Environment Variables

Add these to your `.env` file:

```bash
# Resume-Matcher Configuration
RESUME_MATCHER_LLM_PROVIDER=openrouter
RESUME_MATCHER_LLM_MODEL=anthropic/claude-3.5-sonnet
RESUME_MATCHER_EMBEDDING_PROVIDER=openai
RESUME_MATCHER_EMBEDDING_MODEL=text-embedding-3-small
```

## Step 2: Database Schema Integration

### 2.1 Create Migration Files

Create `/home/carlos/projects/cv-match/supabase/migrations/20250107_create_resume_tables.sql`:

```sql
-- Resume tables
CREATE TABLE resumes (
    resume_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    original_filename TEXT,
    file_content TEXT,
    content_type TEXT DEFAULT 'text/markdown',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE processed_resumes (
    resume_id UUID REFERENCES resumes(id) ON DELETE CASCADE,
    personal_data JSONB,
    experiences JSONB,
    projects JSONB,
    skills JSONB,
    research_work JSONB,
    achievements JSONB,
    education JSONB,
    extracted_keywords JSONB,
    processed_at TIMESTAMP DEFAULT NOW()
);

-- Job tables
CREATE TABLE jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    resume_id UUID REFERENCES resumes(id) ON DELETE CASCADE,
    title TEXT,
    description TEXT,
    content_type TEXT DEFAULT 'text/markdown',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE processed_jobs (
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    job_title TEXT,
    company_profile JSONB,
    location JSONB,
    date_posted TEXT,
    employment_type TEXT,
    job_summary TEXT,
    key_responsibilities JSONB,
    qualifications JSONB,
    compensation_and_benefits JSONB,
    application_info JSONB,
    extracted_keywords JSONB,
    processed_at TIMESTAMP DEFAULT NOW()
);

-- Matching results
CREATE TABLE match_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id UUID REFERENCES resumes(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    original_score FLOAT,
    new_score FLOAT,
    updated_resume TEXT,
    resume_preview JSONB,
    improvements JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 2.2 Create SaaS Infrastructure Tables

Create `/home/carlos/projects/cv-match/supabase/migrations/20250107_create_saas_tables.sql`:

```sql
-- User profiles for SaaS features
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    subscription_tier TEXT DEFAULT 'free',
    credits_remaining INTEGER DEFAULT 5,
    stripe_customer_id TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Usage tracking
CREATE TABLE usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    action_type TEXT, -- 'resume_upload', 'job_analysis', 'resume_optimization'
    credits_consumed INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    stripe_subscription_id TEXT,
    status TEXT, -- 'active', 'cancelled', 'past_due', 'unpaid'
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert RLS policies
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own profile" ON user_profiles FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own usage" ON usage_tracking FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own usage" ON usage_tracking FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own subscriptions" ON subscriptions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own subscriptions" ON subscriptions FOR UPDATE USING (auth.uid() = user_id);
```

### 2.3 Apply Migrations

```bash
cd /home/carlos/projects/cv-match
supabase db push
```

## Step 3: Frontend Integration

### 3.1 Copy Components

```bash
# Copy common components
mkdir -p /home/carlos/projects/cv-match/frontend/components/common
cp /home/carlos/projects/Resume-Matcher/apps/frontend/components/common/file-upload.tsx \
   /home/carlos/projects/cv-match/frontend/components/common/
cp /home/carlos/projects/Resume-Matcher/apps/frontend/components/common/background-container.tsx \
   /home/carlos/projects/cv-match/frontend/components/common/

# Copy dashboard components
mkdir -p /home/carlos/projects/cv-match/frontend/components/dashboard
cp /home/carlos/projects/Resume-Matcher/apps/frontend/components/dashboard/resume-analysis.tsx \
   /home/carlos/projects/cv-match/frontend/components/dashboard/
cp /home/carlos/projects/Resume-Matcher/apps/frontend/components/dashboard/resume-component.tsx \
   /home/carlos/projects/cv-match/frontend/components/dashboard/
cp /home/carlos/projects/Resume-Matcher/apps/frontend/components/dashboard/job-listings.tsx \
   /home/carlos/projects/cv-match/frontend/components/dashboard/
cp /home/carlos/projects/Resume-Matcher/apps/frontend/components/dashboard/paste-job-description.tsx \
   /home/carlos/projects/cv-match/frontend/components/dashboard/

# Copy usage components
mkdir -p /home/carlos/projects/cv-match/frontend/components/usage
cp -r /home/carlos/projects/Resume-Matcher/apps/frontend/components/usage/* \
   /home/carlos/projects/cv-match/frontend/components/usage/

# Copy payment components
mkdir -p /home/carlos/projects/cv-match/frontend/components/payment
cp -r /home/carlos/projects/Resume-Matcher/apps/frontend/components/payment/* \
   /home/carlos/projects/cv-match/frontend/components/payment/
```

### 3.2 Copy Utilities and Hooks

```bash
# Copy hooks
mkdir -p /home/carlos/projects/cv-match/frontend/hooks
cp /home/carlos/projects/Resume-Matcher/apps/frontend/hooks/use-file-upload.ts \
   /home/carlos/projects/cv-match/frontend/hooks/
cp /home/carlos/projects/Resume-Matcher/apps/frontend/hooks/useAuth.ts \
   /home/carlos/projects/cv-match/frontend/hooks/
cp /home/carlos/projects/Resume-Matcher/apps/frontend/hooks/useUsage.ts \
   /home/carlos/projects/cv-match/frontend/hooks/

# Copy API utilities
mkdir -p /home/carlos/projects/cv-match/frontend/lib/api
cp /home/carlos/projects/Resume-Matcher/apps/frontend/lib/api/resume.ts \
   /home/carlos/projects/cv-match/frontend/lib/api/
cp /home/carlos/projects/Resume-Matcher/apps/frontend/lib/api/payments.ts \
   /home/carlos/projects/cv-match/frontend/lib/api/
```

### 3.3 Update Frontend Dependencies

Add to `/home/carlos/projects/cv-match/frontend/package.json`:

```json
{
  "dependencies": {
    "lucide-react": "^0.263.1"
  }
}
```

Install dependencies:

```bash
cd /home/carlos/projects/cv-match/frontend
bun install lucide-react
```

### 3.4 Update Environment Variables

Add to `/home/carlos/projects/cv-match/frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Step 4: API Integration

### 4.1 Copy API Routes

```bash
# Create v1 router directory
mkdir -p /home/carlos/projects/cv-match/backend/app/api/router/v1

# Copy API routes
cp /home/carlos/projects/Resume-Matcher/apps/backend/app/api/router/v1/resume.py \
   /home/carlos/projects/cv-match/backend/app/api/router/v1/
cp /home/carlos/projects/Resume-Matcher/apps/backend/app/api/router/v1/payments.py \
   /home/carlos/projects/cv-match/backend/app/api/router/v1/
cp /home/carlos/projects/Resume-Matcher/apps/backend/app/api/router/v1/usage.py \
   /home/carlos/projects/cv-match/backend/app/api/router/v1/
```

### 4.2 Update Main Router

Update `/home/carlos/projects/cv-match/backend/app/api/router/__init__.py`:

```python
from .v1 import v1_router
from .health import health_check

__all__ = ["v1_router", "health_check"]
```

### 4.3 Update Core Configuration

Update `/home/carlos/projects/cv-match/backend/app/core/config.py` to include Resume-Matcher settings:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Existing settings...

    # Resume-Matcher settings
    RESUME_MATCHER_LLM_PROVIDER: str = "openrouter"
    RESUME_MATCHER_LLM_MODEL: str = "anthropic/claude-3.5-sonnet"
    RESUME_MATCHER_EMBEDDING_PROVIDER: str = "openai"
    RESUME_MATCHER_EMBEDDING_MODEL: str = "text-embedding-3-small"

    class Config:
        env_file = ".env"

settings = Settings()
```

## Step 5: Integration Testing

### 5.1 Test Backend Services

Create a test file `/home/carlos/projects/cv-match/backend/test_resume_integration.py`:

```python
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.resume_service import ResumeService
from app.services.job_service import JobService
from app.services.score_improvement_service import ScoreImprovementService
from app.core.database import SupabaseSession

async def test_services():
    """Test the integrated Resume-Matcher services"""

    db = SupabaseSession()

    # Test ResumeService
    print("Testing ResumeService...")
    resume_service = ResumeService(db)
    # Add your test logic here

    # Test JobService
    print("Testing JobService...")
    job_service = JobService(db)
    # Add your test logic here

    # Test ScoreImprovementService
    print("Testing ScoreImprovementService...")
    score_service = ScoreImprovementService(db)
    # Add your test logic here

    print("All services initialized successfully!")

if __name__ == "__main__":
    asyncio.run(test_services())
```

### 5.2 Test Frontend Components

Create a test page `/home/carlos/projects/cv-match/frontend/app/test-resume/page.tsx`:

```tsx
'use client';

import FileUpload from '@/components/common/file-upload';

export default function TestResumePage() {
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Resume Upload Test</h1>
      <FileUpload />
    </div>
  );
}
```

## Step 6: Launch Preparation

### 6.1 Update User Model

Extend your existing User model in `/home/carlos/projects/cv-match/backend/app/models/user.py`:

```python
from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class SubscriptionTier(enum.StrEnum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"))
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    credits_remaining = Column(Integer, default=5)
    stripe_customer_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profile")
    resumes = relationship("Resume", back_populates="user_profile")
```

### 6.2 Create Service Integration Layer

Create `/home/carlos/projects/cv-match/backend/app/services/resume_integration_service.py`:

```python
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from .resume_service import ResumeService
from .job_service import JobService
from .score_improvement_service import ScoreImprovementService
from .credit_service import CreditService

class ResumeIntegrationService:
    """High-level service for resume matching operations"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.resume_service = ResumeService(db)
        self.job_service = JobService(db)
        self.score_service = ScoreImprovementService(db)
        self.credit_service = CreditService(db)

    async def analyze_resume_against_job(
        self,
        user_id: str,
        resume_id: str,
        job_description: str
    ) -> Dict[str, Any]:
        """
        Complete resume analysis workflow
        1. Check credits
        2. Create job posting
        3. Calculate match score
        4. Generate improvements
        5. Deduct credits
        """

        # Check if user has credits
        has_credits = await self.credit_service.check_credits(user_id, 1)
        if not has_credits:
            raise ValueError("Insufficient credits")

        # Create job posting
        job_data = {
            "resume_id": resume_id,
            "job_descriptions": [job_description]
        }
        job_ids = await self.job_service.create_and_store_job(job_data)
        job_id = job_ids[0]

        # Calculate match score and improvements
        result = await self.score_service.run(resume_id, job_id)

        # Deduct credits
        await self.credit_service.deduct_credits(
            user_id, 1, "resume_analysis"
        )

        return result
```

## Troubleshooting

### Common Issues and Solutions

1. **Import Errors**: Ensure all copied files have the correct import paths
2. **Database Errors**: Check that migrations were applied correctly
3. **Environment Variables**: Verify all required variables are set
4. **Authentication**: Ensure Supabase auth is properly configured
5. **Dependencies**: Install all required Python and bun packages

### Debug Mode

To enable debug logging, add to your `.env`:

```bash
LOG_LEVEL=DEBUG
RESUME_MATCHER_DEBUG=true
```

## Next Steps

After completing this implementation guide:

1. Test the core resume upload and analysis workflow
2. Implement user interface pages
3. Set up payment processing with Stripe
4. Configure subscription tiers and credit systems
5. Deploy to staging environment for final testing

This implementation provides a solid foundation for a competitive CV matching SaaS platform with minimal development time.
