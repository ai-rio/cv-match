---
chunk: 4
total_chunks: 7
title: 2. Resume Matching Endpoints
context: backend/app/api/endpoints/documents.py > 2. Resume Matching Endpoints
estimated_tokens: 3961
source: technical-integration-guide.md
---

<!-- Context: backend/app/services/llm/llm_service.py (Enhanced) > Database Schema Changes -->

## Database Schema Changes


<!-- Context: backend/app/services/llm/llm_service.py (Enhanced) > Database Schema Changes > New Tables for Resume Matching -->

### New Tables for Resume Matching

```sql
-- Resumes table
CREATE TABLE public.resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT,
    original_filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    content_text TEXT,
    metadata JSONB DEFAULT '{}',
    contact_info JSONB DEFAULT '{}',
    sections JSONB DEFAULT '{}',
    quality_score DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Job descriptions table
CREATE TABLE public.job_descriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    company TEXT,
    description TEXT NOT NULL,
    requirements TEXT,
    responsibilities TEXT,
    benefits TEXT,
    location TEXT,
    salary_range TEXT,
    job_type TEXT, -- 'full-time', 'part-time', 'contract', etc.
    remote_option TEXT, -- 'remote', 'hybrid', 'onsite'
    experience_level TEXT, -- 'entry', 'mid', 'senior', 'executive'
    metadata JSONB DEFAULT '{}',
    sections JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Resume embeddings table (for vector similarity)
CREATE TABLE public.resume_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    embedding_type TEXT NOT NULL, -- 'full_text', 'section_experience', etc.
    chunk_text TEXT,
    embedding_vector vector(1536), -- OpenAI embedding size
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Job description embeddings table
CREATE TABLE public.job_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
    embedding_type TEXT NOT NULL,
    chunk_text TEXT,
    embedding_vector vector(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Match results table
CREATE TABLE public.match_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    resume_id UUID NOT NULL REFERENCES resumes(id),
    job_id UUID NOT NULL REFERENCES job_descriptions(id),

    -- Overall scores
    overall_score DECIMAL(5,2) NOT NULL,
    confidence_score DECIMAL(5,2) NOT NULL,

    -- Detailed scores
    skills_score DECIMAL(5,2),
    experience_score DECIMAL(5,2),
    education_score DECIMAL(5,2),
    keyword_score DECIMAL(5,2),

    -- Section-specific scores
    section_scores JSONB DEFAULT '{}',

    -- Analysis results
    match_analysis JSONB DEFAULT '{}',
    skill_gaps JSONB DEFAULT '[]',
    strengths JSONB DEFAULT '[]',

    -- Metadata
    processing_time_ms INTEGER,
    algorithm_version TEXT DEFAULT '1.0',

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Prevent duplicate matches
    UNIQUE(resume_id, job_id)
);

-- AI suggestions table
CREATE TABLE public.ai_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    match_result_id UUID NOT NULL REFERENCES match_results(id) ON DELETE CASCADE,

    -- Suggestion details
    suggestion_type TEXT NOT NULL, -- 'keyword', 'experience', 'skills', 'format', 'content'
    category TEXT NOT NULL, -- 'high_impact', 'medium_impact', 'low_impact'
    title TEXT NOT NULL,
    description TEXT NOT NULL,

    -- Implementation details
    original_text TEXT,
    suggested_text TEXT,
    section_name TEXT,
    line_number INTEGER,

    -- Prioritization
    priority INTEGER NOT NULL DEFAULT 3, -- 1-5 scale (1 = highest)
    impact_score DECIMAL(5,2), -- Estimated impact on match score
    effort_estimate TEXT, -- 'low', 'medium', 'high'

    -- Status tracking
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'implemented', 'rejected'
    implemented_at TIMESTAMPTZ,
    feedback TEXT,

    -- Metadata
    ai_confidence DECIMAL(5,2),
    generated_by TEXT DEFAULT 'gpt-4',

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- User feedback table for continuous improvement
CREATE TABLE public.user_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Feedback target
    target_type TEXT NOT NULL, -- 'match_result', 'suggestion', 'overall'
    target_id UUID,

    -- Feedback content
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,

    -- Context
    context JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for performance
CREATE INDEX idx_resumes_user_id ON public.resumes(user_id);
CREATE INDEX idx_resumes_created_at ON public.resumes(created_at DESC);
CREATE INDEX idx_job_descriptions_user_id ON public.job_descriptions(user_id);
CREATE INDEX idx_job_descriptions_created_at ON public.job_descriptions(created_at DESC);
CREATE INDEX idx_resume_embeddings_resume_id ON public.resume_embeddings(resume_id);
CREATE INDEX idx_resume_embeddings_type ON public.resume_embeddings(embedding_type);
CREATE INDEX idx_job_embeddings_job_id ON public.job_embeddings(job_id);
CREATE INDEX idx_job_embeddings_type ON public.job_embeddings(embedding_type);
CREATE INDEX idx_match_results_user_id ON public.match_results(user_id);
CREATE INDEX idx_match_results_resume_id ON public.match_results(resume_id);
CREATE INDEX idx_match_results_job_id ON public.match_results(job_id);
CREATE INDEX idx_match_results_score ON public.match_results(overall_score DESC);
CREATE INDEX idx_ai_suggestions_match_result_id ON public.ai_suggestions(match_result_id);
CREATE INDEX idx_ai_suggestions_status ON public.ai_suggestions(status);
CREATE INDEX idx_ai_suggestions_priority ON public.ai_suggestions(priority);

-- Vector indexes for similarity search
CREATE INDEX idx_resume_embeddings_vector ON public.resume_embeddings
USING ivfflat (embedding_vector vector_cosine_ops);
CREATE INDEX idx_job_embeddings_vector ON public.job_embeddings
USING ivfflat (embedding_vector vector_cosine_ops);

-- Enable Row Level Security
ALTER TABLE public.resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_descriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.match_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_suggestions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_feedback ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can manage own resumes" ON public.resumes
  USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own job descriptions" ON public.job_descriptions
  USING (auth.uid() = user_id);

CREATE POLICY "Users can view own match results" ON public.match_results
  USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own suggestions" ON public.ai_suggestions
  USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own feedback" ON public.user_feedback
  USING (auth.uid() = user_id);

-- Storage policies for document files
CREATE STORAGE POLICY "Users can upload resume files" ON storage.buckets
  FOR INSERT WITH CHECK (
    bucket_id = 'resumes' AND
    auth.uid()::text = (storage.foldername(name))[1]
  );
```

---


<!-- Context: backend/app/services/llm/llm_service.py (Enhanced) > API Endpoint Specifications -->

## API Endpoint Specifications


<!-- Context: backend/app/services/llm/llm_service.py (Enhanced) > API Endpoint Specifications > Resume Matching API Endpoints -->

### Resume Matching API Endpoints


<!-- Context: backend/app/services/llm/llm_service.py (Enhanced) > API Endpoint Specifications > Resume Matching API Endpoints > 1. Document Upload and Processing -->

#### 1. Document Upload and Processing

```python

<!-- Context: backend/app/api/endpoints/documents.py -->

# backend/app/api/endpoints/documents.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from typing import List
from app.services.resume_matching.document_processing_service import DocumentProcessingService
from app.services.supabase.database import ResumeService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload/resume", status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    title: str = None,
    current_user: User = Depends(get_current_user)
):
    """
    Upload and process a resume file

    Args:
        file: Resume file (PDF or DOCX)
        title: Optional title for the resume
        current_user: Authenticated user

    Returns:
        Processed resume information
    """
    try:
        # Validate file size
        if file.size and file.size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds 10MB limit"
            )

        # Process document
        processing_service = DocumentProcessingService()
        processed_doc = await processing_service.process_document(file, 'resume')

        # Store in database
        resume_service = ResumeService()
        resume_data = {
            'user_id': current_user.id,
            'title': title or file.filename,
            'original_filename': file.filename,
            'file_type': file.filename.split('.')[-1].lower(),
            'file_size': file.size,
            'content_text': processed_doc.text_content,
            'metadata': processed_doc.metadata,
            'contact_info': processed_doc.contact_info,
            'sections': processed_doc.sections,
            'quality_score': processed_doc.quality_score
        }

        resume = await resume_service.create(resume_data)

        # Generate and store embeddings
        from app.services.resume_matching.embedding_service import EmbeddingService
        embedding_service = EmbeddingService()
        embeddings = await embedding_service.generate_document_embeddings(processed_doc)

        embedding_metadata = {
            'user_id': current_user.id,
            'resume_id': resume.id,
            'document_type': 'resume'
        }

        await embedding_service.store_embeddings(resume.id, embeddings, embedding_metadata)

        return {
            "id": resume.id,
            "title": resume.title,
            "quality_score": processed_doc.quality_score,
            "sections_found": list(processed_doc.sections.keys()),
            "contact_info": processed_doc.contact_info,
            "processing_status": "completed"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume processing failed: {str(e)}"
        )

@router.post("/upload/job-description", status_code=status.HTTP_201_CREATED)
async def upload_job_description(
    title: str,
    company: str = None,
    description: str,
    requirements: str = None,
    location: str = None,
    salary_range: str = None,
    current_user: User = Depends(get_current_user)
):
    """
    Create and process a job description

    Args:
        title: Job title
        company: Company name
        description: Job description text
        requirements: Job requirements
        location: Job location
        salary_range: Salary range
        current_user: Authenticated user

    Returns:
        Processed job description information
    """
    try:
        # Create document structure for processing
        from app.services.resume_matching.document_processing_service import ProcessedDocument
        full_text = f"{description}\n\n{requirements or ''}"

        # Process as job description
        processing_service = DocumentProcessingService()
        sections = processing_service._extract_job_sections(full_text)

        # Store in database
        from app.services.supabase.database import JobDescriptionService
        job_service = JobDescriptionService()

        job_data = {
            'user_id': current_user.id,
            'title': title,
            'company': company,
            'description': description,
            'requirements': requirements,
            'location': location,
            'salary_range': salary_range,
            'sections': sections,
            'metadata': {
                'character_count': len(full_text),
                'word_count': len(full_text.split()),
                'processing_timestamp': datetime.utcnow().isoformat()
            }
        }

        job = await job_service.create(job_data)

        # Generate and store embeddings
        from app.services.resume_matching.embedding_service import EmbeddingService
        embedding_service = EmbeddingService()

        # Create processed document for embedding generation
        processed_doc = ProcessedDocument(
            text_content=full_text,
            metadata=job_data['metadata'],
            quality_score=1.0,  # Job descriptions are user-provided
            sections=sections,
            contact_info={}
        )

        embeddings = await embedding_service.generate_document_embeddings(processed_doc)

        embedding_metadata = {
            'user_id': current_user.id,
            'job_id': job.id,
            'document_type': 'job_description'
        }

        await embedding_service.store_embeddings(job.id, embeddings, embedding_metadata)

        return {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "sections_found": list(sections.keys()),
            "processing_status": "completed"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job description processing failed: {str(e)}"
        )

@router.get("/resumes", response_model=List[dict])
async def get_user_resumes(
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """Get user's uploaded resumes"""
    try:
        resume_service = ResumeService()
        resumes = await resume_service.get_by_user(
            current_user.id,
            filters={'limit': limit, 'offset': offset}
        )
        return [resume.dict() for resume in resumes]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve resumes: {str(e)}"
        )

@router.get("/job-descriptions", response_model=List[dict])
async def get_user_job_descriptions(
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """Get user's job descriptions"""
    try:
        from app.services.supabase.database import JobDescriptionService
        job_service = JobDescriptionService()
        jobs = await job_service.get_by_user(
            current_user.id,
            filters={'limit': limit, 'offset': offset}
        )
        return [job.dict() for job in jobs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job descriptions: {str(e)}"
        )
```


<!-- Context: backend/app/api/endpoints/documents.py > 2. Resume Matching Endpoints -->

#### 2. Resume Matching Endpoints

```python