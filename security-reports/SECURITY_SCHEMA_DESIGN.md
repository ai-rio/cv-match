# CV-Match Security Schema Design - Phase 0.2

**Date**: 2025-10-13
**Designer**: Database Architect
**Status**: Ready for Implementation

## Overview

This document outlines the secure schema design changes required to fix the critical database security vulnerabilities identified in the CV-Match system. The changes ensure LGPD compliance and proper user data isolation.

## Schema Changes Required

### 1. Resumes Table Security Enhancement

#### Current Issues:
- Missing user_id column
- No user ownership enforcement
- Inadequate RLS policies
- No foreign key constraints

#### Proposed Secure Schema:
```sql
-- Enhanced resumes table with proper security
ALTER TABLE public.resumes
ADD COLUMN user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE;

-- Add index for performance
CREATE INDEX idx_resumes_user_id ON public.resumes(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_resumes_user_created ON public.resumes(user_id, created_at DESC) WHERE deleted_at IS NULL;

-- Add validation constraint
ALTER TABLE public.resumes
ADD CONSTRAINT resumes_user_id_not_empty
CHECK (length(user_id::text) > 0);
```

#### RLS Policies for Resumes:
```sql
-- Drop inadequate service-only policy
DROP POLICY IF EXISTS "Service full access to resumes" ON public.resumes;

-- Create comprehensive user isolation policies
CREATE POLICY "Users can view own resumes" ON public.resumes
    FOR SELECT USING (auth.uid() = user_id AND deleted_at IS NULL);

CREATE POLICY "Users can insert own resumes" ON public.resumes
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own resumes" ON public.resumes
    FOR UPDATE USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own resumes" ON public.resumes
    FOR DELETE USING (auth.uid() = user_id);

-- Administrative access policy
CREATE POLICY "Service role full access" ON public.resumes
    FOR ALL USING (current_setting('app.current_user_id', true) IS NULL)
    WITH CHECK (current_setting('app.current_user_id', true) IS NULL);
```

### 2. Stripe Webhook Events Enhancement

#### Current Issues:
- Missing user_id for audit trail
- Cannot trace webhook events to specific users

#### Proposed Enhancement:
```sql
-- Add user_id column for audit trail
ALTER TABLE public.stripe_webhook_events
ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL;

-- Add index for performance
CREATE INDEX idx_stripe_webhook_events_user_id ON public.stripe_webhook_events(user_id);
CREATE INDEX idx_stripe_webhook_events_user_created ON public.stripe_webhook_events(user_id, created_at DESC);

-- Add validation constraint
ALTER TABLE public.stripe_webhook_events
ADD CONSTRAINT webhook_user_id_valid
CHECK (user_id IS NULL OR length(user_id::text) > 0);
```

### 3. Enhanced Audit Logging

#### Audit Trigger for Data Access:
```sql
-- Create audit logging function
CREATE OR REPLACE FUNCTION log_resume_access()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.resume_access_logs(
        resume_id,
        user_id,
        action_type,
        accessed_at,
        ip_address,
        user_agent
    ) VALUES (
        NEW.resume_id,
        auth.uid(),
        TG_OP,
        now(),
        current_setting('request.ip', true),
        current_setting('request.user_agent', true)
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create access logging table
CREATE TABLE IF NOT EXISTS public.resume_access_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL REFERENCES public.resumes(resume_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    action_type TEXT NOT NULL CHECK (action_type IN ('INSERT', 'UPDATE', 'SELECT', 'DELETE')),
    accessed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ip_address INET,
    user_agent TEXT
);

-- Enable RLS on audit logs
ALTER TABLE public.resume_access_logs ENABLE ROW LEVEL SECURITY;

-- RLS policies for audit logs
CREATE POLICY "Users can view own access logs" ON public.resume_access_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service role full access to audit logs" ON public.resume_access_logs
    FOR ALL USING (current_setting('app.current_user_id', true) IS NULL);

-- Add indexes for audit logs
CREATE INDEX idx_resume_access_logs_resume_id ON public.resume_access_logs(resume_id);
CREATE INDEX idx_resume_access_logs_user_id ON public.resume_access_logs(user_id);
CREATE INDEX idx_resume_access_logs_accessed_at ON public.resume_access_logs(accessed_at DESC);
```

### 4. Data Retention and Compliance

#### Automatic Data Cleanup (LGPD 5-year retention):
```sql
-- Create function for automatic data cleanup
CREATE OR REPLACE FUNCTION cleanup_expired_data()
RETURNS void AS $$
BEGIN
    -- Delete resumes older than 5 years (per LGPD)
    DELETE FROM public.resumes
    WHERE deleted_at IS NOT NULL
    AND deleted_at < now() - interval '5 years';

    -- Delete access logs older than 5 years
    DELETE FROM public.resume_access_logs
    WHERE accessed_at < now() - interval '5 years';

    -- Delete webhook events older than 5 years
    DELETE FROM public.stripe_webhook_events
    WHERE created_at < now() - interval '5 years';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Schedule cleanup job (runs daily)
-- Note: This would be configured via pg_cron or external scheduler
```

### 5. Enhanced Validation Constraints

#### Resume Content Validation:
```sql
-- Add additional validation constraints
ALTER TABLE public.resumes
ADD CONSTRAINT resume_content_size_limit
CHECK (length(content) <= 100000), -- 100KB limit per resume

ADD CONSTRAINT resume_content_type_valid
CHECK (content_type IN ('text/markdown', 'text/html', 'text/plain', 'application/pdf'));

ADD CONSTRAINT resume_id_format_valid
CHECK (resume_id ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'::text);
```

### 6. Performance Optimization

#### Additional Indexes for Performance:
```sql
-- Full-text search index for resume content
CREATE INDEX idx_resumes_content_fts ON public.resumes
USING gin(to_tsvector('portuguese', content))
WHERE deleted_at IS NULL;

-- Composite index for common queries
CREATE INDEX idx_resumes_user_type_created ON public.resumes
(user_id, content_type, created_at DESC)
WHERE deleted_at IS NULL;

-- Index for soft delete operations
CREATE INDEX idx_resumes_deleted_at_user ON public.resumes
(deleted_at, user_id)
WHERE deleted_at IS NOT NULL;
```

### 7. Security Monitoring

#### Security Metrics View:
```sql
-- Create view for security monitoring
CREATE OR REPLACE VIEW security_metrics AS
SELECT
    'resumes' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN deleted_at IS NULL THEN 1 END) as active_records,
    COUNT(CASE WHEN deleted_at IS NOT NULL THEN 1 END) as deleted_records,
    COUNT(DISTINCT user_id) as unique_users,
    MAX(created_at) as latest_activity,
    COUNT(CASE WHEN created_at > now() - interval '24 hours' THEN 1 END) as last_24h_activity
FROM public.resumes

UNION ALL

SELECT
    'resume_access_logs' as table_name,
    COUNT(*) as total_records,
    COUNT(*) as active_records,
    0 as deleted_records,
    COUNT(DISTINCT user_id) as unique_users,
    MAX(accessed_at) as latest_activity,
    COUNT(CASE WHEN accessed_at > now() - interval '24 hours' THEN 1 END) as last_24h_activity
FROM public.resume_access_logs;
```

## Migration Strategy

### Phase 1: Schema Foundation (30 minutes)
1. Add user_id column to resumes table
2. Create foreign key constraints
3. Add basic indexes
4. Add validation constraints

### Phase 2: Security Policies (30 minutes)
1. Drop inadequate RLS policies
2. Create comprehensive user isolation policies
3. Add administrative access policies
4. Test policy effectiveness

### Phase 3: Audit and Monitoring (30 minutes)
1. Create audit logging infrastructure
2. Add access logging triggers
3. Create security monitoring views
4. Set up data retention policies

### Phase 4: Performance Optimization (30 minutes)
1. Create additional indexes
2. Optimize query patterns
3. Test performance impact
4. Document performance characteristics

## Rollback Plan

### Rollback Procedures:
1. **Drop new indexes** - Reverse performance changes
2. **Remove audit logging** - Disable access logging
3. **Revert RLS policies** - Restore original policies (not recommended)
4. **Drop user_id column** - Only if absolutely necessary

### Rollback Scripts:
```sql
-- Emergency rollback script (use only if critical issues arise)
-- DROP INDEX IF EXISTS idx_resumes_user_id;
-- DROP INDEX IF EXISTS idx_resumes_user_created;
-- ALTER TABLE public.resumes DROP COLUMN IF EXISTS user_id;
-- Restore original RLS policies
```

## Testing Requirements

### Security Testing Checklist:
- [ ] Verify user A cannot access user B's resumes
- [ ] Test RLS policies with different user contexts
- [ ] Validate foreign key constraints prevent orphaned data
- [ ] Test administrative access controls
- [ ] Verify audit logging captures all access attempts
- [ ] Test data retention policies work correctly

### Performance Testing Checklist:
- [ ] Benchmark query performance with new indexes
- [ ] Test concurrent user access scenarios
- [ ] Verify no performance regression (>20% threshold)
- [ ] Test soft delete operations performance
- [ ] Validate full-text search performance

### Compliance Testing Checklist:
- [ ] Verify LGPD 5-year data retention
- [ ] Test right to erasure functionality
- [ ] Validate audit trail completeness
- [ ] Test data export capabilities
- [ ] Verify consent tracking works correctly

## Implementation Notes

### Important Considerations:
1. **Zero downtime**: The resumes table is currently empty (0 records)
2. **Backward compatibility**: All changes are additive
3. **Security first**: RLS policies are restrictive by default
4. **Performance**: Indexes optimized for common query patterns
5. **Compliance**: Full LGPD compliance built-in

### Dependencies:
1. Supabase CLI must be available
2. Database must be accessible for migrations
3. Application must handle new user_id requirements
4. Backend code must use proper authentication context

## Conclusion

This security schema design addresses all critical vulnerabilities identified in the database security analysis. The implementation ensures:

- ✅ Complete user data isolation
- ✅ LGPD compliance requirements
- ✅ Comprehensive audit logging
- ✅ Performance optimization
- ✅ Administrative controls
- ✅ Data retention policies

**Next Step**: Execute migration implementation with proper testing and validation.

---

**Design Status**: ✅ Complete
**Implementation Ready**: ✅ Yes
**Testing Required**: ✅ Yes
**Documentation Complete**: ✅ Yes