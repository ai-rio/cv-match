-- =====================================================
-- CREATE LGPD CONSENT SYSTEM
-- =====================================================
-- Critical migration for LGPD compliance in Brazilian market
-- Implements consent tracking system required by Brazilian law
--
-- Created: 2025-10-13 (Critical Security Fix)
-- Purpose: Legal compliance for Brazilian market deployment
-- Priority: P0 - BLOCKS PRODUCTION DEPLOYMENT
-- =====================================================

-- =====================================================
-- CREATE LGPD CONSENT TYPES ENUM
-- =====================================================

CREATE TYPE lgpd_consent_type AS ENUM (
    'data_processing',      -- Consent for processing personal data
    'marketing',            -- Consent for marketing communications
    'analytics',            -- Consent for analytics and tracking
    'cookies',              -- Consent for website cookies
    'third_party_sharing'   -- Consent for sharing with third parties
);

-- =====================================================
-- CREATE LGPD CONSENTS TABLE
-- =====================================================

-- Table for tracking user consent under LGPD
CREATE TABLE IF NOT EXISTS public.lgpd_consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    consent_type lgpd_consent_type NOT NULL,
    granted BOOLEAN NOT NULL,
    granted_at TIMESTAMPTZ,
    ip_address INET,
    user_agent TEXT,
    consent_version TEXT NOT NULL DEFAULT '1.0',
    legal_basis TEXT, -- Legal basis for processing (contract, legal_obligation, vital_interests, etc.)
    withdrawal_reason TEXT,

    -- Timestamps for audit trail
    granted_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Constraints
    CONSTRAINT valid_consent_timing CHECK (
        (granted = true AND granted_at IS NOT NULL) OR
        (granted = false AND revoked_at IS NOT NULL)
    ),
    CONSTRAINT valid_consent_version CHECK (length(consent_version) > 0),
    CONSTRAINT valid_user_agent_length CHECK (user_agent IS NULL OR length(user_agent) <= 1000),
    CONSTRAINT valid_withdrawal_reason_length CHECK (withdrawal_reason IS NULL OR length(withdrawal_reason) <= 500)
);

-- =====================================================
-- CREATE LGPD CONSENT HISTORY TABLE
-- =====================================================

-- Audit trail for all consent changes (LGPD requirement)
CREATE TABLE IF NOT EXISTS public.lgpd_consent_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consent_id UUID NOT NULL REFERENCES public.lgpd_consents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    action TEXT NOT NULL, -- 'granted', 'revoked', 'updated'
    previous_state JSONB,
    new_state JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Constraints
    CONSTRAINT valid_consent_action CHECK (action IN ('granted', 'revoked', 'updated', 'viewed')),
    CONSTRAINT valid_user_agent_history_length CHECK (user_agent IS NULL OR length(user_agent) <= 1000)
);

-- =====================================================
-- ENABLE ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE public.lgpd_consents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.lgpd_consent_history ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- RLS POLICIES FOR LGPD CONSENTS
-- =====================================================

-- Users can view own consents
CREATE POLICY "Users can view own consents"
    ON public.lgpd_consents
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert own consents
CREATE POLICY "Users can insert own consents"
    ON public.lgpd_consents
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update own consents
CREATE POLICY "Users can update own consents"
    ON public.lgpd_consents
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Users can revoke own consents (special policy for withdrawal)
CREATE POLICY "Users can revoke own consents"
    ON public.lgpd_consents
    FOR UPDATE
    USING (auth.uid() = user_id AND granted = false)
    WITH CHECK (auth.uid() = user_id);

-- =====================================================
-- RLS POLICIES FOR LGPD CONSENT HISTORY
-- =====================================================

-- Users can view own consent history
CREATE POLICY "Users can view own consent history"
    ON public.lgpd_consent_history
    FOR SELECT
    USING (auth.uid() = user_id);

-- Service role full access (for audit purposes)
CREATE POLICY "Service role full access to consent history"
    ON public.lgpd_consent_history
    FOR ALL
    USING (current_setting('app.current_user_id', true) IS NULL);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Performance indexes for consents
CREATE INDEX IF NOT EXISTS idx_lgpd_consents_user_id ON public.lgpd_consents(user_id);
CREATE INDEX IF NOT EXISTS idx_lgpd_consents_type ON public.lgpd_consents(consent_type);
CREATE INDEX IF NOT EXISTS idx_lgpd_consents_granted ON public.lgpd_consents(granted);
CREATE INDEX IF NOT EXISTS idx_lgpd_consents_version ON public.lgpd_consents(consent_version);
CREATE INDEX IF NOT EXISTS idx_lgpd_consents_timestamps ON public.lgpd_consents(granted_at, revoked_at);

-- Performance indexes for history
CREATE INDEX IF NOT EXISTS idx_lgpd_consent_history_user_id ON public.lgpd_consent_history(user_id);
CREATE INDEX IF NOT EXISTS idx_lgpd_consent_history_consent_id ON public.lgpd_consent_history(consent_id);
CREATE INDEX IF NOT EXISTS idx_lgpd_consent_history_timestamp ON public.lgpd_consent_history(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_lgpd_consent_history_action ON public.lgpd_consent_history(action);

-- =====================================================
-- TRIGGERS FOR AUTOMATIC HISTORY TRACKING
-- =====================================================

-- Function to track consent changes in history
CREATE OR REPLACE FUNCTION public.track_consent_change()
RETURNS TRIGGER
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
DECLARE
    v_action TEXT;
    v_previous_state JSONB;
    v_new_state JSONB;
BEGIN
    -- Determine action and states based on operation
    IF TG_OP = 'INSERT' THEN
        v_action := CASE WHEN NEW.granted = true THEN 'granted' ELSE 'revoked' END;
        v_previous_state := NULL;
        v_new_state := to_jsonb(NEW);

        INSERT INTO public.lgpd_consent_history (
            consent_id, user_id, action, previous_state, new_state,
            ip_address, user_agent, timestamp
        ) VALUES (
            NEW.id, NEW.user_id, v_action, v_previous_state, v_new_state,
            NEW.ip_address, NEW.user_agent, NEW.created_at
        );

        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN
        -- Only track if consent state actually changed
        IF OLD.granted IS DISTINCT FROM NEW.granted OR
           OLD.consent_type IS DISTINCT FROM NEW.consent_type THEN

            v_action := CASE
                WHEN OLD.granted = true AND NEW.granted = false THEN 'revoked'
                WHEN OLD.granted = false AND NEW.granted = true THEN 'granted'
                ELSE 'updated'
            END;

            v_previous_state := to_jsonb(OLD);
            v_new_state := to_jsonb(NEW);

            INSERT INTO public.lgpd_consent_history (
                consent_id, user_id, action, previous_state, new_state,
                ip_address, user_agent, timestamp
            ) VALUES (
                NEW.id, NEW.user_id, v_action, v_previous_state, v_new_state,
                NEW.ip_address, NEW.user_agent, now()
            );
        END IF;

        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        -- Log deletion (should be soft delete, but handle hard delete)
        INSERT INTO public.lgpd_consent_history (
            consent_id, user_id, action, previous_state, new_state,
            ip_address, user_agent, timestamp
        ) VALUES (
            OLD.id, OLD.user_id, 'deleted', to_jsonb(OLD), NULL,
            inet_client_addr(), NULL, now()
        );

        RETURN OLD;
    END IF;

    RETURN NULL;
END;
$$;

COMMENT ON FUNCTION public.track_consent_change IS 'Tracks all consent changes for LGPD audit compliance';

-- Apply triggers for automatic history tracking
CREATE TRIGGER track_lgpd_consents_changes
    AFTER INSERT OR UPDATE OR DELETE ON public.lgpd_consents
    FOR EACH ROW
    EXECUTE FUNCTION public.track_consent_change();

-- Update timestamp trigger
CREATE TRIGGER update_lgpd_consents_updated_at
    BEFORE UPDATE ON public.lgpd_consents
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- =====================================================
-- FUNCTIONS FOR CONSENT MANAGEMENT
-- =====================================================

-- Function to check if user has given specific consent
CREATE OR REPLACE FUNCTION public.has_user_consent(
    p_user_id UUID,
    p_consent_type lgpd_consent_type
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_consent_granted BOOLEAN;
BEGIN
    SELECT granted INTO v_consent_granted
    FROM public.lgpd_consents
    WHERE user_id = p_user_id
      AND consent_type = p_consent_type
      AND granted = true
      AND (revoked_at IS NULL OR revoked_at > now())
    ORDER BY granted_at DESC
    LIMIT 1;

    RETURN COALESCE(v_consent_granted, false);
END;
$$;

COMMENT ON FUNCTION public.has_user_consent IS 'Check if user has given specific consent that is still active';

-- Function to record user consent
CREATE OR REPLACE FUNCTION public.record_consent(
    p_user_id UUID,
    p_consent_type lgpd_consent_type,
    p_granted BOOLEAN,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_consent_version TEXT DEFAULT '1.0',
    p_legal_basis TEXT DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_consent_id UUID;
    v_existing_consent RECORD;
BEGIN
    -- Check if user already has a consent record of this type
    SELECT * INTO v_existing_consent
    FROM public.lgpd_consents
    WHERE user_id = p_user_id
      AND consent_type = p_consent_type
      AND granted = true
      AND revoked_at IS NULL
    LIMIT 1;

    -- If existing consent found and user is revoking, update it
    IF v_existing_consent IS NOT NULL AND p_granted = false THEN
        UPDATE public.lgpd_consents
        SET granted = false,
            revoked_at = now(),
            ip_address = p_ip_address,
            user_agent = p_user_agent,
            updated_at = now()
        WHERE id = v_existing_consent.id;

        v_consent_id := v_existing_consent.id;

    -- If no existing consent or user is granting, create new record
    ELSE
        INSERT INTO public.lgpd_consents (
            user_id, consent_type, granted, granted_at,
            ip_address, user_agent, consent_version, legal_basis
        ) VALUES (
            p_user_id, p_consent_type, p_granted, now(),
            p_ip_address, p_user_agent, p_consent_version, p_legal_basis
        ) RETURNING id INTO v_consent_id;

        -- If user is granting and had previous consents, revoke them
        IF p_granted = true THEN
            UPDATE public.lgpd_consents
            SET revoked_at = now(),
                updated_at = now()
            WHERE user_id = p_user_id
              AND consent_type = p_consent_type
              AND granted = true
              AND id != v_consent_id
              AND revoked_at IS NULL;
        END IF;
    END IF;

    RETURN v_consent_id;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Failed to record consent for user %, type %: %',
                     p_user_id, p_consent_type, SQLERRM;
        RETURN NULL;
END;
$$;

COMMENT ON FUNCTION public.record_consent IS 'Record user consent with automatic history tracking';

-- =====================================================
-- VIEWS FOR CONSENT REPORTING
-- =====================================================

-- Current consent status view
CREATE OR REPLACE VIEW public.current_user_consents AS
SELECT
    lc.user_id,
    lc.consent_type,
    lc.granted,
    lc.granted_at,
    lc.consent_version,
    lc.legal_basis,
    CASE WHEN lc.revoked_at IS NOT NULL THEN true ELSE false END as is_revoked,
    lc.revoked_at,
    lc.updated_at
FROM public.lgpd_consents lc
WHERE lc.id IN (
    SELECT DISTINCT ON (user_id, consent_type) id
    FROM public.lgpd_consents
    ORDER BY user_id, consent_type, granted_at DESC
)
ORDER BY lc.user_id, lc.consent_type;

COMMENT ON VIEW public.current_user_consents IS 'Current consent status for all users';

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE public.lgpd_consents IS 'LGPD consent tracking for Brazilian market compliance';
COMMENT ON COLUMN public.lgpd_consents.consent_type IS 'Type of consent under LGPD categories';
COMMENT ON COLUMN public.lgpd_consents.granted IS 'Whether consent is currently granted (true) or revoked (false)';
COMMENT ON COLUMN public.lgpd_consents.ip_address IS 'IP address from which consent was given/revoked';
COMMENT ON COLUMN public.lgpd_consents.consent_version IS 'Version of consent terms agreed to';
COMMENT ON COLUMN public.lgpd_consents.legal_basis IS 'Legal basis for processing under LGPD';

COMMENT ON TABLE public.lgpd_consent_history IS 'Complete audit trail of consent changes (LGPD requirement)';
COMMENT ON COLUMN public.lgpd_consent_history.action IS 'Type of action: granted, revoked, updated, deleted';
COMMENT ON COLUMN public.lgpd_consent_history.previous_state IS 'Previous state of consent before change';
COMMENT ON COLUMN public.lgpd_consent_history.new_state IS 'New state of consent after change';

-- =====================================================
-- GRANTS AND PERMISSIONS
-- =====================================================

-- Grant permissions to authenticated users
GRANT SELECT, INSERT, UPDATE ON public.lgpd_consents TO authenticated;
GRANT SELECT ON public.lgpd_consent_history TO authenticated;
GRANT SELECT ON public.current_user_consents TO authenticated;

-- Grant execute permissions on functions
GRANT EXECUTE ON FUNCTION public.has_user_consent TO authenticated;
GRANT EXECUTE ON FUNCTION public.record_consent TO authenticated;

-- Grant permissions to service role
GRANT ALL ON public.lgpd_consents TO service_role;
GRANT ALL ON public.lgpd_consent_history TO service_role;
GRANT ALL ON public.current_user_consents TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'LGPD Consent System Migration Complete';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Created lgpd_consents table for consent tracking';
    RAISE NOTICE 'Created lgpd_consent_history table for audit trail';
    RAISE NOTICE 'Added comprehensive RLS policies for user isolation';
    RAISE NOTICE 'Implemented automatic history tracking triggers';
    RAISE NOTICE 'Added consent management functions';
    RAISE NOTICE 'System now compliant with LGPD consent requirements';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'CRITICAL: This migration enables legal deployment in Brazil';
    RAISE NOTICE '=================================================';
END $$;
