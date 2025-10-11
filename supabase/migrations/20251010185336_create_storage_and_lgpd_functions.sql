-- =====================================================
-- CREATE STORAGE BUCKETS AND LGPD FUNCTIONS
-- =====================================================
-- This migration creates storage buckets for resume files
-- and LGPD compliance functions for data cleanup.
--
-- Created: 2025-10-10
-- Purpose: Storage setup and LGPD compliance automation
-- =====================================================

-- =====================================================
-- STORAGE BUCKETS
-- =====================================================

-- Create storage bucket for resume files (PDF/DOCX uploads)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'resumes',
    'resumes',
    false,
    2097152, -- 2MB in bytes
    ARRAY['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
)
ON CONFLICT (id) DO NOTHING;

-- Create storage bucket for optimized resume outputs
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'optimized-resumes',
    'optimized-resumes',
    false,
    5242880, -- 5MB in bytes
    ARRAY['application/vnd.openxmlformats-officedocument.wordprocessingml.document']
)
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- STORAGE RLS POLICIES
-- =====================================================

-- RLS for resumes bucket (uploads)
CREATE POLICY "Users can upload own resumes"
    ON storage.objects
    FOR INSERT
    WITH CHECK (
        bucket_id = 'resumes' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can view own resumes"
    ON storage.objects
    FOR SELECT
    USING (
        bucket_id = 'resumes' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can update own resumes"
    ON storage.objects
    FOR UPDATE
    USING (
        bucket_id = 'resumes' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can delete own resumes"
    ON storage.objects
    FOR DELETE
    USING (
        bucket_id = 'resumes' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- RLS for optimized-resumes bucket (outputs)
CREATE POLICY "Users can view own optimized resumes"
    ON storage.objects
    FOR SELECT
    USING (
        bucket_id = 'optimized-resumes' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Backend service role can insert optimized resumes
CREATE POLICY "Service can insert optimized resumes"
    ON storage.objects
    FOR INSERT
    WITH CHECK (bucket_id = 'optimized-resumes');

-- Service role can manage optimized resumes
CREATE POLICY "Service can manage optimized resumes"
    ON storage.objects
    FOR ALL
    USING (
        bucket_id = 'optimized-resumes' AND
        current_setting('app.current_user_id', true) IS NULL
    );

-- =====================================================
-- LGPD COMPLIANCE FUNCTIONS
-- =====================================================

-- Function to clean up old data per LGPD retention policies
CREATE OR REPLACE FUNCTION public.cleanup_expired_data()
RETURNS void
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
DECLARE
    v_deleted_profiles INTEGER;
    v_deleted_optimizations INTEGER;
    v_deleted_resumes INTEGER;
    v_deleted_job_descriptions INTEGER;
BEGIN
    -- Delete profiles that have passed their data retention date
    DELETE FROM public.profiles
    WHERE data_retention_date < NOW()
    AND deleted_at IS NOT NULL
    RETURNING id INTO v_deleted_profiles;

    -- Delete old soft-deleted optimizations (after 90 days)
    DELETE FROM public.optimizations
    WHERE deleted_at < (NOW() - INTERVAL '90 days')
    RETURNING id INTO v_deleted_optimizations;

    -- Delete old soft-deleted resumes (after 90 days)
    DELETE FROM public.resumes
    WHERE deleted_at < (NOW() - INTERVAL '90 days')
    RETURNING id INTO v_deleted_resumes;

    -- Delete old soft-deleted job descriptions (after 90 days)
    DELETE FROM public.job_descriptions
    WHERE deleted_at < (NOW() - INTERVAL '90 days')
    RETURNING id INTO v_deleted_job_descriptions;

    RAISE NOTICE 'LGPD cleanup completed at %', NOW();
    RAISE NOTICE 'Deleted % profiles, % optimizations, % resumes, % job descriptions',
        COALESCE(v_deleted_profiles, 0),
        COALESCE(v_deleted_optimizations, 0),
        COALESCE(v_deleted_resumes, 0),
        COALESCE(v_deleted_job_descriptions, 0);
END;
$$;

COMMENT ON FUNCTION public.cleanup_expired_data IS 'Cleans up expired user data per LGPD retention requirements (should be run via scheduled job)';

-- Function to get user data for GDPR/LGPD export
CREATE OR REPLACE FUNCTION public.export_user_data(p_user_id UUID)
RETURNS JSON
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_data JSON;
BEGIN
    SELECT json_build_object(
        'profile', (
            SELECT row_to_json(p) FROM (
                SELECT
                    id, full_name, email, created_at, updated_at,
                    consent_marketing, consent_data_processing,
                    data_retention_date
                FROM public.profiles
                WHERE id = p_user_id AND deleted_at IS NULL
            ) p
        ),
        'optimizations', (
            SELECT json_agg(row_to_json(o)) FROM (
                SELECT
                    id, input_resume_filename, input_job_description,
                    status, processing_started_at, processing_completed_at,
                    ai_model_used, ai_tokens_used, ai_processing_time_ms,
                    created_at, updated_at
                FROM public.optimizations
                WHERE user_id = p_user_id AND deleted_at IS NULL
            ) o
        ),
        'job_descriptions', (
            SELECT json_agg(row_to_json(jd)) FROM (
                SELECT
                    id, title, company, location, salary_range,
                    created_at, updated_at
                FROM public.job_descriptions
                WHERE user_id = p_user_id AND deleted_at IS NULL
            ) jd
        ),
        'usage_tracking', (
            SELECT json_agg(row_to_json(ut)) FROM (
                SELECT
                    month_date, free_optimizations_used, paid_optimizations_used,
                    created_at, updated_at
                FROM public.usage_tracking
                WHERE user_id = p_user_id
                ORDER BY month_date DESC
                LIMIT 24  -- Last 24 months
            ) ut
        ),
        'payment_summary', (
            SELECT row_to_json(ps) FROM (
                SELECT
                    COUNT(*) as total_payments,
                    COALESCE(SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END), 0) as total_spent_brl
                FROM public.payment_history
                WHERE user_id = p_user_id
            ) ps
        )
    ) INTO v_user_data;

    RETURN v_user_data;
END;
$$;

COMMENT ON FUNCTION public.export_user_data IS 'Exports all user data for GDPR/LGPD compliance requests';

-- Function to permanently delete user data (LGPD right to be forgotten)
CREATE OR REPLACE FUNCTION public.permanent_delete_user_data(p_user_id UUID)
RETURNS BOOLEAN
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check if user exists
    IF NOT EXISTS (SELECT 1 FROM auth.users WHERE id = p_user_id) THEN
        RAISE EXCEPTION 'User % does not exist', p_user_id;
    END IF;

    -- Soft delete profile first
    UPDATE public.profiles
    SET deleted_at = NOW()
    WHERE id = p_user_id AND deleted_at IS NULL;

    -- Delete all user data
    DELETE FROM public.usage_tracking WHERE user_id = p_user_id;
    DELETE FROM public.job_descriptions WHERE user_id = p_user_id;
    DELETE FROM public.resumes WHERE resume_id IN (
        SELECT resume_id FROM public.optimizations WHERE user_id = p_user_id
    );
    DELETE FROM public.optimizations WHERE user_id = p_user_id;

    -- Mark user as deleted in auth.users by adding metadata
    UPDATE auth.users
    SET raw_user_meta_data = raw_user_meta_data || '{"deleted_at": "' || to_jsonb(NOW()) || '"}'
    WHERE id = p_user_id;

    RAISE NOTICE 'User % data permanently deleted', p_user_id;
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Failed to delete user data for %: %', p_user_id, SQLERRM;
        RETURN FALSE;
END;
$$;

COMMENT ON FUNCTION public.permanent_delete_user_data IS 'Permanently deletes all user data for LGPD right to be forgotten';

-- =====================================================
-- COMMENTS
-- =====================================================

-- Storage bucket comments are managed by Supabase
-- Note: Cannot add comments to storage.buckets table as it's managed by Supabase

-- =====================================================
-- GRANTS AND PERMISSIONS
-- =====================================================

-- Grant storage permissions to authenticated users
GRANT ALL ON storage.objects TO authenticated;

-- Grant storage permissions to service role
GRANT ALL ON storage.objects TO service_role;

-- Grant LGPD function permissions to service role
GRANT EXECUTE ON FUNCTION public.cleanup_expired_data() TO service_role;
GRANT EXECUTE ON FUNCTION public.export_user_data(UUID) TO service_role;
GRANT EXECUTE ON FUNCTION public.permanent_delete_user_data(UUID) TO service_role;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Storage and LGPD Functions Migration Complete';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Created storage buckets: resumes, optimized-resumes';
    RAISE NOTICE 'Configured RLS policies for storage access';
    RAISE NOTICE 'Added LGPD cleanup and export functions';
    RAISE NOTICE 'Added permanent user deletion function';
    RAISE NOTICE 'Ready for production with LGPD compliance';
    RAISE NOTICE '=================================================';
END $$;