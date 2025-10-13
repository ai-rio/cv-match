# Technical Integration Guide

**Project:** CV-Match Resume-Matcher Integration
**Document Version:** 1.0
**Last Updated:** October 12, 2025
**Target Audience:** Development Team, Technical Architects

## Executive Summary

This technical integration guide provides detailed specifications for implementing Resume-Matcher's AI-powered features into the CV-Match SaaS platform. The guide covers service architecture, code adaptation patterns, database schema changes, API specifications, and integration best practices.

**Integration Scope:**
- Document processing and parsing pipeline
- Vector similarity matching with Qdrant
- LLM-powered analysis and suggestions
- Advanced scoring algorithms
- Comprehensive API endpoints

**Technical Stack:**
- **Backend:** FastAPI with async/await patterns
- **Database:** Supabase PostgreSQL + Qdrant vector database
- **AI Services:** OpenAI GPT-4 + Embeddings API
- **Frontend:** Next.js 15+ with TypeScript

---

## Service Structure Recommendations

### Backend Architecture Overview

```
CV-Match Backend Integration
├── app/
│   ├── services/
│   │   ├── resume_matching/           # New: Resume matching services
│   │   │   ├── document_processing_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── similarity_service.py
│   │   │   ├── scoring_service.py
│   │   │   ├── llm_analysis_service.py
│   │   │   └── improvement_service.py
│   │   ├── vectordb/                   # New: Vector database services
│   │   │   ├── qdrant_service.py
│   │   │   ├── vector_operations.py
│   │   │   └── search_service.py
│   │   ├── supabase/                   # Existing: Enhanced with new models
│   │   ├── llm/                        # Existing: Enhanced with new capabilities
│   │   └── storage/                    # Existing: Enhanced for document storage
│   ├── models/                         # Enhanced: New Pydantic models
│   │   ├── resume.py
│   │   ├── job_description.py
│   │   ├── match_result.py
│   │   ├── embedding.py
│   │   └── suggestion.py
│   ├── api/                            # Enhanced: New API endpoints
│   │   ├── endpoints/
│   │   │   ├── resume_matching.py
│   │   │   ├── documents.py
│   │   │   ├── job_descriptions.py
│   │   │   └── suggestions.py
│   │   └── dependencies/
│   │       ├── auth.py
│   │       └── rate_limiting.py
│   └── core/                           # Enhanced: Configuration and utilities
│       ├── config.py
│       └── security.py
```

### Service Layer Implementation

#### 1. Document Processing Service

```python
# backend/app/services/resume_matching/document_processing_service.py

from typing import Optional, Dict, Any
from fastapi import UploadFile
import PyPDF2
from docx import Document
import io
import re
from dataclasses import dataclass

@dataclass
class ProcessedDocument:
    text_content: str
    metadata: Dict[str, Any]
    quality_score: float
    sections: Dict[str, str]
    contact_info: Dict[str, str]

class DocumentProcessingService:
    """Service for processing uploaded resumes and job descriptions"""

    def __init__(self):
        self.supported_formats = ['pdf', 'docx']
        self.max_file_size = 10 * 1024 * 1024  # 10MB

    async def process_document(self, file: UploadFile, document_type: str) -> ProcessedDocument:
        """
        Process uploaded document and extract structured content

        Args:
            file: Uploaded file object
            document_type: Type of document ('resume' or 'job_description')

        Returns:
            ProcessedDocument with extracted content and metadata

        Raises:
            ValueError: If file format not supported or processing fails
        """
        # Validate file
        await self._validate_file(file)

        # Read file content
        file_content = await file.read()

        # Extract text based on file type
        if file.filename.endswith('.pdf'):
            text_content = await self._extract_pdf_text(file_content)
        elif file.filename.endswith('.docx'):
            text_content = await self._extract_docx_text(file_content)
        else:
            raise ValueError(f"Unsupported file format: {file.filename}")

        # Clean and structure content
        cleaned_text = self._clean_text(text_content)
        sections = self._extract_sections(cleaned_text, document_type)
        metadata = self._extract_metadata(cleaned_text, file.filename)
        contact_info = self._extract_contact_info(cleaned_text)
        quality_score = self._calculate_quality_score(cleaned_text)

        return ProcessedDocument(
            text_content=cleaned_text,
            metadata=metadata,
            quality_score=quality_score,
            sections=sections,
            contact_info=contact_info
        )

    async def _validate_file(self, file: UploadFile):
        """Validate uploaded file"""
        if not file.filename:
            raise ValueError("No filename provided")

        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")

        # Note: File size validation should happen before this method
        # in the API endpoint using request.headers.get('content-length')

    async def _extract_pdf_text(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"

            return text_content
        except Exception as e:
            raise ValueError(f"PDF processing failed: {str(e)}")

    async def _extract_docx_text(self, file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            docx_file = io.BytesIO(file_content)
            doc = Document(docx_file)

            text_content = ""
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"

            return text_content
        except Exception as e:
            raise ValueError(f"DOCX processing failed: {str(e)}")

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', '', text)

        # Normalize line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)

        return text.strip()

    def _extract_sections(self, text: str, document_type: str) -> Dict[str, str]:
        """Extract document sections based on type"""
        if document_type == 'resume':
            return self._extract_resume_sections(text)
        else:
            return self._extract_job_sections(text)

    def _extract_resume_sections(self, text: str) -> Dict[str, str]:
        """Extract standard resume sections"""
        sections = {}

        # Define section patterns
        section_patterns = {
            'experience': r'(?:experience|work history|employment)(.*?)(?=education|skills|$)',
            'education': r'(?:education|academic|qualification)(.*?)(?=experience|skills|$)',
            'skills': r'(?:skills|competencies|technical)(.*?)(?=experience|education|$)',
            'summary': r'(?:summary|objective|profile)(.*?)(?=experience|education|skills|$)'
        }

        text_lower = text.lower()
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
            if match:
                sections[section_name] = match.group(1).strip()

        return sections

    def _extract_job_sections(self, text: str) -> Dict[str, str]:
        """Extract job description sections"""
        sections = {}

        section_patterns = {
            'requirements': r'(?:requirements|qualifications)(.*?)(?=responsibilities|benefits|$)',
            'responsibilities': r'(?:responsibilities|duties)(.*?)(?=requirements|benefits|$)',
            'benefits': r'(?:benefits|perks)(.*?)(?=requirements|responsibilities|$)',
            'company_info': r'(?:about|company)(.*?)(?=requirements|responsibilities|benefits|$)'
        }

        text_lower = text.lower()
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
            if match:
                sections[section_name] = match.group(1).strip()

        return sections

    def _extract_metadata(self, text: str, filename: str) -> Dict[str, Any]:
        """Extract document metadata"""
        return {
            'filename': filename,
            'character_count': len(text),
            'word_count': len(text.split()),
            'line_count': len(text.split('\n')),
            'language': self._detect_language(text),
            'processing_timestamp': datetime.utcnow().isoformat()
        }

    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from text"""
        contact_info = {}

        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group()

        # Phone pattern (Brazilian format)
        phone_pattern = r'(?:\+55\s?)?\(?\d{2}\)?[-\s]?\d{4,5}[-\s]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group()

        # LinkedIn pattern
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, text)
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group()

        return contact_info

    def _calculate_quality_score(self, text: str) -> float:
        """Calculate document quality score (0-100)"""
        score = 0.0

        # Base score for having content
        if len(text) > 100:
            score += 20

        # Word count scoring
        word_count = len(text.split())
        if word_count > 100:
            score += 20
        if word_count > 300:
            score += 20

        # Structure scoring (presence of sections)
        if any(section in text.lower() for section in ['experience', 'education', 'skills']):
            score += 20

        # Contact information scoring
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            score += 10

        # Language quality (basic check)
        if len(text.split()) > 50:
            score += 10

        return min(score, 100.0)

    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        # Common Portuguese words
        portuguese_words = ['é', 'de', 'a', 'o', 'que', 'do', 'em', 'um', 'para', 'é']

        words = text.lower().split()[:50]  # Check first 50 words
        portuguese_count = sum(1 for word in words if word in portuguese_words)

        if portuguese_count > len(words) * 0.1:  # 10% threshold
            return 'pt-br'
        else:
            return 'en'
```

#### 2. Embedding Service

```python
# backend/app/services/resume_matching/embedding_service.py

from typing import List, Dict, Any
import openai
import asyncio
import hashlib
import json
from app.core.config import settings
from app.services.vectordb.qdrant_service import QdrantService

class EmbeddingService:
    """Service for generating and managing text embeddings"""

    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.qdrant_service = QdrantService()
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimension = 1536

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for given text using OpenAI API

        Args:
            text: Text to generate embedding for

        Returns:
            List of float values representing the embedding

        Raises:
            Exception: If embedding generation fails
        """
        try:
            response = await self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Embedding generation failed: {str(e)}")

    async def generate_document_embeddings(self, document: ProcessedDocument) -> Dict[str, List[float]]:
        """
        Generate embeddings for different parts of a document

        Args:
            document: ProcessedDocument instance

        Returns:
            Dictionary with embeddings for different document parts
        """
        embeddings = {}

        # Full text embedding
        embeddings['full_text'] = await self.generate_embedding(document.text_content)

        # Section embeddings
        for section_name, section_text in document.sections.items():
            if section_text and len(section_text.strip()) > 50:
                embeddings[f'section_{section_name}'] = await self.generate_embedding(section_text)

        # Summary embedding (first 200 characters)
        summary = document.text_content[:200]
        embeddings['summary'] = await self.generate_embedding(summary)

        return embeddings

    async def store_embeddings(self, document_id: str, embeddings: Dict[str, List[float]],
                             metadata: Dict[str, Any]) -> bool:
        """
        Store embeddings in vector database

        Args:
            document_id: Unique document identifier
            embeddings: Dictionary of embeddings to store
            metadata: Additional metadata for the embeddings

        Returns:
            True if storage successful, False otherwise
        """
        try:
            for embedding_type, embedding_vector in embeddings.items():
                point_id = f"{document_id}_{embedding_type}"

                await self.qdrant_service.store_vector(
                    point_id=point_id,
                    vector=embedding_vector,
                    metadata={
                        **metadata,
                        'embedding_type': embedding_type,
                        'document_id': document_id
                    }
                )
            return True
        except Exception as e:
            print(f"Error storing embeddings: {str(e)}")
            return False

    async def find_similar_documents(self, query_embedding: List[float],
                                   limit: int = 10,
                                   filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Find similar documents based on embedding similarity

        Args:
            query_embedding: Embedding to search for
            limit: Maximum number of results to return
            filters: Optional filters for search

        Returns:
            List of similar documents with similarity scores
        """
        try:
            results = await self.qdrant_service.search_similar(
                query_vector=query_embedding,
                limit=limit,
                filters=filters
            )
            return results
        except Exception as e:
            raise Exception(f"Similarity search failed: {str(e)}")

    async def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Similarity score between 0 and 1
        """
        try:
            import numpy as np

            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            raise Exception(f"Similarity calculation failed: {str(e)}")
```

#### 3. Similarity Service

```python
# backend/app/services/resume_matching/similarity_service.py

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import numpy as np
from app.services.resume_matching.embedding_service import EmbeddingService

@dataclass
class SimilarityResult:
    overall_similarity: float
    section_similarities: Dict[str, float]
    keyword_similarity: float
    confidence_score: float

class SimilarityService:
    """Service for calculating document similarities"""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.weight_config = {
            'full_text': 0.4,
            'skills': 0.3,
            'experience': 0.2,
            'education': 0.1
        }

    async def calculate_document_similarity(self, resume_embeddings: Dict[str, List[float]],
                                          job_embeddings: Dict[str, List[float]]) -> SimilarityResult:
        """
        Calculate comprehensive similarity between resume and job description

        Args:
            resume_embeddings: Resume document embeddings
            job_embeddings: Job description embeddings

        Returns:
            SimilarityResult with detailed similarity scores
        """
        section_similarities = {}
        overall_similarity = 0.0
        total_weight = 0.0

        # Calculate similarities for each section type
        for section in self.weight_config.keys():
            resume_key = f"section_{section}" if section != 'full_text' else 'full_text'
            job_key = f"section_{section}" if section != 'full_text' else 'full_text'

            if resume_key in resume_embeddings and job_key in job_embeddings:
                similarity = await self.embedding_service.calculate_similarity(
                    resume_embeddings[resume_key],
                    job_embeddings[job_key]
                )
                section_similarities[section] = similarity
                overall_similarity += similarity * self.weight_config[section]
                total_weight += self.weight_config[section]

        # Normalize overall similarity
        if total_weight > 0:
            overall_similarity /= total_weight

        # Calculate keyword similarity
        keyword_similarity = await self._calculate_keyword_similarity(
            resume_embeddings, job_embeddings
        )

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            section_similarities, len(resume_embeddings), len(job_embeddings)
        )

        return SimilarityResult(
            overall_similarity=overall_similarity,
            section_similarities=section_similarities,
            keyword_similarity=keyword_similarity,
            confidence_score=confidence_score
        )

    async def _calculate_keyword_similarity(self, resume_embeddings: Dict[str, List[float]],
                                          job_embeddings: Dict[str, List[float]]) -> float:
        """Calculate keyword-based similarity"""
        # Extract keywords from summary embeddings as a proxy
        if 'summary' in resume_embeddings and 'summary' in job_embeddings:
            return await self.embedding_service.calculate_similarity(
                resume_embeddings['summary'],
                job_embeddings['summary']
            )
        return 0.0

    def _calculate_confidence_score(self, section_similarities: Dict[str, float],
                                  resume_sections: int, job_sections: int) -> float:
        """Calculate confidence score based on available data"""
        base_confidence = 0.5

        # Increase confidence based on number of matching sections
        section_count = len(section_similarities)
        section_confidence = min(section_count / 4.0, 0.3)  # Max 0.3 for sections

        # Adjust based on similarity distribution
        if section_similarities:
            similarities = list(section_similarities.values())
            variance = np.var(similarities)
            variance_penalty = min(variance * 0.5, 0.2)  # Max 0.2 penalty
        else:
            variance_penalty = 0.2

        confidence = base_confidence + section_confidence - variance_penalty
        return max(0.1, min(1.0, confidence))

    async def find_best_matches(self, resume_embeddings: Dict[str, List[float]],
                              job_embeddings_list: List[Dict[str, List[float]]],
                              limit: int = 5) -> List[Tuple[int, SimilarityResult]]:
        """
        Find best matching job descriptions for a resume

        Args:
            resume_embeddings: Resume document embeddings
            job_embeddings_list: List of job description embeddings
            limit: Maximum number of matches to return

        Returns:
            List of tuples (job_index, similarity_result) sorted by similarity
        """
        similarities = []

        for idx, job_embeddings in enumerate(job_embeddings_list):
            similarity = await self.calculate_document_similarity(
                resume_embeddings, job_embeddings
            )
            similarities.append((idx, similarity))

        # Sort by overall similarity (descending)
        similarities.sort(key=lambda x: x[1].overall_similarity, reverse=True)

        return similarities[:limit]
```

---

## Code Adaptation Guidelines

### Integration with Existing Services

#### 1. Supabase Service Extension

```python
# backend/app/services/supabase/database.py (Enhanced)

from typing import TypeVar, Generic, Dict, Any, List, Optional
from pydantic import BaseModel
from supabase import Client, create_client
from app.core.config import settings

T = TypeVar('T', bound=BaseModel)

class SupabaseDatabaseService(Generic[T]):
    """Enhanced database service with resume matching capabilities"""

    def __init__(self, table_name: str, model_class: Type[T]):
        self.table_name = table_name
        self.model_class = model_class
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )

    async def create(self, data: Dict[str, Any]) -> T:
        """Create new record with user association"""
        try:
            response = self.client.table(self.table_name).insert(data).execute()
            if response.data:
                return self.model_class(**response.data[0])
            raise Exception("No data returned from insert operation")
        except Exception as e:
            raise Exception(f"Create operation failed: {str(e)}")

    async def get_by_user(self, user_id: str, filters: Dict[str, Any] = None) -> List[T]:
        """Get records for specific user with optional filters"""
        try:
            query = self.client.table(self.table_name).select("*").eq("user_id", user_id)

            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            response = query.execute()
            return [self.model_class(**item) for item in response.data]
        except Exception as e:
            raise Exception(f"Get by user operation failed: {str(e)}")

    async def update(self, id: str, data: Dict[str, Any]) -> T:
        """Update existing record"""
        try:
            response = self.client.table(self.table_name).update(data).eq("id", id).execute()
            if response.data:
                return self.model_class(**response.data[0])
            raise Exception("No data returned from update operation")
        except Exception as e:
            raise Exception(f"Update operation failed: {str(e)}")

    async def delete(self, id: str) -> bool:
        """Delete record by ID"""
        try:
            response = self.client.table(self.table_name).delete().eq("id", id).execute()
            return len(response.data) > 0
        except Exception as e:
            raise Exception(f"Delete operation failed: {str(e)}")

    async def search(self, query: str, search_fields: List[str], user_id: str) -> List[T]:
        """Full-text search across specified fields"""
        try:
            # Build search query
            search_conditions = []
            for field in search_fields:
                search_conditions.append(f"{field}.ilike.%{query}%")

            # Combine search conditions with OR
            search_query = " , ".join(search_conditions)

            response = self.client.table(self.table_name).select("*") \
                .eq("user_id", user_id) \
                .or_(search_query) \
                .execute()

            return [self.model_class(**item) for item in response.data]
        except Exception as e:
            raise Exception(f"Search operation failed: {str(e)}")

# Specialized services for resume matching
class ResumeService(SupabaseDatabaseService):
    """Service for resume operations"""

    def __init__(self):
        super().__init__("resumes", ResumeModel)

    async def get_user_resumes_with_embeddings(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user resumes with their embeddings"""
        try:
            response = self.client.table("resumes") \
                .select("*, resume_embeddings(embedding_vector, chunk_text)") \
                .eq("user_id", user_id) \
                .execute()
            return response.data
        except Exception as e:
            raise Exception(f"Failed to get resumes with embeddings: {str(e)}")

class JobDescriptionService(SupabaseDatabaseService):
    """Service for job description operations"""

    def __init__(self):
        super().__init__("job_descriptions", JobDescriptionModel)

class MatchResultService(SupabaseDatabaseService):
    """Service for match result operations"""

    def __init__(self):
        super().__init__("match_results", MatchResultModel)

    async def get_user_match_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's match history with related data"""
        try:
            response = self.client.table("match_results") \
                .select("""
                    *,
                    resumes(title, original_filename),
                    job_descriptions(title, company)
                """) \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            return response.data
        except Exception as e:
            raise Exception(f"Failed to get match history: {str(e)}")
```

#### 2. LLM Service Enhancement

```python
# backend/app/services/llm/llm_service.py (Enhanced)

from typing import Dict, Any, List, Optional
import openai
from app.core.config import settings
from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    resume_text: str
    job_description_text: str
    analysis_type: str = "comprehensive"

class AnalysisResponse(BaseModel):
    skills_match: Dict[str, Any]
    experience_match: Dict[str, Any]
    suggestions: List[str]
    score_breakdown: Dict[str, float]
    overall_assessment: str

class LLMService:
    """Enhanced LLM service for resume analysis and improvements"""

    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4"
        self.max_tokens = 2000

    async def analyze_resume_job_match(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Analyze resume against job description using LLM

        Args:
            request: Analysis request with resume and job description

        Returns:
            AnalysisResponse with detailed analysis results
        """
        prompt = self._build_analysis_prompt(request.resume_text, request.job_description_text)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )

            analysis_text = response.choices[0].message.content
            return self._parse_analysis_response(analysis_text)

        except Exception as e:
            raise Exception(f"LLM analysis failed: {str(e)}")

    async def generate_improvement_suggestions(self, resume_text: str,
                                            job_description_text: str,
                                            match_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Generate specific improvement suggestions for resume

        Args:
            resume_text: Current resume text
            job_description_text: Target job description
            match_scores: Current match scores

        Returns:
            List of improvement suggestions with priorities
        """
        prompt = self._build_improvement_prompt(resume_text, job_description_text, match_scores)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_improvement_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.4
            )

            suggestions_text = response.choices[0].message.content
            return self._parse_suggestions_response(suggestions_text)

        except Exception as e:
            raise Exception(f"Suggestion generation failed: {str(e)}")

    async def optimize_resume_section(self, section_text: str,
                                    job_requirements: str,
                                    section_type: str) -> str:
        """
        Optimize specific resume section for job requirements

        Args:
            section_text: Current section text
            job_requirements: Relevant job requirements
            section_type: Type of section (experience, skills, etc.)

        Returns:
            Optimized section text
        """
        prompt = self._build_optimization_prompt(section_text, job_requirements, section_type)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_optimization_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise Exception(f"Section optimization failed: {str(e)}")

    def _get_system_prompt(self) -> str:
        """System prompt for resume analysis"""
        return """
        You are an expert career coach and resume analyst with deep knowledge of recruitment processes
        across various industries. Your task is to analyze resumes against job descriptions and provide
        detailed, actionable insights.

        Focus on:
        1. Skills alignment and gaps
        2. Experience relevance and transferability
        3. Education and qualification matches
        4. Keyword optimization for ATS systems
        5. Overall compatibility assessment

        Provide specific, constructive feedback with concrete examples.
        """

    def _get_improvement_system_prompt(self) -> str:
        """System prompt for improvement suggestions"""
        return """
        You are a professional resume writer specializing in optimizing resumes for specific job applications.
        Your suggestions should be practical, specific, and focused on improving the candidate's chances
        of getting interviews.

        For each suggestion, provide:
        1. Specific text to add or modify
        2. Reasoning behind the suggestion
        3. Priority level (High/Medium/Low)
        4. Expected impact on match score

        Focus on suggestions that will provide the highest ROI for the candidate's time.
        """

    def _get_optimization_system_prompt(self) -> str:
        """System prompt for section optimization"""
        return """
        You are optimizing a resume section to better match job requirements while maintaining
        authenticity and professional tone. Enhance the content to highlight relevant skills
        and experiences, but do not invent false information.

        Maintain the original intent and truthfulness while improving:
        1. Keyword alignment
        2. Impact and achievement focus
        3. Professional formatting
        4. ATS compatibility
        """

    def _build_analysis_prompt(self, resume_text: str, job_description_text: str) -> str:
        """Build comprehensive analysis prompt"""
        return f"""
        Please analyze the following resume against the job description:

        JOB DESCRIPTION:
        {job_description_text}

        RESUME:
        {resume_text}

        Please provide a detailed analysis covering:
        1. Skills Match: Which skills align well and what gaps exist
        2. Experience Relevance: How well the experience matches requirements
        3. Education Alignment: Educational qualifications vs requirements
        4. ATS Optimization: Keyword presence and formatting
        5. Overall Assessment: Summary of match quality

        Format your response as structured JSON with clear sections and specific examples.
        """

    def _build_improvement_prompt(self, resume_text: str, job_description_text: str,
                                match_scores: Dict[str, float]) -> str:
        """Build improvement suggestions prompt"""
        return f"""
        Based on the following resume, job description, and match scores, provide specific
        improvement suggestions to increase the candidate's chances of success:

        CURRENT MATCH SCORES:
        {match_scores}

        JOB DESCRIPTION:
        {job_description_text}

        CURRENT RESUME:
        {resume_text}

        Provide 5-7 specific, actionable suggestions that will significantly improve the match.
        Focus on high-impact changes that the candidate can realistically implement.
        """

    def _build_optimization_prompt(self, section_text: str, job_requirements: str,
                                 section_type: str) -> str:
        """Build section optimization prompt"""
        return f"""
        Optimize the following {section_type} section to better align with the job requirements:

        JOB REQUIREMENTS:
        {job_requirements}

        CURRENT {section_type.upper()} SECTION:
        {section_text}

        Please rewrite this section to:
        1. Include relevant keywords from the job requirements
        2. Highlight achievements and impact
        3. Maintain professional tone and authenticity
        4. Optimize for ATS systems

        Keep the content truthful while making it more compelling and relevant.
        """

    def _parse_analysis_response(self, analysis_text: str) -> AnalysisResponse:
        """Parse LLM analysis response into structured format"""
        # This is a simplified parser - in production, you'd want more robust parsing
        import json
        import re

        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return AnalysisResponse(**data)
        except:
            pass

        # Fallback parsing if JSON extraction fails
        return AnalysisResponse(
            skills_match={"status": "parsed", "details": "Analysis completed"},
            experience_match={"status": "parsed", "details": "Analysis completed"},
            suggestions=["Review complete analysis in LLM response"],
            score_breakdown={"overall": 0.75},
            overall_assessment=analysis_text[:500] + "..."
        )

    def _parse_suggestions_response(self, suggestions_text: str) -> List[Dict[str, Any]]:
        """Parse LLM suggestions into structured format"""
        # Simplified parsing - enhance with regex patterns for production
        suggestions = []

        lines = suggestions_text.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('#'):
                suggestions.append({
                    "text": line.strip(),
                    "priority": "Medium",
                    "category": "General",
                    "impact": "Moderate"
                })

        return suggestions[:10]  # Limit to 10 suggestions
```

---

## Database Schema Changes

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

## API Endpoint Specifications

### Resume Matching API Endpoints

#### 1. Document Upload and Processing

```python
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

#### 2. Resume Matching Endpoints

```python
# backend/app/api/endpoints/resume_matching.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel
from app.services.resume_matching.similarity_service import SimilarityService
from app.services.resume_matching.llm_service import LLMService
from app.services.supabase.database import ResumeService, JobDescriptionService, MatchResultService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/matching", tags=["resume-matching"])

class MatchRequest(BaseModel):
    resume_id: str
    job_id: str
    include_suggestions: bool = True

class MatchResponse(BaseModel):
    match_id: str
    overall_score: float
    confidence_score: float
    detailed_scores: dict
    analysis: dict
    suggestions: List[dict] = []

@router.post("/analyze", response_model=MatchResponse)
async def analyze_match(
    request: MatchRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze match between resume and job description

    Args:
        request: Match request with resume and job IDs
        background_tasks: FastAPI background tasks
        current_user: Authenticated user

    Returns:
        Detailed match analysis results
    """
    try:
        # Validate ownership
        resume_service = ResumeService()
        job_service = JobDescriptionService()

        resume = await resume_service.get_by_id(request.resume_id)
        job = await job_service.get_by_id(request.job_id)

        if not resume or resume.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found or access denied"
            )

        if not job or job.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found or access denied"
            )

        # Check if match already exists
        match_service = MatchResultService()
        existing_matches = await match_service.get_by_user(
            current_user.id,
            filters={'resume_id': request.resume_id, 'job_id': request.job_id}
        )

        if existing_matches:
            existing_match = existing_matches[0]
            return MatchResponse(
                match_id=existing_match.id,
                overall_score=existing_match.overall_score,
                confidence_score=existing_match.confidence_score,
                detailed_scores={
                    'skills': existing_match.skills_score,
                    'experience': existing_match.experience_score,
                    'education': existing_match.education_score,
                    'keywords': existing_match.keyword_score
                },
                analysis=existing_match.match_analysis
            )

        # Get embeddings
        from app.services.resume_matching.embedding_service import EmbeddingService
        embedding_service = EmbeddingService()

        resume_embeddings = await embedding_service.get_document_embeddings(request.resume_id)
        job_embeddings = await embedding_service.get_document_embeddings(request.job_id)

        if not resume_embeddings or not job_embeddings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Embeddings not found for documents"
            )

        # Calculate similarity
        similarity_service = SimilarityService()
        similarity_result = await similarity_service.calculate_document_similarity(
            resume_embeddings, job_embeddings
        )

        # Perform LLM analysis
        llm_service = LLMService()
        llm_analysis = await llm_service.analyze_resume_job_match(
            resume.content_text,
            job.description
        )

        # Create match result
        match_data = {
            'user_id': current_user.id,
            'resume_id': request.resume_id,
            'job_id': request.job_id,
            'overall_score': similarity_result.overall_similarity * 100,
            'confidence_score': similarity_result.confidence_score * 100,
            'skills_score': similarity_result.section_similarities.get('skills', 0) * 100,
            'experience_score': similarity_result.section_similarities.get('experience', 0) * 100,
            'education_score': similarity_result.section_similarities.get('education', 0) * 100,
            'keyword_score': similarity_result.keyword_similarity * 100,
            'section_scores': {k: v * 100 for k, v in similarity_result.section_similarities.items()},
            'match_analysis': llm_analysis.dict(),
            'skill_gaps': llm_analysis.skills_match.get('gaps', []),
            'strengths': llm_analysis.skills_match.get('strengths', [])
        }

        match_result = await match_service.create(match_data)

        # Generate suggestions in background
        if request.include_suggestions:
            background_tasks.add_task(
                generate_improvement_suggestions,
                match_result.id,
                resume.content_text,
                job.description,
                similarity_result.overall_similarity
            )

        return MatchResponse(
            match_id=match_result.id,
            overall_score=match_result.overall_score,
            confidence_score=match_result.confidence_score,
            detailed_scores={
                'skills': match_result.skills_score,
                'experience': match_result.experience_score,
                'education': match_result.education_score,
                'keywords': match_result.keyword_score
            },
            analysis=match_result.match_analysis
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Match analysis failed: {str(e)}"
        )

async def generate_improvement_suggestions(
    match_result_id: str,
    resume_text: str,
    job_description_text: str,
    similarity_score: float
):
    """Generate improvement suggestions in background"""
    try:
        llm_service = LLMService()

        # Generate suggestions
        match_scores = {'overall': similarity_score}
        suggestions = await llm_service.generate_improvement_suggestions(
            resume_text, job_description_text, match_scores
        )

        # Store suggestions in database
        from app.services.supabase.database import SupabaseDatabaseService
        suggestion_service = SupabaseDatabaseService("ai_suggestions", dict)

        for suggestion in suggestions:
            suggestion_data = {
                'match_result_id': match_result_id,
                'suggestion_type': suggestion.get('type', 'general'),
                'category': suggestion.get('category', 'medium_impact'),
                'title': suggestion.get('title', 'Improvement Suggestion'),
                'description': suggestion.get('text', ''),
                'priority': suggestion.get('priority', 3),
                'impact_score': suggestion.get('impact', 5.0),
                'effort_estimate': suggestion.get('effort', 'medium'),
                'ai_confidence': suggestion.get('confidence', 0.7)
            }

            await suggestion_service.create(suggestion_data)

    except Exception as e:
        # Log error but don't fail the main request
        print(f"Failed to generate suggestions: {str(e)}")

@router.get("/matches", response_model=List[dict])
async def get_match_history(
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """Get user's match history"""
    try:
        match_service = MatchResultService()
        matches = await match_service.get_user_match_history(
            current_user.id, limit=limit, offset=offset
        )
        return matches
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve match history: {str(e)}"
        )

@router.get("/matches/{match_id}/suggestions", response_model=List[dict])
async def get_match_suggestions(
    match_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get suggestions for a specific match"""
    try:
        from app.services.supabase.database import SupabaseDatabaseService
        suggestion_service = SupabaseDatabaseService("ai_suggestions", dict)

        suggestions = await suggestion_service.get_by_user(
            current_user.id,
            filters={'match_result_id': match_id}
        )

        # Sort by priority
        suggestions.sort(key=lambda x: x.get('priority', 5))

        return suggestions

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve suggestions: {str(e)}"
        )

@router.put("/suggestions/{suggestion_id}/status")
async def update_suggestion_status(
    suggestion_id: str,
    status: str,  # 'implemented', 'rejected'
    current_user: User = Depends(get_current_user)
):
    """Update suggestion implementation status"""
    try:
        from app.services.supabase.database import SupabaseDatabaseService
        suggestion_service = SupabaseDatabaseService("ai_suggestions", dict)

        # Validate ownership
        suggestions = await suggestion_service.get_by_user(
            current_user.id,
            filters={'id': suggestion_id}
        )

        if not suggestions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found or access denied"
            )

        # Update status
        update_data = {
            'status': status,
            'implemented_at': datetime.utcnow().isoformat() if status == 'implemented' else None
        }

        updated_suggestion = await suggestion_service.update(suggestion_id, update_data)

        return {"status": "updated", "suggestion": updated_suggestion}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update suggestion status: {str(e)}"
        )
```

---

## File Structure Organization

### Frontend Component Structure

```typescript
// frontend/app/components/resume-matching/
├── ResumeUpload.tsx              // Enhanced file upload component
├── JobDescriptionInput.tsx       // Job description form
├── MatchResults.tsx             // Results display and visualization
├── SuggestionsPanel.tsx         // AI improvement suggestions
├── ScoreVisualization.tsx       // Score charts and graphs
├── DocumentPreview.tsx          // Document preview component
├── MatchingHistory.tsx          // User's match history
├── FeedbackForm.tsx             // User feedback collection
└── index.ts                     // Component exports

// frontend/app/hooks/
├── useResumeMatching.ts         // Main matching logic hook
├── useDocumentUpload.ts         // File upload handling
├── useSuggestions.ts            // Suggestions management
└── useMatchingHistory.ts        // History management

// frontend/app/types/
├── resume.ts                    // Resume-related types
├── job-description.ts           // Job description types
├── match-result.ts              // Match result types
└── suggestion.ts                // Suggestion types
```

### Component Implementation Example

```typescript
// frontend/app/components/resume-matching/ResumeUpload.tsx

'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { uploadResume } from '@/app/api/resume-matching'
import { ProgressBar } from '@/app/components/ui/ProgressBar'
import { Alert, AlertDescription } from '@/app/components/ui/Alert'

interface ResumeUploadProps {
  onUploadSuccess: (resumeId: string) => void
  onError: (error: string) => void
}

export function ResumeUpload({ onUploadSuccess, onError }: ResumeUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowedTypes.includes(file.type)) {
      onError('Apenas arquivos PDF e DOCX são permitidos')
      return
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      onError('O arquivo deve ter menos de 10MB')
      return
    }

    setUploadedFile(file)
    await handleUpload(file)
  }, [onError])

  const handleUpload = async (file: File) => {
    setUploading(true)
    setUploadProgress(0)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('title', file.name.replace(/\.[^/.]+$/, ''))

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return prev
          }
          return prev + 10
        })
      }, 200)

      const result = await uploadResume(formData)

      clearInterval(progressInterval)
      setUploadProgress(100)

      setTimeout(() => {
        onUploadSuccess(result.id)
        setUploading(false)
        setUploadProgress(0)
      }, 500)

    } catch (error) {
      setUploading(false)
      setUploadProgress(0)
      onError(error instanceof Error ? error.message : 'Falha no upload')
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1,
    disabled: uploading
  })

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${uploading ? 'pointer-events-none opacity-50' : ''}
        `}
      >
        <input {...getInputProps()} />

        {uploading ? (
          <div className="space-y-4">
            <div className="text-lg font-medium">Processando currículo...</div>
            <ProgressBar progress={uploadProgress} />
            <p className="text-sm text-gray-600">
              Isso pode levar alguns segundos. Estamos analisando seu currículo.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-lg font-medium">
              {isDragActive ? 'Solte o arquivo aqui' : 'Arraste seu currículo ou clique para selecionar'}
            </div>
            <p className="text-sm text-gray-600">
              PDF ou DOCX (máximo 10MB)
            </p>
            {uploadedFile && !uploading && (
              <Alert>
                <AlertDescription>
                  Arquivo selecionado: {uploadedFile.name}
                </AlertDescription>
              </Alert>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// API function
// frontend/app/api/resume-matching.ts

export async function uploadResume(formData: FormData) {
  try {
    const response = await fetch('/api/documents/upload/resume', {
      method: 'POST',
      body: formData,
      credentials: 'include'
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Falha no upload')
    }

    return await response.json()
  } catch (error) {
    throw error
  }
}
```

---

## Integration Patterns and Best Practices

### 1. Error Handling Patterns

```python
# backend/app/core/exceptions.py

from fastapi import HTTPException, status

class ResumeMatchingException(Exception):
    """Base exception for resume matching operations"""
    pass

class DocumentProcessingError(ResumeMatchingException):
    """Raised when document processing fails"""
    pass

class EmbeddingGenerationError(ResumeMatchingException):
    """Raised when embedding generation fails"""
    pass

class LLMServiceError(ResumeMatchingException):
    """Raised when LLM service operations fail"""
    pass

class VectorDatabaseError(ResumeMatchingException):
    """Raised when vector database operations fail"""
    pass

# Exception handler
# backend/app/api/exception_handlers.py

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.exceptions import ResumeMatchingException

async def resume_matching_exception_handler(request: Request, exc: ResumeMatchingException):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Resume matching operation failed",
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )

# Register exception handlers in main app
# backend/app/main.py

from fastapi import FastAPI
from app.core.exceptions import ResumeMatchingException
from app.api.exception_handlers import resume_matching_exception_handler

app = FastAPI()
app.add_exception_handler(ResumeMatchingException, resume_matching_exception_handler)
```

### 2. Caching Strategies

```python
# backend/app/services/cache_service.py

import redis
import json
import hashlib
from typing import Any, Optional
from app.core.config import settings

class CacheService:
    """Redis-based caching service"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL"""
        try:
            self.redis_client.setex(key, ttl, json.dumps(value))
        except Exception:
            pass  # Cache failures should not break the application

    async def delete(self, key: str):
        """Delete value from cache"""
        try:
            self.redis_client.delete(key)
        except Exception:
            pass

    def generate_cache_key(self, prefix: str, *args) -> str:
        """Generate cache key from arguments"""
        key_data = ":".join(str(arg) for arg in args)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

# Usage in services
class EmbeddingService:
    def __init__(self):
        self.cache_service = CacheService()

    async def generate_embedding(self, text: str) -> List[float]:
        # Check cache first
        cache_key = self.cache_service.generate_cache_key("embedding", text)
        cached_embedding = await self.cache_service.get(cache_key)

        if cached_embedding:
            return cached_embedding

        # Generate new embedding
        embedding = await self._generate_embedding_from_api(text)

        # Cache for 24 hours
        await self.cache_service.set(cache_key, embedding, ttl=86400)

        return embedding
```

### 3. Rate Limiting

```python
# backend/app/api/dependencies/rate_limiting.py

from fastapi import HTTPException, status, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis

limiter = Limiter(key_func=get_remote_address)

class RateLimiter:
    """Custom rate limiting for resume matching operations"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )

    async def check_rate_limit(self, user_id: str, operation: str, limit: int, window: int):
        """
        Check if user exceeds rate limit for specific operation

        Args:
            user_id: User identifier
            operation: Operation type (e.g., 'match_analysis', 'suggestions')
            limit: Number of allowed operations
            window: Time window in seconds
        """
        key = f"rate_limit:{user_id}:{operation}"
        current = self.redis_client.incr(key)

        if current == 1:
            self.redis_client.expire(key, window)

        if current > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded for {operation}. Try again later."
            )

# Usage in endpoints
@router.post("/analyze")
@limiter.limit("10/minute")  # General rate limit
async def analyze_match(
    request: Request,
    match_request: MatchRequest,
    current_user: User = Depends(get_current_user)
):
    # Custom rate limit for premium users
    rate_limiter = RateLimiter()

    if current_user.subscription_tier == 'free':
        await rate_limiter.check_rate_limit(current_user.id, 'match_analysis', 5, 3600)  # 5 per hour
    else:
        await rate_limiter.check_rate_limit(current_user.id, 'match_analysis', 50, 3600)  # 50 per hour

    # ... rest of the function
```

### 4. Background Job Processing

```python
# backend/app/services/background_jobs.py

from celery import Celery
from app.services.resume_matching.llm_service import LLMService
from app.core.config import settings

celery_app = Celery(
    "cv_match",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

@celery_app.task(bind=True, max_retries=3)
def generate_suggestions_task(self, match_result_id: str, resume_text: str,
                            job_description_text: str, similarity_score: float):
    """Background task for generating improvement suggestions"""
    try:
        llm_service = LLMService()

        match_scores = {'overall': similarity_score}
        suggestions = await llm_service.generate_improvement_suggestions(
            resume_text, job_description_text, match_scores
        )

        # Store suggestions
        from app.services.supabase.database import SupabaseDatabaseService
        suggestion_service = SupabaseDatabaseService("ai_suggestions", dict)

        for suggestion in suggestions:
            suggestion_data = {
                'match_result_id': match_result_id,
                'suggestion_type': suggestion.get('type', 'general'),
                'category': suggestion.get('category', 'medium_impact'),
                'title': suggestion.get('title', 'Improvement Suggestion'),
                'description': suggestion.get('text', ''),
                'priority': suggestion.get('priority', 3),
                'impact_score': suggestion.get('impact', 5.0),
                'effort_estimate': suggestion.get('effort', 'medium'),
                'ai_confidence': suggestion.get('confidence', 0.7)
            }

            await suggestion_service.create(suggestion_data)

    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

---

## Testing Strategies

### Unit Testing Examples

```python
# tests/test_document_processing.py

import pytest
from app.services.resume_matching.document_processing_service import DocumentProcessingService
from unittest.mock import Mock, patch
import io

class TestDocumentProcessingService:

    @pytest.fixture
    def service(self):
        return DocumentProcessingService()

    @pytest.fixture
    def sample_pdf_content(self):
        # Create a simple PDF for testing
        return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n..."

    @pytest.mark.asyncio
    async def test_process_pdf_document(self, service, sample_pdf_content):
        """Test PDF document processing"""

        # Mock file object
        mock_file = Mock()
        mock_file.filename = "test_resume.pdf"
        mock_file.read.return_value = sample_pdf_content

        # Mock PDF parsing
        with patch('PyPDF2.PdfReader') as mock_pdf_reader:
            mock_page = Mock()
            mock_page.extract_text.return_value = "John Doe\nSoftware Engineer\nExperience: 5 years"

            mock_reader = Mock()
            mock_reader.pages = [mock_page]
            mock_pdf_reader.return_value = mock_reader

            result = await service.process_document(mock_file, 'resume')

            assert result.text_content == "John Doe Software Engineer Experience: 5 years"
            assert result.quality_score > 0
            assert 'experience' in result.sections

    @pytest.mark.asyncio
    async def test_invalid_file_format(self, service):
        """Test handling of invalid file formats"""

        mock_file = Mock()
        mock_file.filename = "test.txt"

        with pytest.raises(ValueError, match="Unsupported file format"):
            await service.process_document(mock_file, 'resume')

    def test_clean_text(self, service):
        """Test text cleaning functionality"""

        dirty_text = "John   Doe\n\n\nSoftware    Engineer!!@@#"
        clean_text = service._clean_text(dirty_text)

        assert "  " not in clean_text  # No double spaces
        assert clean_text == "John Doe Software Engineer"

    def test_extract_contact_info(self, service):
        """Test contact information extraction"""

        text = """
        John Doe
        Email: john.doe@example.com
        Phone: (11) 98765-4321
        LinkedIn: linkedin.com/in/johndoe
        """

        contact_info = service._extract_contact_info(text)

        assert contact_info['email'] == 'john.doe@example.com'
        assert contact_info['phone'] == '(11) 98765-4321'
        assert contact_info['linkedin'] == 'linkedin.com/in/johndoe'

# tests/test_similarity_service.py

import pytest
from app.services.resume_matching.similarity_service import SimilarityService
from unittest.mock import AsyncMock

class TestSimilarityService:

    @pytest.fixture
    def service(self):
        return SimilarityService()

    @pytest.mark.asyncio
    async def test_calculate_document_similarity(self, service):
        """Test document similarity calculation"""

        # Mock embeddings
        resume_embeddings = {
            'full_text': [0.1, 0.2, 0.3],
            'section_skills': [0.4, 0.5, 0.6],
            'section_experience': [0.7, 0.8, 0.9]
        }

        job_embeddings = {
            'full_text': [0.1, 0.2, 0.4],
            'section_skills': [0.4, 0.5, 0.7],
            'section_experience': [0.7, 0.8, 0.8]
        }

        # Mock embedding service
        service.embedding_service = AsyncMock()
        service.embedding_service.calculate_similarity.return_value = 0.85

        result = await service.calculate_document_similarity(resume_embeddings, job_embeddings)

        assert result.overall_similarity > 0
        assert result.confidence_score > 0
        assert 'skills' in result.section_similarities
        assert 'experience' in result.section_similarities

# tests/test_api_endpoints.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import Mock, patch

client = TestClient(app)

class TestResumeMatchingAPI:

    def test_upload_resume_success(self):
        """Test successful resume upload"""

        mock_file = b"PDF content"

        with patch('app.services.resume_matching.document_processing_service.DocumentProcessingService') as mock_service:
            mock_processor = Mock()
            mock_processor.process_document.return_value = Mock(
                text_content="Resume content",
                quality_score=85.0,
                sections={'experience': '5 years experience'},
                contact_info={'email': 'test@example.com'}
            )
            mock_service.return_value = mock_processor

            response = client.post(
                "/api/documents/upload/resume",
                files={"file": ("test.pdf", mock_file, "application/pdf")},
                data={"title": "Test Resume"}
            )

            assert response.status_code == 201
            data = response.json()
            assert data['quality_score'] == 85.0
            assert 'experience' in data['sections_found']

    def test_upload_resume_invalid_file(self):
        """Test upload with invalid file"""

        response = client.post(
            "/api/documents/upload/resume",
            files={"file": ("test.txt", b"content", "text/plain")}
        )

        assert response.status_code == 413  # Unsupported file type
```

### Integration Testing

```python
# tests/test_integration.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.supabase.database import ResumeService, JobDescriptionService

client = TestClient(app)

class TestResumeMatchingIntegration:

    @pytest.mark.asyncio
    async def test_end_to_end_matching_flow(self):
        """Test complete resume matching flow"""

        # 1. Upload resume
        resume_response = client.post(
            "/api/documents/upload/resume",
            files={"file": ("resume.pdf", b"PDF resume content", "application/pdf")},
            data={"title": "Software Engineer Resume"}
        )

        assert resume_response.status_code == 201
        resume_id = resume_response.json()['id']

        # 2. Create job description
        job_response = client.post(
            "/api/documents/upload/job-description",
            data={
                "title": "Senior Software Engineer",
                "company": "Tech Company",
                "description": "We are looking for a senior software engineer with Python experience...",
                "requirements": "5+ years Python experience, React, AWS"
            }
        )

        assert job_response.status_code == 201
        job_id = job_response.json()['id']

        # 3. Analyze match
        match_response = client.post(
            "/api/matching/analyze",
            json={
                "resume_id": resume_id,
                "job_id": job_id,
                "include_suggestions": True
            }
        )

        assert match_response.status_code == 200
        match_data = match_response.json()

        assert 'overall_score' in match_data
        assert 'detailed_scores' in match_data
        assert 'analysis' in match_data
        assert match_data['overall_score'] >= 0
        assert match_data['overall_score'] <= 100

        # 4. Get suggestions (should be generated in background)
        suggestions_response = client.get(
            f"/api/matching/matches/{match_data['match_id']}/suggestions"
        )

        assert suggestions_response.status_code == 200
        suggestions = suggestions_response.json()
        assert isinstance(suggestions, list)

        # 5. Get match history
        history_response = client.get("/api/matching/matches")

        assert history_response.status_code == 200
        history = history_response.json()
        assert len(history) >= 1
        assert history[0]['id'] == match_data['match_id']
```

---

## Performance Optimization Guidelines

### 1. Database Optimization

```sql
-- Create materialized views for frequently accessed data
CREATE MATERIALIZED VIEW user_match_stats AS
SELECT
    user_id,
    COUNT(*) as total_matches,
    AVG(overall_score) as avg_score,
    MAX(overall_score) as best_score,
    MIN(created_at) as first_match,
    MAX(created_at) as last_match
FROM match_results
GROUP BY user_id;

-- Create indexes for common query patterns
CREATE INDEX idx_match_results_user_score ON match_results(user_id, overall_score DESC);
CREATE INDEX idx_ai_suggestions_match_priority ON ai_suggestions(match_result_id, priority);

-- Partition large tables by date
CREATE TABLE match_results_y2024m01 PARTITION OF match_results
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### 2. Caching Strategy

```python
# backend/app/services/cache_service.py (Enhanced)

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )
        self.default_ttl = 3600  # 1 hour

    async def get_user_resume_cache(self, user_id: str) -> dict:
        """Get cached resume data for user"""
        key = f"user_resumes:{user_id}"
        return await self.get(key)

    async def set_user_resume_cache(self, user_id: str, resumes: list, ttl: int = None):
        """Cache user's resumes"""
        key = f"user_resumes:{user_id}"
        await self.set(key, resumes, ttl or self.default_ttl)

    async def invalidate_user_cache(self, user_id: str):
        """Invalidate all cache entries for user"""
        pattern = f"*:{user_id}*"
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)
```

### 3. API Response Optimization

```python
# backend/app/api/responses.py

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.services.cache_service import CacheService

router = APIRouter()

@router.get("/matches", response_model=List[dict])
async def get_match_history(
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """Get user's match history with caching"""

    cache_service = CacheService()

    # Check cache first
    cache_key = f"match_history:{current_user.id}:{limit}:{offset}"
    cached_result = await cache_service.get(cache_key)

    if cached_result:
        return JSONResponse(
            content=cached_result,
            headers={"X-Cache": "HIT"}
        )

    # Get from database
    match_service = MatchResultService()
    matches = await match_service.get_user_match_history(
        current_user.id, limit=limit, offset=offset
    )

    # Cache for 5 minutes
    await cache_service.set(cache_key, matches, ttl=300)

    return JSONResponse(
        content=matches,
        headers={"X-Cache": "MISS"}
    )
```

---

This technical integration guide provides comprehensive specifications for implementing Resume-Matcher features into the CV-Match platform. The guide covers all aspects from service architecture to testing strategies, ensuring a successful integration with minimal disruption to existing functionality.

**Key Implementation Points:**
- Follow the existing service layer patterns
- Implement comprehensive error handling
- Use caching strategies for performance optimization
- Maintain backward compatibility with existing features
- Implement proper rate limiting and usage tracking
- Create thorough test coverage for all new functionality

The integration builds upon CV-Match's strong foundation while adding sophisticated AI capabilities that will significantly enhance the platform's value proposition.