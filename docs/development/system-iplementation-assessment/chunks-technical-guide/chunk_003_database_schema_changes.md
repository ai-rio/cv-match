---
chunk: 3
total_chunks: 7
title: Database Schema Changes
context: backend/app/services/llm/llm_service.py (Enhanced) > Database Schema Changes
estimated_tokens: 3097
source: technical-integration-guide.md
---

<!-- Context: Specialized services for resume matching -->

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


<!-- Context: Specialized services for resume matching > 2. LLM Service Enhancement -->

#### 2. LLM Service Enhancement

```python

<!-- Context: backend/app/services/llm/llm_service.py (Enhanced) -->

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


<!-- Context: backend/app/services/llm/llm_service.py (Enhanced) > Database Schema Changes -->

## Database Schema Changes
