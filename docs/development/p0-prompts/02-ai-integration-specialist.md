# Agent Prompt: AI Integration & Score Service

**Agent**: ai-integration-specialist  
**Phase**: 1 - AI Services (Parallel with Backend Services)  
**Priority**: P0  
**Estimated Time**: 2.5 hours  
**Dependencies**: None (can start immediately, works in parallel)

---

## 🎯 Mission

Copy and adapt the score_improvement_service.py and the entire agent/ system from Resume-Matcher to cv-match, ensuring OpenRouter integration works and LLM orchestration is operational.

---

## 📋 Tasks

### Task 1: Copy agent/ Directory System (1 hour)

**Source**: `/home/carlos/projects/Resume-Matcher/apps/backend/app/agent/`  
**Target**: `/home/carlos/projects/cv-match/backend/app/agent/`

**Actions**:
1. Copy entire agent directory structure:
   ```bash
   cp -r /home/carlos/projects/Resume-Matcher/apps/backend/app/agent \
         /home/carlos/projects/cv-match/backend/app/
   ```

2. Review copied files and identify:
   - `manager.py` - Main orchestrator
   - Provider files (OpenRouter, Anthropic, etc.)
   - Utility files
   - Config files

3. Update imports in ALL files to match cv-match structure

4. Verify environment variables needed:
   - `RESUME_MATCHER_LLM_PROVIDER`
   - `RESUME_MATCHER_LLM_MODEL`
   - `OPENROUTER_API_KEY` or `ANTHROPIC_API_KEY`

5. Test basic import:
   ```bash
   docker compose exec backend python -c "
   from app.agent.manager import AgentManager
   print('✅ AgentManager imported')
   "
   ```

**Success Criteria**:
- [x] Directory copied with all files
- [x] All imports updated
- [x] AgentManager can be imported
- [x] No missing dependencies

---

### Task 2: Adapt score_improvement_service.py (1 hour)

**Source**: `/home/carlos/projects/Resume-Matcher/apps/backend/app/services/score_improvement_service.py`  
**Target**: `/home/carlos/projects/cv-match/backend/app/services/score_improvement_service.py`

**Actions**:
1. Copy the file to target location

2. Update imports to match cv-match + agent system:
   ```python
   from app.agent.manager import AgentManager
   from app.core.database import get_supabase_client
   from app.services.resume_service import ResumeService
   from app.services.job_service import JobService
   ```

3. Ensure the service integrates with:
   - Agent system for LLM calls
   - Resume service for resume data
   - Job service for job description data
   - Database for storing results

4. Adapt any Resume-Matcher-specific patterns

5. Test integration:
   ```bash
   docker compose exec backend python -c "
   from app.services.score_improvement_service import ScoreImprovementService
   svc = ScoreImprovementService()
   print('✅ ScoreImprovementService working')
   "
   ```

**Success Criteria**:
- [x] File copied and adapted
- [x] Imports work
- [x] Service instantiable
- [x] Integrates with agent system
- [x] Ready to calculate scores

---

### Task 3: Test LLM Integration (30 min)

**Actions**:
1. Create test script for LLM integration:
   ```python
   # File: backend/test_llm_integration.py
   import asyncio
   from app.agent.manager import AgentManager
   
   async def test_llm():
       manager = AgentManager()
       print(f"✅ Initialized with {len(manager.providers)} provider(s)")
       
       # Test simple completion
       response = await manager.generate(
           "Diga 'olá' em português",
           max_tokens=50
       )
       print(f"✅ LLM Response: {response[:100]}")
       print("✅ LLM integration working!")
   
   if __name__ == "__main__":
       asyncio.run(test_llm())
   ```

2. Run the test:
   ```bash
   docker compose exec backend python test_llm_integration.py
   ```

3. Verify:
   - Agent Manager initializes
   - Can make LLM API calls
   - Responses are received
   - No rate limiting issues (in test mode)

**Success Criteria**:
- [x] AgentManager initializes with providers
- [x] Can make test completion request
- [x] Receives response from LLM
- [x] No API key errors
- [x] Ready for production use

---

## 🔧 Technical Details

### Agent System Architecture

The agent system should have:
```
app/agent/
├── __init__.py
├── manager.py          # Main orchestrator
├── providers/
│   ├── __init__.py
│   ├── openrouter.py  # OpenRouter integration
│   ├── anthropic.py   # Direct Anthropic (if used)
│   └── base.py        # Base provider class
└── utils/
    ├── __init__.py
    └── prompts.py     # Prompt templates
```

### Score Improvement Service Pattern

```python
class ScoreImprovementService:
    def __init__(self):
        self.agent_manager = AgentManager()
        self.resume_service = ResumeService()
        self.job_service = JobService()
    
    async def calculate_match_score(
        self,
        resume_text: str,
        job_description: str
    ) -> dict:
        """Calculate match score using LLM"""
        
        # Build prompt
        prompt = self._build_score_prompt(resume_text, job_description)
        
        # Get LLM response
        response = await self.agent_manager.generate(
            prompt,
            max_tokens=2000,
            temperature=0.3  # Lower for more consistent scoring
        )
        
        # Parse response
        result = self._parse_score_response(response)
        
        return {
            "match_score": result["score"],
            "improvements": result["suggestions"],
            "keywords": result["keywords"]
        }
```

### Prompt Engineering for Brazilian Market

Ensure prompts include:
```python
def _build_score_prompt(self, resume: str, job: str) -> str:
    return f"""
    Você é um especialista em análise de currículos para o mercado brasileiro.
    
    Analise este currículo em relação à vaga e forneça:
    1. Score de compatibilidade (0-100)
    2. Principais pontos fortes
    3. Áreas de melhoria
    4. Palavras-chave para ATS
    
    CURRÍCULO:
    {resume}
    
    VAGA:
    {job}
    
    Responda em JSON válido com as chaves:
    - score (número)
    - strengths (lista)
    - improvements (lista)
    - keywords (lista)
    """
```

---

## 🚨 Common Issues & Solutions

### Issue 1: OpenRouter API Key Not Found
**Symptom**: `KeyError: 'OPENROUTER_API_KEY'`  
**Solution**: 
```bash
# Check .env
grep OPENROUTER_API_KEY backend/.env

# Add if missing
echo "OPENROUTER_API_KEY=your_key_here" >> backend/.env

# Restart backend
docker compose restart backend
```

### Issue 2: Rate Limiting
**Symptom**: `429 Too Many Requests`  
**Solution**: Implement retry with exponential backoff in agent/manager.py

### Issue 3: LLM Response Parsing
**Symptom**: `JSONDecodeError`  
**Solution**: Add robust parsing with fallbacks:
```python
def _parse_score_response(self, response: str) -> dict:
    try:
        # Try to parse as JSON
        return json.loads(response)
    except json.JSONDecodeError:
        # Extract from markdown code blocks
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
            return json.loads(json_str)
        # Fallback
        return {"score": 0, "error": "Failed to parse response"}
```

### Issue 4: Timeout on Long Completions
**Symptom**: `TimeoutError`  
**Solution**: Increase timeout in httpx client:
```python
async with httpx.AsyncClient(timeout=60.0) as client:
    # Make request
```

---

## 📊 Verification Checklist

```bash
cd /home/carlos/projects/cv-match/backend

# 1. Test agent system import
docker compose exec backend python -c "
from app.agent.manager import AgentManager
print('✅ Agent system imports')
"

# 2. Test AgentManager initialization
docker compose exec backend python -c "
from app.agent.manager import AgentManager
manager = AgentManager()
print(f'✅ Initialized with providers: {type(manager).__name__}')
"

# 3. Test score service import
docker compose exec backend python -c "
from app.services.score_improvement_service import ScoreImprovementService
print('✅ ScoreImprovementService imports')
"

# 4. Test score service initialization
docker compose exec backend python -c "
from app.services.score_improvement_service import ScoreImprovementService
svc = ScoreImprovementService()
print('✅ ScoreImprovementService initialized')
"

# 5. Test LLM integration
docker compose exec backend python test_llm_integration.py
```

---

## 📝 Deliverables

### Files to Create:
1. `/home/carlos/projects/cv-match/backend/app/agent/` (entire directory)
   - `manager.py`
   - `providers/` directory with provider implementations
   - `utils/` directory with utilities
2. `/home/carlos/projects/cv-match/backend/app/services/score_improvement_service.py`
3. `/home/carlos/projects/cv-match/backend/test_llm_integration.py` (test script)

### Environment Variables to Add:
Add to `backend/.env`:
```env
# LLM Configuration
RESUME_MATCHER_LLM_PROVIDER=openrouter
RESUME_MATCHER_LLM_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_API_KEY=your_key_here

# Or for direct Anthropic
# ANTHROPIC_API_KEY=your_key_here
```

### Documentation:
- Document LLM provider configuration
- Note prompt templates used
- Explain score calculation logic

### Git Commit:
```bash
git add backend/app/agent/
git add backend/app/services/score_improvement_service.py
git add backend/test_llm_integration.py
git commit -m "feat(ai): Add LLM integration and score calculation

- Copy agent system from Resume-Matcher
- Add AgentManager for LLM orchestration
- Implement score_improvement_service for match calculation
- Configure OpenRouter integration
- Add test script for LLM verification
- Brazilian market prompt templates

Related: P0 AI Services implementation"
```

---

## ⏱️ Timeline

- **00:00-01:00**: Task 1 (Copy agent/ system)
- **01:00-02:00**: Task 2 (score_improvement_service.py)
- **02:00-02:30**: Task 3 (LLM integration testing)

**Total**: 2.5 hours

---

## 🎯 Success Definition

Mission complete when:
1. Agent system fully copied and operational
2. Score improvement service working
3. LLM integration tested and verified
4. Can make test completions
5. Ready to integrate with API endpoints

---

## 🔄 Handoff to Backend Specialist

After completion, notify backend-specialist agent:
- ✅ Agent system operational
- ✅ Score service available
- ✅ LLM integration working
- Ready for API endpoint integration

**Status**: Ready for deployment 🚀
