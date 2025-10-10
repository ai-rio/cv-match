-- =====================================================
-- CREATE RESUMES TABLE (LEGACY COMPATIBILITY)
-- =====================================================
-- This migration creates the resumes table for backward compatibility
-- with existing ResumeService during the migration from Resume-Matcher.
--
-- Created: 2025-10-10
-- Purpose: Backward compatibility during Resume-Matcher integration
-- =====================================================

-- =====================================================
-- CREATE RESUMES TABLE
-- =====================================================

-- Legacy table for storing resume content
CREATE TABLE IF NOT EXISTS public.resumes (
    id BIGSERIAL PRIMARY KEY,
    resume_id UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    content_type TEXT NOT NULL DEFAULT 'text/markdown',
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMPTZ DEFAULT NULL,

    -- Constraints
    CONSTRAINT resume_id_not_empty CHECK (length(resume_id::text) > 0),
    CONSTRAINT content_not_empty CHECK (length(trim(content)) > 0),
    CONSTRAINT valid_content_type CHECK (content_type IN ('text/markdown', 'text/html', 'text/plain'))
);

-- =====================================================
-- ENABLE ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE public.resumes ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- RLS POLICIES FOR RESUMES
-- =====================================================

-- Service role full access (backend uses service role)
CREATE POLICY "Service full access to resumes"
    ON public.resumes
    FOR ALL
    USING (current_setting('app.current_user_id', true) IS NULL);

-- =====================================================
-- INDEXES FOR RESUMES
-- =====================================================

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_resumes_resume_id ON public.resumes(resume_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_resumes_created_at ON public.resumes(created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_resumes_deleted_at ON public.resumes(deleted_at) WHERE deleted_at IS NOT NULL;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Create updated_at trigger function for legacy tables (if not exists)
CREATE OR REPLACE FUNCTION public.update_legacy_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- Apply trigger to resumes table
CREATE TRIGGER update_resumes_updated_at
    BEFORE UPDATE ON public.resumes
    FOR EACH ROW
    EXECUTE FUNCTION public.update_legacy_updated_at_column();

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE public.resumes IS 'Legacy table for backward compatibility during Resume-Matcher integration';
COMMENT ON COLUMN public.resumes.resume_id IS 'Unique identifier for resume content';
COMMENT ON COLUMN public.resumes.content_type IS 'Format of resume content: text/markdown, text/html, or text/plain';
COMMENT ON COLUMN public.resumes.deleted_at IS 'Soft delete timestamp for LGPD compliance';

-- =====================================================
-- GRANTS AND PERMISSIONS
-- =====================================================

-- Grant permissions to service role (backend will use service role key)
GRANT ALL ON public.resumes TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;

-- Grant usage on sequences for IDs
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO service_role;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Resumes Table Migration Complete';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Created resumes table for backward compatibility';
    RAISE NOTICE 'Purpose: Support Resume-Matcher service integration';
    RAISE NOTICE 'Added soft delete for LGPD compliance';
    RAISE NOTICE 'Service role access configured';
    RAISE NOTICE '=================================================';
END $$;