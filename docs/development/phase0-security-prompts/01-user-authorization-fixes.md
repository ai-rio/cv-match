# User Authorization Security Fixes

**Agent**: backend-security-specialist
**Time**: 4 hours
**Priority**: 🔴 CRITICAL
**Phase**: 0.1
**Dependencies**: None (can start immediately)

## Executive Summary

Fix critical user authorization vulnerability that allows any authenticated user to access any other user's resume data. This is a **CRITICAL security vulnerability** that violates data protection laws and enables data breaches.

## Problem Statement

### Security Vulnerability: Missing User Authorization

**Current Issue**: The resume endpoints have NO user authorization checks. Any authenticated user can access ANY resume by simply knowing the resume ID.

**Evidence from Code Review**:
```python
# From resumes.py, line 127-142
@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str, current_user: dict = Depends(get_current_user)
) -> ResumeResponse:
    """Get a specific resume by ID."""
    resume_service = ResumeService()
    resume_data = await resume_service.get_resume_with_processed_data(resume_id)

    if not resume_data:
        raise HTTPException(status_code=404, detail="Resume not found")

    # ⚠️ NO CHECK: if resume belongs to current_user!
    # This allows any authenticated user to access any resume
```

**Business Impact**:
- **Legal Liability**: Violates LGPD (Brazilian data protection law)
- **Data Breach**: Complete exposure of user resume data
- **Market Entry**: Illegal to deploy in Brazil without this fix

## Context & Documentation References

### Security Assessment Findings
- **Critical Finding**: User authorization gap allows any authenticated user to access any resume by ID
- **Business Impact**: Data breach risk and LGPD violation
- **Reference**: [`chunk_003_1_security_vulnerability_exploitation.md`](../system-iplementation-assessment/chunks/chunk_003_1_security_vulnerability_exploitation.md)

### Technical Implementation Context
- **Related Implementation**: [`chunk_002_backendappservicessupabasedatabasepy_enhanced.md`](../system-iplementation-assessment/chunks-technical-guide/chunk_002_backendappservicessupabasedatabasepy_enhanced.md)
- **Database Context**: [`chunk_003_database_schema_changes.md`](../system-iplementation-assessment/chunks-technical-guide/chunk_003_database_schema_changes.md)
- **API Context**: [`chunk_004_2_resume_matching_endpoints.md`](../system-iplementation-assessment/chunks-technical-guide/chunk_004_2_resume_matching_endpoints.md)

### Phase Dependencies
- **Must Complete Before**: Phase 0.2 (Data Protection)
- **Can Run Parallel With**: Phase 0.1 database schema and input validation
- **Enables**: All subsequent security phases

## Security Requirements

1. **User Data Isolation**: Users can ONLY access their own resume data
2. **Authorization Checks**: All resume endpoints must verify user ownership
3. **Database Constraints**: user_id foreign key must be properly enforced
4. **RLS Policies**: Row Level Security policies must correctly restrict data access
5. **Error Handling**: Security errors must not leak information
6. **Audit Logging**: All access attempts must be logged
7. **Testing**: Comprehensive security tests for authorization bypasses
8. **Documentation**: Security measures must be documented

## Acceptance Criteria

- [ ] All resume endpoints verify user ownership before data access
- [ ] User can only access resumes with matching user_id
- [ ] Database schema includes proper user_id foreign key constraints
- [ ] RLS policies correctly enforce user data isolation
- [ ] Security tests pass for authorization bypass attempts
- [ ] Error responses don't leak sensitive information
- [ ] Security events are properly logged
- [ ] Manual testing confirms data isolation works correctly

## Technical Constraints

1. **Backward Compatibility**: Don't break existing valid user workflows
2. **Performance**: Authorization checks must not significantly impact response times
3. **Database Impact**: Schema changes must be migration-safe
4. **Error Messages**: Must be generic to prevent information leakage
5. **Testing**: All security fixes must have comprehensive test coverage

## Chunk Reading Order

For this task, read these chunks in order:
1. [`chunk_003_1_security_vulnerability_exploitation.md`](../system-iplementation-assessment/chunks/chunk_003_1_security_vulnerability_exploitation.md) - Security vulnerability details
2. [`chunk_004_2_resume_matching_endpoints.md`](../system-iplementation-assessment/chunks-technical-guide/chunk_004_2_resume_matching_endpoints.md) - Current endpoint implementations
3. [`chunk_003_database_schema_changes.md`](../system-iplementation-assessment/chunks-technical-guide/chunk_003_database_schema_changes.md) - Database schema for security context

## Testing Requirements

- **Authorization Bypass Testing**: Verify users cannot access other users' data
- **Edge Case Testing**: Test with various user roles and permission scenarios
- **Performance Testing**: Ensure security checks don't degrade performance
- **Security Testing**: Penetration testing for authorization vulnerabilities
- **Integration Testing**: Verify security works across all related endpoints

## Implementation Tasks

### 1. Fix Resume Endpoints (HIGH PRIORITY)

**Files to Fix**:
- `backend/app/api/endpoints/resumes.py`
- `backend/app/services/resume_service.py`

**Required Changes**:
```python
# Add user authorization check in ALL resume endpoints
@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str, current_user: dict = Depends(get_current_user)
) -> ResumeResponse:
    """Get a specific resume by ID."""
    resume_service = ResumeService()

    # ADD USER AUTHORIZATION CHECK
    resume_data = await resume_service.get_resume_with_user_check(
        resume_id, current_user["id"]
    )

    if not resume_data:
        raise HTTPException(status_code=404, detail="Resume not found")

    return resume_data
```

### 2. Update Resume Service

**Required Changes**:
```python
# Add user authorization methods to ResumeService
async def get_resume_with_user_check(self, resume_id: str, user_id: str) -> Optional[dict]:
    """Get resume only if belongs to user"""
    query = self.client.table("resumes") \
        .select("*") \
        .eq("id", resume_id) \
        .eq("user_id", user_id) \
        .single()

    response = query.execute()
    return response.data if response.data else None
```

### 3. Verify Database Schema

**Check Current Schema**:
```sql
-- Verify resumes table has user_id column
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'resumes' AND column_name = 'user_id';
```

### 4. Update RLS Policies

**Required Changes**:
```sql
-- Ensure RLS policies enforce user isolation
CREATE POLICY "Users can only access own resumes"
ON public.resumes
FOR ALL
USING (auth.uid() = user_id);
```

### 5. Add Security Tests

**Test Files to Create/Update**:
- `tests/test_resume_authorization.py`

**Required Tests**:
```python
async def test_user_cannot_access_other_user_resume():
    """Verify user cannot access another user's resume"""
    # Create user1 and user2
    # Create resume for user1
    # Try to access resume as user2
    # Verify access denied

async def test_user_can_access_own_resume():
    """Verify user can access their own resume"""
    # Create user and resume
    # Access resume as same user
    # Verify access successful
```

## Security Verification Checklist

After implementation, verify:

### Manual Testing
- [ ] User A cannot access User B's resume (403/404 response)
- [ ] User A can access their own resume (200 response)
- [ ] Anonymous users cannot access any resume (401 response)
- [ ] Error responses don't reveal resume existence

### Automated Testing
- [ ] All authorization tests pass
- [ ] Security scan shows no authorization vulnerabilities
- [ ] Performance impact is minimal (<100ms additional latency)

### Database Security
- [ ] user_id foreign key constraints enforced
- [ ] RLS policies working correctly
- [ ] Database queries filter by user_id correctly

## Rollback Procedures

If issues occur:
1. **Immediate Rollback**: Revert to previous working commit
2. **Database Rollback**: Reverse schema changes if applied
3. **Service Rollback**: Restore previous service implementations
4. **Testing**: Verify system functionality after rollback

## Success Metrics

- **Zero Authorization Bypasses**: No user can access another user's data
- **Security Tests Pass**: 100% security test pass rate
- **Performance Impact**: <5% increase in response times
- **User Experience**: No negative impact on legitimate user workflows

## Final Security Validation

Before completion, run this security verification:

```bash
# Test authorization bypasses
python -m pytest tests/test_resume_authorization.py -v

# Verify RLS policies
psql $DATABASE_URL -c "SELECT * FROM pg_policies WHERE tablename = 'resumes';"

# Test manual authorization
curl -H "Authorization: Bearer USER_A_TOKEN" \
     http://localhost:8000/api/resumes/USER_B_RESUME_ID
# Should return 403/404, not resume data
```

---

## 🚨 CRITICAL REMINDER

This security fix is **MANDATORY** before any other development:
- **Legal Requirement**: LGPD compliance requires user data isolation
- **Security Requirement**: Prevents data breaches
- **Business Requirement**: Enables legal deployment in Brazil

**Do not proceed to other phases until this security fix is complete and verified.**