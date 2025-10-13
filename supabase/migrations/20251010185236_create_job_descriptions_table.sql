-- =====================================================
-- CREATE JOB DESCRIPTIONS TABLE
-- =====================================================
-- This migration creates the job_descriptions table for storing
-- job description information for resume optimization.
--
-- Created: 2025-10-10
-- Purpose: Store job descriptions for AI resume optimization
-- =====================================================

-- =====================================================
-- CREATE JOB DESCRIPTIONS TABLE
-- =====================================================

-- Table for storing job description information
CREATE TABLE IF NOT EXISTS public.job_descriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    description TEXT NOT NULL,
    location TEXT,
    salary_range TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMPTZ DEFAULT NULL,

    -- Constraints
    CONSTRAINT job_title_check CHECK (length(title) > 0 AND length(title) <= 255),
    CONSTRAINT job_company_check CHECK (length(company) > 0 AND length(company) <= 255),
    CONSTRAINT job_description_check CHECK (length(description) > 50 AND length(description) <= 10000),
    CONSTRAINT job_location_length CHECK (location IS NULL OR length(location) <= 255),
    CONSTRAINT job_salary_length CHECK (salary_range IS NULL OR length(salary_range) <= 255)
);

-- =====================================================
-- ENABLE ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE public.job_descriptions ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- RLS POLICIES FOR JOB DESCRIPTIONS
-- =====================================================

-- Users can view own job descriptions
CREATE POLICY "Users can view own job descriptions"
    ON public.job_descriptions
    FOR SELECT
    USING (auth.uid() = user_id AND deleted_at IS NULL);

-- Users can insert own job descriptions
CREATE POLICY "Users can insert own job descriptions"
    ON public.job_descriptions
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update own job descriptions
CREATE POLICY "Users can update own job descriptions"
    ON public.job_descriptions
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Users can delete own job descriptions
CREATE POLICY "Users can delete own job descriptions"
    ON public.job_descriptions
    FOR DELETE
    USING (auth.uid() = user_id);

-- =====================================================
-- INDEXES FOR JOB DESCRIPTIONS
-- =====================================================

-- Performance indexes
CREATE INDEX idx_job_descriptions_user_id ON public.job_descriptions(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_job_descriptions_created_at ON public.job_descriptions(created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_job_descriptions_deleted_at ON public.job_descriptions(deleted_at) WHERE deleted_at IS NOT NULL;

-- Full-text search index for job titles and descriptions
CREATE INDEX idx_job_descriptions_search
    ON public.job_descriptions
    USING gin(to_tsvector('portuguese', title || ' ' || description))
    WHERE deleted_at IS NULL;

-- Index for location-based searches
CREATE INDEX idx_job_descriptions_location ON public.job_descriptions(location) WHERE deleted_at IS NULL AND location IS NOT NULL;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger for updated_at column
CREATE TRIGGER update_job_descriptions_updated_at
    BEFORE UPDATE ON public.job_descriptions
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Public job descriptions view (non-sensitive data only)
CREATE OR REPLACE VIEW public.public_job_descriptions AS
SELECT
    jd.id,
    jd.title,
    jd.company,
    jd.location,
    jd.salary_range,
    LEFT(jd.description, 200) as description_preview,
    jd.created_at
FROM public.job_descriptions jd
WHERE jd.deleted_at IS NULL;

COMMENT ON VIEW public.public_job_descriptions IS 'Public view of job descriptions with non-sensitive data only';

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE public.job_descriptions IS 'Stores job descriptions for resume optimization';
COMMENT ON COLUMN public.job_descriptions.title IS 'Job title with max 255 characters';
COMMENT ON COLUMN public.job_descriptions.company IS 'Company name with max 255 characters';
COMMENT ON COLUMN public.job_descriptions.description IS 'Full job description (50-10000 characters)';
COMMENT ON COLUMN public.job_descriptions.location IS 'Job location (optional, max 255 characters)';
COMMENT ON COLUMN public.job_descriptions.salary_range IS 'Salary range information (optional)';
COMMENT ON COLUMN public.job_descriptions.deleted_at IS 'Soft delete timestamp for LGPD compliance';

-- =====================================================
-- GRANTS AND PERMISSIONS
-- =====================================================

-- Grant permissions to authenticated users
GRANT ALL ON public.job_descriptions TO authenticated;
GRANT SELECT ON public.public_job_descriptions TO authenticated, anon;

-- Grant permissions to service role
GRANT ALL ON public.job_descriptions TO service_role;
GRANT ALL ON public.public_job_descriptions TO service_role;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Job Descriptions Table Migration Complete';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Created job_descriptions table';
    RAISE NOTICE 'Added soft delete for LGPD compliance';
    RAISE NOTICE 'Created full-text search indexes';
    RAISE NOTICE 'Configured RLS policies for user isolation';
    RAISE NOTICE '=================================================';
END $$;
