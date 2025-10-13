# Database Schema Security

**Agent**: database-security-architect
**Time**: 4 hours
**Priority**: 🔴 CRITICAL
**Phase**: 0.1
**Dependencies**: None (can start immediately)

## Executive Summary

Fix critical database schema vulnerabilities that prevent user data isolation and violate LGPD compliance. Missing user_id foreign keys and inadequate RLS policies create fundamental security flaws that enable data breaches.

## Problem Statement

### Security Vulnerability: Database Schema Without User Relationships

**Current Issue**: Database tables lack proper user_id foreign keys and constraints, making user data isolation impossible at the database level.

**Evidence from Code Review**:
```sql
-- From 20251010185206_create_resumes_table.sql
CREATE TABLE IF NOT EXISTS public.resumes (
    id BIGSERIAL PRIMARY KEY,
    resume_id UUID NOT NULL UNIQUE,
    content TEXT NOT NULL,
    -- ⚠️ MISSING: user_id column entirely!
);
```

**Business Impact**:
- **Legal Liability**: Cannot enforce LGPD data protection at database level
- **Data Integrity**: Orphaned records and inconsistent relationships
- **Security Foundation**: No database-level security for user data isolation

## Context & Documentation References

### Security Assessment Findings
- **Critical Finding**: Missing user_id foreign key on resumes table
- **Business Impact**: Cannot associate data with users, data breach risk
- **Reference**: [`chunk_003_1_security_vulnerability_exploitation.md`](../system-iplementation-assessment/chunks/chunk_003_1_security_vulnerability_exploitation.md)

### Technical Implementation Context
- **Related Implementation**: [`chunk_003_database_schema_changes.md`](../system-iplementation-assessment/chunks-technical-guide/chunk_003_database_schema_changes.md)
- **Database Service**: [`chunk_002_backendappservicessupabasedatabasepy_enhanced.md`](../system-iplementation-assessment/chunks-technical-guide/chunk_002_backendappservicessupabasedatabasepy_enhanced.md)
- **Schema Context**: [`chunk_004_2_resume_matching_endpoints.md`](../system-iplementation-assessment/chunks-technical-guide/chunk_004_2_resume_matching_endpoints.md)

### Phase Dependencies
- **Must Complete Before**: Phase 0.2 (Data Protection)
- **Can Run Parallel With**: Phase 0.1 user authorization and input validation
- **Enables**: User authorization fixes and all subsequent security phases

## Security Requirements

1. **User Data Association**: Add user_id foreign key columns to all user-data tables
2. **RLS Enforcement**: Implement strict Row Level Security policies using auth.uid() = user_id
3. **Data Integrity**: Create proper foreign key constraints between related tables
4. **Validation Constraints**: Add data integrity constraints (NOT NULL, CHECK constraints, ranges)
5. **Security Indexes**: Create security indexes for user_id and foreign key columns
6. **Audit Logging**: Implement audit logging for all data access operations
7. **RLS Enablement**: Ensure RLS is enabled on all user-data tables
8. **Migration Safety**: Handle existing data without data loss

## Acceptance Criteria

- [ ] All user-data tables have user_id UUID foreign key to auth.users(id)
- [ ] RLS policies enforce strict user ownership (auth.uid() = user_id)
- [ ] Foreign key constraints prevent orphaned records
- [ ] Data integrity constraints validate score ranges and required fields
- [ ] Security indexes exist for all user_id and foreign key columns
- [ ] Audit logging captures all INSERT/UPDATE/DELETE operations
- [ ] Database migration handles existing data without data loss
- [ ] Cross-user data access is impossible at database level

## Technical Constraints

1. **Data Preservation**: Must maintain existing data during migration (no data loss)
2. **Backward Compatibility**: Cannot break existing application functionality
3. **Rollback Capability**: All changes must be reversible with rollback migration
4. **Performance Impact**: Performance impact must be minimal (<20ms additional query time)
5. **Legal Compliance**: Must comply with LGPD data protection requirements
6. **Migration Safety**: Database migrations must be idempotent and testable

## Chunk Reading Order

For this task, read these chunks in order:
1. [`chunk_003_1_security_vulnerability_exploitation.md`](../system-iplementation-assessment/chunks/chunk_003_1_security_vulnerability_exploitation.md) - Security vulnerability details
2. [`chunk_003_database_schema_changes.md`](../system-iplementation-assessment/chunks-technical-guide/chunk_003_database_schema_changes.md) - Database schema requirements
3. [`chunk_002_backendappservicessupabasedatabasepy_enhanced.md`](../system-iplementation-assessment/chunks-technical-guide/chunk_002_backendappservicessupabasedatabasepy_enhanced.md) - Database service context

## Testing Requirements

- **Schema Verification**: Database schema verification script confirms all changes applied
- **Cross-User Access Tests**: Cross-user data access tests fail with appropriate errors
- **Data Integrity Tests**: Data integrity constraint tests validate input boundaries
- **Performance Tests**: Performance tests confirm minimal impact on query times
- **Audit Logging Tests**: Audit logging verification confirms all operations captured
- **Migration Rollback Tests**: Migration rollback test ensures changes are reversible

## Implementation Tasks

### 1. Schema Assessment (HIGH PRIORITY)

**Current State Analysis**:
```sql
-- Check existing table schemas
SELECT table_name, column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name IN ('resumes', 'job_descriptions', 'match_results')
  AND column_name = 'user_id';

-- Check current RLS status
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('resumes', 'job_descriptions', 'match_results');
```

### 2. Create Security Migration

**Migration File**: `supabase/migrations/20251013_add_user_security_columns.sql`

**Required Changes**:
```sql
-- Add user_id columns to existing tables
ALTER TABLE public.resumes
ADD COLUMN IF NOT EXISTS user_id UUID NOT NULL DEFAULT gen_random_uuid()
REFERENCES auth.users(id) ON DELETE CASCADE;

ALTER TABLE public.job_descriptions
ADD COLUMN IF NOT EXISTS user_id UUID NOT NULL DEFAULT gen_random_uuid()
REFERENCES auth.users(id) ON DELETE CASCADE;

-- Enable RLS on all user-data tables
ALTER TABLE public.resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_descriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.match_results ENABLE ROW LEVEL SECURITY;

-- Create strict RLS policies
DROP POLICY IF EXISTS "Users can manage own resumes" ON public.resumes;
CREATE POLICY "Users can manage own resumes" ON public.resumes
FOR ALL
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- Similar policies for other tables...
```

### 3. Data Migration Strategy

**Handle Existing Data**:
```sql
-- For existing resumes without user_id, assign to system user for now
UPDATE public.resumes
SET user_id = (SELECT id FROM auth.users WHERE email = 'system@cv-match.com' LIMIT 1)
WHERE user_id IS NULL;

-- Add data integrity constraints
ALTER TABLE public.match_results
ADD CONSTRAINT chk_overall_score_range CHECK (overall_score >= 0 AND overall_score <= 100);

ALTER TABLE public.match_results
ADD CONSTRAINT chk_confidence_score_range CHECK (confidence_score >= 0 AND confidence_score <= 1);
```

### 4. Create Security Indexes

**Performance Optimization**:
```sql
-- Create security indexes
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON public.resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_job_descriptions_user_id ON public.job_descriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_match_results_user_id ON public.match_results(user_id);

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_match_results_user_resume ON public.match_results(user_id, resume_id);
CREATE INDEX IF NOT EXISTS idx_match_results_user_job ON public.match_results(user_id, job_id);
```

### 5. Implement Audit Logging

**Audit Trail Setup**:
```sql
-- Create audit table
CREATE TABLE IF NOT EXISTS public.data_access_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL, -- INSERT, UPDATE, DELETE, SELECT
    user_id UUID REFERENCES auth.users(id),
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS on audit table
ALTER TABLE public.data_access_audit ENABLE ROW LEVEL SECURITY;
```

### 6. Update Application Services

**Service Layer Changes**:
```python
# Update SupabaseDatabaseService to enforce user_id
class SupabaseDatabaseService(Generic[T]):
    async def create(self, data: Dict[str, Any], user_id: str) -> T:
        """Create new record with user association"""
        data_with_user = {**data, "user_id": user_id}
        # ... rest of implementation

    async def get_by_user(self, user_id: str, filters: Dict[str, Any] = None) -> List[T]:
        """Get records for specific user - RLS handles filtering"""
        query = self.client.table(self.table_name).select("*")

        # RLS will automatically filter by user_id, but we can be explicit
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        response = query.execute()
        return [self.model_class(**item) for item in response.data]
```

## Security Verification Checklist

After implementation, verify:

### Database Security
- [ ] All user-data tables have user_id foreign key constraints
- [ ] RLS policies enforce strict user ownership
- [ ] Security indexes created and performing well
- [ ] Data integrity constraints preventing invalid data

### Access Control Testing
- [ ] Cross-user SELECT queries return no data
- [ ] Cross-user UPDATE/DELETE operations are blocked
- [ ] Users can only access their own data
- [ ] System can handle user data association correctly

### Performance Testing
- [ ] Query performance impact <20ms per query
- [ ] Indexes are being used by query planner
- [ ] RLS policies don't significantly impact performance

### Data Integrity
- [ ] Foreign key constraints prevent orphaned records
- [ ] Check constraints validate score ranges
- [ ] NOT NULL constraints enforced
- [ ] Migration handled existing data correctly

## Rollback Procedures

If issues occur:
1. **Migration Rollback**: Apply reverse migration to remove user_id columns
2. **Service Rollback**: Revert service implementations to previous version
3. **Data Recovery**: Restore from backup if data corruption occurs
4. **Application Rollback**: Deploy previous working application version

## Success Metrics

- **Zero Data Leaks**: No cross-user data access possible
- **Schema Integrity**: All constraints properly enforced
- **Performance**: <20ms additional query time overhead
- **Data Consistency**: No orphaned records or data integrity violations

## Final Security Validation

Before completion, run this security verification:

```bash
# Verify schema changes
psql $DATABASE_URL -c "\d public.resumes"
psql $DATABASE_URL -c "SELECT * FROM pg_policies WHERE tablename = 'resumes';"

# Test cross-user access
psql $DATABASE_URL -c "SELECT * FROM public.resumes WHERE user_id = 'other-user-id';"
# Should return empty result due to RLS

# Performance test
psql $DATABASE_URL -c "EXPLAIN ANALYZE SELECT * FROM public.resumes WHERE user_id = 'test-user-id';"
```

---

## 🚨 CRITICAL REMINDER

This database security fix is **MANDATORY** before any other development:
- **Legal Requirement**: LGPD compliance requires database-level data protection
- **Security Foundation**: Database security enables all other security measures
- **Business Requirement**: Enables legal deployment in Brazil

**Do not proceed to other phases until this database security fix is complete and verified.**