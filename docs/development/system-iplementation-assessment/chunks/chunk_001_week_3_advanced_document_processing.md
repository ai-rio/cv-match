---
chunk: 1
total_chunks: 4
title: Week 3: Advanced Document Processing
context: Implementation Roadmap > Phase 1: Core AI Foundation (Weeks 2-7) > Week-by-Week Breakdown > Week 3: Advanced Document Processing
estimated_tokens: 3884
source: implementation-roadmap.md
---

<!-- Context: Implementation Roadmap -->

# Implementation Roadmap

**Project:** CV-Match Resume-Matcher Integration
**Roadmap Period:** October 2025 - January 2026
**Total Duration:** 14-15 weeks (REVISED due to critical security fixes)
**Project Manager:** TBD
**Technical Lead:** TBD


<!-- Context: Implementation Roadmap > Executive Summary -->

## Executive Summary

This roadmap outlines a comprehensive 4-phase implementation plan for integrating Resume-Matcher's AI-powered features into the CV-Match SaaS platform. Following an independent security verification that identified critical vulnerabilities, the plan now includes a mandatory **Phase 0: Emergency Security Fixes** that must be completed before any other work.

**🚨 CRITICAL UPDATE:** The independent security verification revealed 8 critical security vulnerabilities that make the current system **ILLEGAL to deploy in Brazil** under LGPD regulations. These must be fixed first.

**Key Milestones:**
- **Phase 0 (Weeks 0-1):** Emergency Security Fixes - **MUST COMPLETE FIRST**
- **Phase 1 (Weeks 2-7):** Core AI Foundation - Document processing and vector similarity
- **Phase 2 (Weeks 8-11):** Enhanced Features - LLM integration and advanced scoring
- **Phase 3 (Weeks 12-14):** UI/UX Integration - Complete user interface and testing

**Success Metrics:**
- Phase 0 security fixes completed and verified
- On-time delivery of all subsequent phases
- 90%+ test coverage achieved
- Performance benchmarks met (<3s processing time)
- User acceptance testing passed with >85% satisfaction

---


<!-- Context: Implementation Roadmap > Phase 0: Emergency Security Fixes (Weeks 0-1) -->

## Phase 0: Emergency Security Fixes (Weeks 0-1)


<!-- Context: Implementation Roadmap > Phase 0: Emergency Security Fixes (Weeks 0-1) > Objective -->

### Objective
**CRITICAL:** Address all security vulnerabilities identified in the independent verification. This phase **BLOCKS ALL OTHER WORK** and must be completed before any additional features can be implemented.


<!-- Context: Implementation Roadmap > Phase 0: Emergency Security Fixes (Weeks 0-1) > Duration: 1-2 weeks -->

### Duration: 1-2 weeks
**Start Date:** Week 0 (IMMEDIATE)
**End Date:** Week 1
**Team Required:** 2 Backend Developers, 1 Security Engineer, 1 QA Engineer


<!-- Context: Implementation Roadmap > Phase 0: Emergency Security Fixes (Weeks 0-1) > Critical Path Dependencies -->

### Critical Path Dependencies
```
Security Fixes → All Other Work (BLOCKED until complete)
```


<!-- Context: Implementation Roadmap > Phase 0: Emergency Security Fixes (Weeks 0-1) > Security Status: PRODUCTION ILLEGAL -->

### Security Status: PRODUCTION ILLEGAL
**Current State:** Cannot legally deploy in Brazil due to LGPD violations
**Risk Level:** 🔴 **CRITICAL** - Legal liability and data breach risk


<!-- Context: Implementation Roadmap > Phase 0: Emergency Security Fixes (Weeks 0-1) > Week-by-Week Breakdown -->

### Week-by-Week Breakdown


<!-- Context: Implementation Roadmap > Phase 0: Emergency Security Fixes (Weeks 0-1) > Week-by-Week Breakdown > Week 0: Critical Security Fixes (Days 1-3) -->

#### Week 0: Critical Security Fixes (Days 1-3)
**Duration:** 3 days
**Priority:** 🔴 **URGENT** - Must complete before any other work
**Focus:** Fix user authorization and data access controls

**Tasks:**

1. **User Authorization Fixes (Day 1)**
   - Fix resume endpoints to check user ownership
   - Add user_id foreign key to resumes table
   - Implement proper RLS policies
   - Add authorization tests

   **Code Changes Required:**
   ```python
   # Fix in backend/app/api/endpoints/resumes.py
   @router.get("/{resume_id}", response_model=ResumeResponse)
   async def get_resume(
       resume_id: str, current_user: dict = Depends(get_current_user)
   ) -> ResumeResponse:
       resume_service = ResumeService()
       resume_data = await resume_service.get_resume_with_processed_data(resume_id)

       if not resume_data:
           raise HTTPException(status_code=404, detail="Resume not found")

       # ADD THIS CRITICAL CHECK
       if resume_data.get("user_id") != current_user["id"]:
           raise HTTPException(status_code=403, detail="Access denied")

       return resume_data
   ```

2. **Database Schema Fixes (Day 1)**
   - Add missing user_id columns
   - Create proper foreign key constraints
   - Fix RLS policies
   - Database migration scripts

   **Database Migration:**
   ```sql
   -- Add user_id to resumes table
   ALTER TABLE public.resumes
   ADD COLUMN user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE;

   -- Update RLS policies
   DROP POLICY IF EXISTS "Users can view own resumes" ON public.resumes;
   CREATE POLICY "Users can manage own resumes"
     ON public.resumes
     USING (auth.uid() = user_id);
   ```

3. **Security Audit and Testing (Day 2)**
   - Perform penetration testing on all endpoints
   - Verify authorization controls work correctly
   - Test data isolation between users
   - Document security fixes

4. **Remove Mock Data (Day 3)**
   - Remove hardcoded fake data from job_service.py
   - Implement proper error handling for missing AI integration
   - Add TODO tracking for real implementation
   - Update all mock data references

   **Code Changes:**
   ```python
   # Fix in backend/app/services/job_service.py
   async def _extract_structured_json(self, job_description_text: str):
       # REMOVE THIS MOCK DATA
       # logger.info("Structured JSON extraction not yet implemented")
       # return {"job_title": "Sample Job", ...}

       # IMPLEMENT PROPER ERROR HANDLING
       if not self.agent_manager:
           raise NotImplementedError(
               "AI Integration required for structured data extraction. "
               "Please complete AI service setup before processing job descriptions."
           )

       result = await self.agent_manager.extract_job_data(job_description_text)
       return result
   ```


<!-- Context: Implementation Roadmap > Phase 0: Emergency Security Fixes (Weeks 0-1) > Week-by-Week Breakdown > Week 0: LGPD Compliance and Bias Detection (Days 4-5) -->

#### Week 0: LGPD Compliance and Bias Detection (Days 4-5)

**Tasks:**

1. **Bias Detection Implementation (Day 4)**
   - Add anti-discrimination rules to all AI prompts
   - Implement bias detection in scoring
   - Add transparency in scoring algorithms
   - Create bias monitoring system

   **Code Changes:**
   ```python
   # Fix in backend/app/services/score_improvement_service.py
   def _build_score_prompt(self, resume_text: str, job_description: str) -> str:
       return f"""
       CRITICAL - ANTI-DISCRIMINATION RULES:
       - Do NOT consider: age, gender, race, religion, sexual orientation
       - Do NOT penalize: employment gaps, non-traditional backgrounds
       - ONLY evaluate: relevant skills, experience, qualifications
       - IGNORE: names, addresses, personal information unrelated to skills

       Você é um especialista em análise de currículos para o mercado brasileiro.

       Analise este currículo...
       """
   ```

2. **PII Detection Basic Implementation (Day 4)**
   - Implement basic PII pattern detection
   - Add masking for CPF, RG, email, phone
   - LGPD compliance basics
   - PII logging prevention

   **Code Changes:**
   ```python
   # Add new service: backend/app/services/pii_detection.py
   import re
   from typing import List, Tuple

   class PIIDetectionService:
       def __init__(self):
           self.pii_patterns = {
               'cpf': r'\d{3}\.\d{3}\.\d{3}-\d{2}',
               'rg': r'\d{1,2}\.\d{3}\.\d{3}-[\dX]',
               'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
               'phone': r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}',
           }

       def detect_and_mask_pii(self, text: str) -> Tuple[str, List[str]]:
           detected_pii = []
           masked_text = text

           for pii_type, pattern in self.pii_patterns.items():
               matches = re.findall(pattern, masked_text)
               if matches:
                   detected_pii.extend(matches)
                   masked_text = re.sub(pattern, f'[MASKED_{pii_type.upper()}]', masked_text)

           return masked_text, detected_pii
   ```

3. **Input Validation Implementation (Day 5)**
   - Add input validation to all endpoints
   - Implement file upload security
   - Add rate limiting
   - CORS configuration fixes

   **Code Changes:**
   ```python
   # Add validation models
   from pydantic import BaseModel, Field, validator

   class ResumeUploadRequest(BaseModel):
       content: str = Field(..., min_length=100, max_length=10000)
       file_type: str = Field(..., regex=r'^(pdf|docx)$')

       @validator('content')
       def validate_content(cls, v):
           if not v.strip():
               raise ValueError('Content cannot be empty')
           return v

   # Add rate limiting
   from slowapi import Limiter
   from slowapi.util import get_remote_address

   limiter = Limiter(key_func=get_remote_address)

   @router.post("/resumes")
   @limiter.limit("5/minute")
   async def upload_resume(
       request: ResumeUploadRequest,
       current_user: dict = Depends(get_current_user)
   ):
       # Process upload...
   ```


<!-- Context: Implementation Roadmap > Phase 0: Emergency Security Fixes (Weeks 0-1) > Week-by-Week Breakdown > Week 1: Security Verification and Documentation -->

#### Week 1: Security Verification and Documentation

**Tasks:**

1. **Security Testing (Day 6)**
   - Comprehensive penetration testing
   - Authorization testing for all endpoints
   - Data isolation verification
   - Performance impact assessment

2. **LGPD Compliance Audit (Day 7)**
   - Review all data handling practices
   - Verify PII detection works correctly
   - Check data retention policies
   - Create compliance documentation

3. **Security Documentation (Day 8)**
   - Document all security fixes
   - Create security checklist
   - Update API documentation
   - Prepare security audit report

**Deliverables:**
- Complete security fixes implementation
- Updated database schema with proper constraints
- PII detection and masking system
- Bias detection in AI prompts
- Input validation on all endpoints
- Security audit report
- LGPD compliance documentation

**Acceptance Criteria:**
- ✅ All security vulnerabilities resolved
- ✅ User authorization working correctly
- ✅ Database schema properly constrained
- ✅ PII detection operational
- ✅ Bias detection implemented
- ✅ Input validation added
- ✅ Security audit passed
- ✅ LGPD compliance verified

**Files to Create/Modify:**
```python
backend/app/api/endpoints/resumes.py (fixed)
backend/app/services/job_service.py (fixed)
backend/app/services/score_improvement_service.py (fixed)
backend/app/services/pii_detection.py (new)
backend/app/models/validation.py (new)
backend/app/migrations/add_user_id_to_resumes.sql (new)
docs/security/security-audit-report.md (new)
docs/compliance/lgpd-compliance.md (new)
```


<!-- Context: Implementation Roadmap > Phase 0: Emergency Security Fixes (Weeks 0-1) > Phase 0 Success Criteria -->

### Phase 0 Success Criteria
- [ ] **CRITICAL**: User authorization implemented and tested
- [ ] **CRITICAL**: Database schema fixed with foreign keys
- [ ] **CRITICAL**: Mock data removed from production code
- [ ] **CRITICAL**: Bias detection implemented in AI prompts
- [ ] **CRITICAL**: PII detection and masking operational
- [ ] **CRITICAL**: Input validation added to all endpoints
- [ ] **CRITICAL**: Security audit passed with zero critical findings
- [ ] **CRITICAL**: LGPD compliance verified by legal review

**🚨 PRODUCTION BLOCKER:** Phase 0 must be 100% complete before any other work can proceed.

---


<!-- Context: Implementation Roadmap > Phase 1: Core AI Foundation (Weeks 2-7) -->

## Phase 1: Core AI Foundation (Weeks 2-7)


<!-- Context: Implementation Roadmap > Phase 1: Core AI Foundation (Weeks 2-7) > Objective -->

### Objective
Establish the fundamental infrastructure for document processing, vector embeddings, and basic similarity matching.


<!-- Context: Implementation Roadmap > Phase 1: Core AI Foundation (Weeks 2-7) > Duration: 6 weeks -->

### Duration: 6 weeks
**Start Date:** Week 2 (AFTER Phase 0 completion)
**End Date:** Week 7
**Team Required:** 2 Backend Developers, 1 Frontend Developer, 1 QA Engineer
**Prerequisite:** Phase 0 Emergency Security Fixes **MUST** be completed first


<!-- Context: Implementation Roadmap > Phase 1: Core AI Foundation (Weeks 2-7) > Critical Path Dependencies -->

### Critical Path Dependencies
```
Phase 0 Complete → Document Processing → Vector Database → Basic Matching Algorithm
```


<!-- Context: Implementation Roadmap > Phase 1: Core AI Foundation (Weeks 2-7) > Week-by-Week Breakdown -->

### Week-by-Week Breakdown


<!-- Context: Implementation Roadmap > Phase 1: Core AI Foundation (Weeks 2-7) > Week-by-Week Breakdown > Week 2: Project Setup and Document Processing Foundation -->

#### Week 2: Project Setup and Document Processing Foundation
**Duration:** 5 days
**Focus:** Infrastructure setup and basic document processing

**Tasks:**
1. **Project Infrastructure (2 days)**
   - Set up development environments
   - Configure Qdrant vector database
   - Establish OpenAI API access
   - Create project documentation structure

2. **Document Upload Enhancement (2 days)**
   - Extend current upload functionality
   - Add file type validation (PDF, DOCX)
   - Implement file size limits and progress indicators
   - Create document metadata extraction

3. **Basic PDF Parsing (1 day)**
   - Implement PyPDF2 integration
   - Create text extraction service
   - Add error handling for corrupted files

**Deliverables:**
- Enhanced document upload API endpoint
- Basic PDF parsing service
- Qdrant database configuration
- Development environment setup guide

**Acceptance Criteria:**
- Users can upload PDF and DOCX files up to 10MB
- PDF text extraction works with 95% accuracy
- Qdrant database is accessible and configured
- All new APIs have basic test coverage

**Files to Create/Modify:**
```python
backend/app/services/document_processing.py
backend/app/api/endpoints/documents.py
backend/app/models/document.py
frontend/app/components/DocumentUpload.tsx
```


<!-- Context: Implementation Roadmap > Phase 1: Core AI Foundation (Weeks 2-7) > Week-by-Week Breakdown > Week 3: Advanced Document Processing -->

#### Week 3: Advanced Document Processing
**Duration:** 5 days
**Focus:** Complete document parsing pipeline

**Tasks:**
1. **DOCX Parsing Implementation (2 days)**
   - Integrate python-docx library
   - Implement text and metadata extraction
   - Handle different DOCX formats and versions

2. **Text Cleaning Pipeline (2 days)**
   - Remove special characters and formatting
   - Normalize whitespace and line breaks
   - Extract structured information (contact, dates, sections)

3. **Document Quality Validation (1 day)**
   - Implement content quality checks
   - Add minimum text length validation
   - Create document structure analysis

**Deliverables:**
- Complete document parsing service
- Text cleaning and normalization pipeline
- Document quality validation system
- Comprehensive document processing tests

**Acceptance Criteria:**
- Both PDF and DOCX parsing with 90%+ accuracy
- Text cleaning removes formatting artifacts
- Quality validation rejects low-quality documents
- Document processing completes in <5 seconds

**Files to Create/Modify:**
```python
backend/app/services/text_extraction.py
backend/app/services/metadata_extraction.py
backend/app/services/document_validator.py
tests/test_document_processing.py
```
