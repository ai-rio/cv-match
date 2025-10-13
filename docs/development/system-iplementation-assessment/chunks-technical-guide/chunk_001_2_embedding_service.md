---
chunk: 1
total_chunks: 7
title: 2. Embedding Service
context: backend/app/services/resume_matching/document_processing_service.py > 2. Embedding Service
estimated_tokens: 3024
source: technical-integration-guide.md
---

<!-- Context: Technical Integration Guide -->

# Technical Integration Guide

**Project:** CV-Match Resume-Matcher Integration
**Document Version:** 1.0
**Last Updated:** October 12, 2025
**Target Audience:** Development Team, Technical Architects


<!-- Context: Technical Integration Guide > Executive Summary -->

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


<!-- Context: Technical Integration Guide > Service Structure Recommendations -->

## Service Structure Recommendations


<!-- Context: Technical Integration Guide > Service Structure Recommendations > Backend Architecture Overview -->

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


<!-- Context: Technical Integration Guide > Service Structure Recommendations > Service Layer Implementation -->

### Service Layer Implementation


<!-- Context: Technical Integration Guide > Service Structure Recommendations > Service Layer Implementation > 1. Document Processing Service -->

#### 1. Document Processing Service

```python

<!-- Context: backend/app/services/resume_matching/document_processing_service.py -->

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


<!-- Context: backend/app/services/resume_matching/document_processing_service.py > 2. Embedding Service -->

#### 2. Embedding Service

```python