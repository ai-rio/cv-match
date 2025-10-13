# Agent Prompt: Usage Services Migration

**Agent**: backend-specialist
**Phase**: 1 - Usage Services (Parallel with payment services)
**Priority**: P0
**Estimated Time**: 2 hours
**Dependencies**: None (runs parallel with payment services)

---

## 🎯 Mission

Copy and adapt usage tracking and limit services from Resume-Matcher to cv-match, ensuring accurate credit management, usage tracking, and rate limiting.

---

## 📋 Tasks

### Task 1: Copy Usage Limit Service (1 hour)

**Source**: `/home/carlos/projects/Resume-Matcher/apps/backend/app/services/usage_limit_service.py`
**Target**: `/home/carlos/projects/cv-match/backend/app/services/usage_limit_service.py`

**Actions**:

1. Copy the file:

   ```bash
   cp /home/carlos/projects/Resume-Matcher/apps/backend/app/services/usage_limit_service.py \
      /home/carlos/projects/cv-match/backend/app/services/usage_limit_service.py
   ```

2. Update imports to match cv-match structure

3. Configure credit tiers:

   ```python
   CREDIT_TIERS = {
       "free": 3,
       "basic": 10,
       "pro": 50,
       "enterprise": 1000
   }
   ```

4. Test import:
   ```bash
   docker compose exec backend python -c "
   from app.services.usage_limit_service import UsageLimitService
   print('✅ UsageLimitService imported')
   "
   ```

**Success Criteria**:

- [x] File copied and adapted
- [x] Credit tiers configured
- [x] Imports working
- [x] Can check user credits

---

### Task 2: Copy Usage Tracking Service (45 min)

**Source**: `/home/carlos/projects/Resume-Matcher/apps/backend/app/services/usage_tracking_service.py`
**Target**: `/home/carlos/projects/cv-match/backend/app/services/usage_tracking_service.py`

**Actions**:

1. Copy the file:

   ```bash
   cp /home/carlos/projects/Resume-Matcher/apps/backend/app/services/usage_tracking_service.py \
      /home/carlos/projects/cv-match/backend/app/services/usage_tracking_service.py
   ```

2. Ensure it tracks:
   - Resume uploads
   - Optimization requests
   - Credit deductions
   - API calls

3. Test import:
   ```bash
   docker compose exec backend python -c "
   from app.services.usage_tracking_service import UsageTrackingService
   print('✅ UsageTrackingService imported')
   "
   ```

**Success Criteria**:

- [x] File copied
- [x] Tracks all usage types
- [x] Integrates with database
- [x] Audit trail created

---

### Task 3: Copy Paid Resume Improvement Service (15 min)

**Source**: `/home/carlos/projects/Resume-Matcher/apps/backend/app/services/paid_resume_improvement_service.py`
**Target**: `/home/carlos/projects/cv-match/backend/app/services/paid_resume_improvement_service.py`

**Actions**:

1. Copy the file:

   ```bash
   cp /home/carlos/projects/Resume-Matcher/apps/backend/app/services/paid_resume_improvement_service.py \
      /home/carlos/projects/cv-match/backend/app/services/paid_resume_improvement_service.py
   ```

2. Ensure it:
   - Checks credits before processing
   - Deducts credits after success
   - Handles insufficient credits gracefully

3. Test import:
   ```bash
   docker compose exec backend python -c "
   from app.services.paid_resume_improvement_service import PaidResumeImprovementService
   print('✅ PaidResumeImprovementService imported')
   "
   ```

**Success Criteria**:

- [x] File copied
- [x] Credit checking works
- [x] Credit deduction atomic
- [x] Error handling complete

---

## 🔧 Technical Details

### Usage Limit Service Pattern

```python
class UsageLimitService:
    def __init__(self):
        self.db = get_supabase_client()

    async def check_credits(self, user_id: str) -> int:
        """Get remaining credits for user"""
        result = self.db.table("user_credits")\
            .select("credits_remaining")\
            .eq("user_id", user_id)\
            .single()\
            .execute()
        return result.data["credits_remaining"] if result.data else 0

    async def deduct_credits(
        self,
        user_id: str,
        amount: int,
        operation_id: str
    ) -> bool:
        """Deduct credits atomically"""
        # Use database transaction for atomicity
        current = await self.check_credits(user_id)
        if current < amount:
            return False

        # Atomic update with check
        result = self.db.rpc("deduct_credits", {
            "p_user_id": user_id,
            "p_amount": amount,
            "p_operation_id": operation_id
        }).execute()

        return result.data["success"]

    async def add_credits(
        self,
        user_id: str,
        amount: int,
        source: str
    ):
        """Add credits (from payment)"""
        self.db.table("credit_transactions").insert({
            "user_id": user_id,
            "amount": amount,
            "type": "credit",
            "source": source,
            "timestamp": "now()"
        }).execute()
```

### Usage Tracking Pattern

```python
class UsageTrackingService:
    async def track_usage(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        metadata: dict = None
    ):
        """Track user action"""
        self.db.table("usage_tracking").insert({
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "metadata": metadata,
            "timestamp": "now()"
        }).execute()
```

---

## 📊 Verification Checklist

```bash
cd /home/carlos/projects/cv-match/backend

# 1. Verify files exist
ls -la app/services/usage_limit_service.py
ls -la app/services/usage_tracking_service.py
ls -la app/services/paid_resume_improvement_service.py

# 2. Test all imports
docker compose exec backend python -c "
from app.services.usage_limit_service import UsageLimitService
from app.services.usage_tracking_service import UsageTrackingService
from app.services.paid_resume_improvement_service import PaidResumeImprovementService
print('✅ All usage services import')
"

# 3. Test service instantiation
docker compose exec backend python -c "
from app.services.usage_limit_service import UsageLimitService
service = UsageLimitService()
print('✅ UsageLimitService instantiated')
"
```

---

## 📝 Deliverables

### Files to Create:

1. `backend/app/services/usage_limit_service.py`
2. `backend/app/services/usage_tracking_service.py`
3. `backend/app/services/paid_resume_improvement_service.py`

### Git Commit:

```bash
git add backend/app/services/usage_limit_service.py
git add backend/app/services/usage_tracking_service.py
git add backend/app/services/paid_resume_improvement_service.py
git commit -m "feat(usage): Add usage tracking and limit services

- Add UsageLimitService for credit management
- Add UsageTrackingService for audit trails
- Add PaidResumeImprovementService for paid operations
- Configure credit tiers (free: 3, basic: 10, pro: 50)
- Implement atomic credit deduction
- Add usage tracking for all operations

Features:
- Check credits before operation
- Deduct credits atomically
- Track all user actions
- Prevent negative credits
- Audit trail for compliance

Related: P1 Payment Integration Phase 1
Tested: All imports verified"
```

---

## ⏱️ Timeline

- **00:00-01:00**: Task 1 (Usage limit service)
- **01:00-01:45**: Task 2 (Usage tracking service)
- **01:45-02:00**: Task 3 (Paid improvement service)

**Total**: 2 hours

---

## 🎯 Success Definition

Mission complete when:

1. All 3 services copied and working
2. Credit tiers configured
3. Atomic credit operations implemented
4. Usage tracking functional
5. All imports working
6. Ready for database integration (Phase 2)

---

## 🔄 Handoff to Next Phase

After completion, notify database-architect:

- ✅ Usage services ready
- ✅ Need tables: user_credits, credit_transactions, usage_tracking
- ✅ Need RPC function for atomic credit deduction

**Status**: Ready for deployment 🚀
