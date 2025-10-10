-- =====================================================
-- CREATE OPTIMIZATIONS TABLE
-- =====================================================
-- Core table for storing AI-powered resume optimization results
-- Based on Resume-Matcher schema with cv-match enhancements
--
-- Created: 2025-10-10
-- Purpose: Store resume optimization records with payment tracking
-- =====================================================

-- =====================================================
-- CREATE ENUM TYPES
-- =====================================================

-- Optimization status lifecycle
CREATE TYPE optimization_status AS ENUM (
    'pending_payment',
    'payment_processing',
    'processing',
    'completed',
    'failed',
    'cancelled'
);

-- =====================================================
-- CREATE OPTIMIZATIONS TABLE
-- =====================================================

-- Resume optimization records
CREATE TABLE IF NOT EXISTS public.optimizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,

    -- Input data
    input_resume_filename TEXT NOT NULL,
    input_resume_storage_path TEXT,
    input_job_description TEXT NOT NULL,

    -- Output data
    output_optimized_resume TEXT,
    storage_path_docx TEXT,

    -- Metadata
    status optimization_status DEFAULT 'pending_payment' NOT NULL,
    stripe_payment_id TEXT,
    stripe_payment_status TEXT,
    processing_started_at TIMESTAMPTZ,
    processing_completed_at TIMESTAMPTZ,
    error_message TEXT,

    -- AI metadata
    ai_model_used TEXT,
    ai_tokens_used INTEGER,
    ai_processing_time_ms INTEGER,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMPTZ DEFAULT NULL,

    -- Constraints
    CONSTRAINT input_resume_filename_length CHECK (LENGTH(input_resume_filename) <= 255),
    CONSTRAINT input_job_description_length CHECK (LENGTH(input_job_description) BETWEEN 50 AND 10000),
    CONSTRAINT output_optimized_resume_length CHECK (output_optimized_resume IS NULL OR LENGTH(output_optimized_resume) <= 50000),
    CONSTRAINT stripe_payment_id_format CHECK (stripe_payment_id IS NULL OR stripe_payment_id ~ '^(pi_|cs_)[A-Za-z0-9]+$'),
    CONSTRAINT valid_processing_times CHECK (
        (processing_started_at IS NULL AND processing_completed_at IS NULL) OR
        (processing_completed_at IS NULL OR processing_completed_at >= processing_started_at)
    )
);

-- =====================================================
-- ENABLE ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE public.optimizations ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- RLS POLICIES FOR OPTIMIZATIONS
-- =====================================================

-- Users can view own optimizations
CREATE POLICY "Users can view own optimizations"
    ON public.optimizations
    FOR SELECT
    USING (auth.uid() = user_id AND deleted_at IS NULL);

-- Users can insert own optimizations
CREATE POLICY "Users can insert own optimizations"
    ON public.optimizations
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update own optimizations
CREATE POLICY "Users can update own optimizations"
    ON public.optimizations
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Users can soft delete own optimizations
CREATE POLICY "Users can soft delete own optimizations"
    ON public.optimizations
    FOR DELETE
    USING (auth.uid() = user_id);

-- =====================================================
-- INDEXES FOR OPTIMIZATIONS
-- =====================================================

-- Performance indexes
CREATE INDEX idx_optimizations_user_id ON public.optimizations(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_optimizations_stripe_payment_id ON public.optimizations(stripe_payment_id) WHERE stripe_payment_id IS NOT NULL;
CREATE INDEX idx_optimizations_status ON public.optimizations(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_optimizations_created_at ON public.optimizations(created_at DESC);
CREATE INDEX idx_optimizations_user_created ON public.optimizations(user_id, created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_optimizations_deleted_at ON public.optimizations(deleted_at) WHERE deleted_at IS NOT NULL;

-- Full-text search index for job descriptions
CREATE INDEX idx_optimizations_job_description_search
    ON public.optimizations
    USING gin(to_tsvector('portuguese', input_job_description))
    WHERE deleted_at IS NULL;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger for updated_at column
CREATE TRIGGER update_optimizations_updated_at
    BEFORE UPDATE ON public.optimizations
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- =====================================================
-- FUNCTIONS FOR SOFT DELETE
-- =====================================================

-- Function to soft delete optimizations (LGPD compliance)
CREATE OR REPLACE FUNCTION public.soft_delete_optimization()
RETURNS TRIGGER
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
BEGIN
    -- Instead of actually deleting, set deleted_at
    UPDATE public.optimizations
    SET deleted_at = NOW()
    WHERE id = OLD.id;

    -- Prevent actual deletion
    RETURN NULL;
END;
$$;

COMMENT ON FUNCTION public.soft_delete_optimization IS 'Implements soft delete for LGPD compliance instead of hard delete';

-- Trigger for soft delete on optimizations
CREATE TRIGGER soft_delete_optimization_trigger
    BEFORE DELETE ON public.optimizations
    FOR EACH ROW
    EXECUTE FUNCTION public.soft_delete_optimization();

-- =====================================================
-- VIEWS
-- =====================================================

-- View for optimization analytics
CREATE VIEW public.optimization_analytics AS
SELECT
    o.user_id,
    COUNT(*) as total_optimizations,
    COUNT(*) FILTER (WHERE o.status = 'completed') as completed_count,
    COUNT(*) FILTER (WHERE o.status = 'failed') as failed_count,
    COUNT(*) FILTER (WHERE o.status = 'processing') as processing_count,
    SUM(o.ai_tokens_used) as total_tokens_used,
    AVG(o.ai_processing_time_ms) as avg_processing_time_ms,
    MAX(o.created_at) as last_optimization_date,
    MIN(o.created_at) as first_optimization_date
FROM public.optimizations o
WHERE o.deleted_at IS NULL
GROUP BY o.user_id;

COMMENT ON VIEW public.optimization_analytics IS 'Aggregated optimization statistics per user';

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE public.optimizations IS 'Resume optimization records with payment tracking and AI metadata';
COMMENT ON COLUMN public.optimizations.status IS 'Current status of the optimization job';
COMMENT ON COLUMN public.optimizations.stripe_payment_id IS 'Stripe Payment Intent ID or Checkout Session ID';
COMMENT ON COLUMN public.optimizations.deleted_at IS 'Soft delete timestamp for LGPD compliance';
COMMENT ON COLUMN public.optimizations.ai_tokens_used IS 'Number of tokens consumed by AI model for cost tracking';

-- =====================================================
-- GRANTS AND PERMISSIONS
-- =====================================================

-- Grant permissions to authenticated users
GRANT ALL ON public.optimizations TO authenticated;
GRANT SELECT ON public.optimization_analytics TO authenticated;

-- Grant permissions to service role
GRANT ALL ON public.optimizations TO service_role;
GRANT ALL ON public.optimization_analytics TO service_role;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Optimizations Table Migration Complete';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Created optimizations table with payment tracking';
    RAISE NOTICE 'Added AI metadata fields for cost tracking';
    RAISE NOTICE 'Implemented soft delete for LGPD compliance';
    RAISE NOTICE 'Created analytics view for reporting';
    RAISE NOTICE '=================================================';
END $$;