-- =====================================================
-- CREATE LGPD COMPLIANCE TABLES
-- =====================================================
-- This migration creates additional tables needed for the
-- comprehensive LGPD compliance system including data subject
-- rights requests and retention management.
--
-- Created: 2025-10-13
-- Purpose: LGPD Phase 0.3 - Critical security implementation
-- =====================================================

-- =====================================================
-- DATA SUBJECT RIGHTS REQUESTS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS public.data_subject_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    request_type VARCHAR(50) NOT NULL, -- 'access', 'correction', 'deletion', 'portability', 'information'
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'rejected', 'cancelled'
    request_data JSONB NOT NULL, -- Request-specific data
    response_data JSONB, -- Response data (masked)
    processing_notes TEXT,
    rejection_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    processed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ, -- For data access/export requests
    ip_address INET,
    user_agent TEXT,

    -- Constraints
    CONSTRAINT valid_request_type CHECK (request_type IN (
        'access', 'correction', 'deletion', 'portability', 'information', 'consent_withdrawal'
    )),
    CONSTRAINT valid_status CHECK (status IN (
        'pending', 'processing', 'completed', 'rejected', 'cancelled'
    ))
);

-- =====================================================
-- RETENTION POLICIES TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS public.retention_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_category VARCHAR(100) NOT NULL UNIQUE,
    retention_period VARCHAR(50) NOT NULL,
    retention_days INTEGER NOT NULL,
    legal_basis TEXT NOT NULL,
    deletion_method VARCHAR(50) NOT NULL DEFAULT 'soft_delete',
    requires_user_consent BOOLEAN DEFAULT FALSE,
    auto_cleanup BOOLEAN DEFAULT TRUE,
    exceptions TEXT[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Constraints
    CONSTRAINT positive_retention_days CHECK (retention_days > 0),
    CONSTRAINT valid_deletion_method CHECK (deletion_method IN (
        'soft_delete', 'permanent_delete', 'anonymize'
    ))
);

-- =====================================================
-- RETENTION TASKS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS public.retention_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_category VARCHAR(100) NOT NULL,
    scheduled_date TIMESTAMPTZ NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    retention_policy JSONB NOT NULL,
    records_processed INTEGER DEFAULT 0,
    records_deleted INTEGER DEFAULT 0,
    errors TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- Constraints
    CONSTRAINT valid_task_status CHECK (status IN (
        'pending', 'running', 'completed', 'failed'
    ))
);

-- =====================================================
-- RETENTION RESULTS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS public.retention_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES public.retention_tasks(id) ON DELETE CASCADE,
    data_category VARCHAR(100) NOT NULL,
    retention_policy VARCHAR(100) NOT NULL,
    records_scanned INTEGER NOT NULL DEFAULT 0,
    records_deleted INTEGER NOT NULL DEFAULT 0,
    records_retained INTEGER NOT NULL DEFAULT 0,
    errors_encountered INTEGER NOT NULL DEFAULT 0,
    duration_seconds NUMERIC(10,3),
    cleanup_date TIMESTAMPTZ NOT NULL,
    next_cleanup_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- =====================================================
-- INSERT DEFAULT RETENTION POLICIES
-- =====================================================

INSERT INTO public.retention_policies (
    data_category, retention_period, retention_days, legal_basis, deletion_method,
    requires_user_consent, auto_cleanup
) VALUES
(
    'user_profile',
    '5_years',
    1825,
    'LGPD Art. 15 - Standard retention period',
    'soft_delete',
    FALSE,
    TRUE
),
(
    'resume_data',
    '2_years',
    730,
    'User consent and service necessity',
    'soft_delete',
    TRUE,
    TRUE
),
(
    'job_descriptions',
    '1_year',
    365,
    'Service usage pattern',
    'soft_delete',
    FALSE,
    TRUE
),
(
    'optimization_results',
    '2_years',
    730,
    'Service delivery records',
    'soft_delete',
    TRUE,
    TRUE
),
(
    'usage_analytics',
    '1_year',
    365,
    'Legitimate interest for service improvement',
    'anonymize',
    FALSE,
    TRUE
),
(
    'consent_records',
    '7_years',
    2555,
    'Legal requirement for consent records',
    'permanent_delete',
    FALSE,
    FALSE
),
(
    'payment_records',
    '7_years',
    2555,
    'Tax and legal requirements',
    'permanent_delete',
    FALSE,
    FALSE
),
(
    'audit_logs',
    '2_years',
    730,
    'Security and compliance monitoring',
    'permanent_delete',
    FALSE,
    TRUE
)
ON CONFLICT (data_category) DO NOTHING;

-- =====================================================
-- INDEXES FOR NEW TABLES
-- =====================================================

-- Data subject requests indexes
CREATE INDEX idx_data_subject_requests_user_id ON public.data_subject_requests(user_id);
CREATE INDEX idx_data_subject_requests_type ON public.data_subject_requests(request_type);
CREATE INDEX idx_data_subject_requests_status ON public.data_subject_requests(status);
CREATE INDEX idx_data_subject_requests_created_at ON public.data_subject_requests(created_at);
CREATE INDEX idx_data_subject_requests_expires_at ON public.data_subject_requests(expires_at) WHERE expires_at IS NOT NULL;

-- Retention policies indexes
CREATE INDEX idx_retention_policies_category ON public.retention_policies(data_category);
CREATE INDEX idx_retention_policies_active ON public.retention_policies(is_active) WHERE is_active = TRUE;

-- Retention tasks indexes
CREATE INDEX idx_retention_tasks_category ON public.retention_tasks(data_category);
CREATE INDEX idx_retention_tasks_status ON public.retention_tasks(status);
CREATE INDEX idx_retention_tasks_scheduled ON public.retention_tasks(scheduled_date);
CREATE INDEX idx_retention_tasks_created_at ON public.retention_tasks(created_at);

-- Retention results indexes
CREATE INDEX idx_retention_results_task_id ON public.retention_results(task_id);
CREATE INDEX idx_retention_results_category ON public.retention_results(data_category);
CREATE INDEX idx_retention_results_cleanup_date ON public.retention_results(cleanup_date);

-- =====================================================
-- RLS POLICIES FOR NEW TABLES
-- =====================================================

-- Enable RLS on new tables
ALTER TABLE public.data_subject_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.retention_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.retention_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.retention_results ENABLE ROW LEVEL SECURITY;

-- Data subject requests - users can view their own requests
CREATE POLICY "Users can view own data subject requests"
    ON public.data_subject_requests
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create own data subject requests"
    ON public.data_subject_requests
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Retention policies - read only for authenticated users
CREATE POLICY "Authenticated users can view retention policies"
    ON public.retention_policies
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Retention tasks and results - read only for authenticated users
CREATE POLICY "Authenticated users can view retention tasks"
    ON public.retention_tasks
    FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can view retention results"
    ON public.retention_results
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- =====================================================
-- UPDATED TRIGGERS
-- =====================================================

-- Updated at trigger for retention_policies
CREATE OR REPLACE FUNCTION public.update_retention_policies_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER update_retention_policies_updated_at
    BEFORE UPDATE ON public.retention_policies
    FOR EACH ROW
    EXECUTE FUNCTION public.update_retention_policies_updated_at();

-- =====================================================
-- GRANTS
-- =====================================================

-- Grant permissions to authenticated users
GRANT SELECT ON public.data_subject_requests TO authenticated;
GRANT INSERT ON public.data_subject_requests TO authenticated;
GRANT SELECT ON public.retention_policies TO authenticated;
GRANT SELECT ON public.retention_tasks TO authenticated;
GRANT SELECT ON public.retention_results TO authenticated;

-- Grant all permissions to service role
GRANT ALL ON public.data_subject_requests TO service_role;
GRANT ALL ON public.retention_policies TO service_role;
GRANT ALL ON public.retention_tasks TO service_role;
GRANT ALL ON public.retention_results TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE public.data_subject_requests IS 'User requests for data subject rights under LGPD';
COMMENT ON TABLE public.retention_policies IS 'Data retention policies for LGPD compliance';
COMMENT ON TABLE public.retention_tasks IS 'Scheduled tasks for data retention cleanup';
COMMENT ON TABLE public.retention_results IS 'Results of retention cleanup operations';

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'LGPD Compliance Tables Migration Complete';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Created data subject rights request tables';
    RAISE NOTICE 'Added retention policy management tables';
    RAISE NOTICE 'Configured RLS policies for privacy protection';
    RAISE NOTICE 'Inserted default retention policies';
    RAISE NOTICE 'Ready for complete LGPD compliance system';
    RAISE NOTICE '=================================================';
END $$;
