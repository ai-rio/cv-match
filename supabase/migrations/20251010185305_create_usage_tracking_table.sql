-- =====================================================
-- CREATE USAGE TRACKING TABLE
-- =====================================================
-- This migration creates the usage_tracking table for tracking
-- monthly usage limits for freemium feature gating in Brazilian market.
--
-- Created: 2025-10-10
-- Purpose: Track monthly usage limits for free tier users
-- =====================================================

-- =====================================================
-- CREATE USAGE TRACKING TABLE
-- =====================================================

-- Table for tracking monthly usage per user
CREATE TABLE IF NOT EXISTS public.usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    month_date DATE NOT NULL,
    free_optimizations_used INTEGER DEFAULT 0,
    paid_optimizations_used INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    UNIQUE(user_id, month_date),

    -- Constraints
    CONSTRAINT usage_month_not_future CHECK (month_date <= DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month' - INTERVAL '1 day'),
    CONSTRAINT usage_month_not_too_old CHECK (month_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '2 years'),
    CONSTRAINT free_optimizations_non_negative CHECK (free_optimizations_used >= 0),
    CONSTRAINT paid_optimizations_non_negative CHECK (paid_optimizations_used >= 0)
);

-- =====================================================
-- ENABLE ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE public.usage_tracking ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- RLS POLICIES FOR USAGE TRACKING
-- =====================================================

-- Users can view own usage
CREATE POLICY "Users can view own usage"
    ON public.usage_tracking
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert own usage
CREATE POLICY "Users can insert own usage"
    ON public.usage_tracking
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update own usage
CREATE POLICY "Users can update own usage"
    ON public.usage_tracking
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- =====================================================
-- INDEXES FOR USAGE TRACKING
-- =====================================================

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_date ON public.usage_tracking(user_id, month_date);
CREATE INDEX IF NOT EXISTS idx_usage_tracking_month ON public.usage_tracking(month_date);
CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_id ON public.usage_tracking(user_id);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger for updated_at column
CREATE TRIGGER update_usage_tracking_updated_at
    BEFORE UPDATE ON public.usage_tracking
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- =====================================================
-- FUNCTIONS FOR USAGE MANAGEMENT
-- =====================================================

-- Function to get or create monthly usage record
CREATE OR REPLACE FUNCTION public.get_or_create_monthly_usage(
    p_user_id UUID,
    p_month_date DATE DEFAULT DATE_TRUNC('month', CURRENT_DATE)
)
RETURNS TABLE (
    id UUID,
    user_id UUID,
    month_date DATE,
    free_optimizations_used INTEGER,
    paid_optimizations_used INTEGER,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_usage_record RECORD;
BEGIN
    -- Try to find existing record
    SELECT * INTO v_usage_record
    FROM public.usage_tracking
    WHERE user_id = p_user_id AND month_date = p_month_date
    FOR UPDATE;

    -- If not found, create new record
    IF v_usage_record IS NULL THEN
        INSERT INTO public.usage_tracking (user_id, month_date)
        VALUES (p_user_id, p_month_date)
        RETURNING * INTO v_usage_record;
    END IF;

    -- Return the record
    RETURN QUERY SELECT * FROM public.usage_tracking WHERE id = v_usage_record.id;
END;
$$;

COMMENT ON FUNCTION public.get_or_create_monthly_usage IS 'Get existing or create new monthly usage record for user';

-- Function to increment usage counter
CREATE OR REPLACE FUNCTION public.increment_usage(
    p_user_id UUID,
    p_is_free BOOLEAN DEFAULT TRUE
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_month_date DATE := DATE_TRUNC('month', CURRENT_DATE);
    v_usage_record_id UUID;
BEGIN
    -- Get or create monthly usage record
    SELECT id INTO v_usage_record_id
    FROM public.get_or_create_monthly_usage(p_user_id, v_month_date)
    LIMIT 1;

    -- Increment appropriate counter
    IF p_is_free THEN
        UPDATE public.usage_tracking
        SET free_optimizations_used = free_optimizations_used + 1
        WHERE id = v_usage_record_id;
    ELSE
        UPDATE public.usage_tracking
        SET paid_optimizations_used = paid_optimizations_used + 1
        WHERE id = v_usage_record_id;
    END IF;

    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Failed to increment usage for user %: %', p_user_id, SQLERRM;
        RETURN FALSE;
END;
$$;

COMMENT ON FUNCTION public.increment_usage IS 'Increment usage counter for user (free or paid)';

-- =====================================================
-- VIEWS FOR USAGE ANALYTICS
-- =====================================================

-- Monthly usage summary view
CREATE OR REPLACE VIEW public.monthly_usage_summary AS
SELECT
    ut.user_id,
    p.full_name,
    p.email,
    ut.month_date,
    ut.free_optimizations_used,
    ut.paid_optimizations_used,
    ut.free_optimizations_used + ut.paid_optimizations_used as total_optimizations,
    ut.updated_at as last_activity
FROM public.usage_tracking ut
JOIN public.profiles p ON ut.user_id = p.id
WHERE p.deleted_at IS NULL
ORDER BY ut.month_date DESC, ut.user_id;

COMMENT ON VIEW public.monthly_usage_summary IS 'Monthly usage summary per user';

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE public.usage_tracking IS 'Tracks user actions for analytics and billing in Brazilian market';
COMMENT ON COLUMN public.usage_tracking.month_date IS 'Month for which usage is tracked (first day of month)';
COMMENT ON COLUMN public.usage_tracking.free_optimizations_used IS 'Number of free tier optimizations used this month';
COMMENT ON COLUMN public.usage_tracking.paid_optimizations_used IS 'Number of paid optimizations used this month';

-- =====================================================
-- GRANTS AND PERMISSIONS
-- =====================================================

-- Grant permissions to authenticated users
GRANT SELECT, INSERT, UPDATE ON public.usage_tracking TO authenticated;
GRANT SELECT ON public.monthly_usage_summary TO authenticated;

-- Grant permissions to service role
GRANT ALL ON public.usage_tracking TO service_role;
GRANT ALL ON public.monthly_usage_summary TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Usage Tracking Table Migration Complete';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Created usage_tracking table for freemium features';
    RAISE NOTICE 'Added functions for usage management';
    RAISE NOTICE 'Configured RLS policies for user isolation';
    RAISE NOTICE 'Created monthly usage summary view';
    RAISE NOTICE 'Ready for Brazilian market freemium model';
    RAISE NOTICE '=================================================';
END $$;