-- =====================================================
-- CREATE LGPD CONSENT MANAGEMENT SYSTEM
-- =====================================================
-- This migration creates a comprehensive consent management system
-- for LGPD compliance with Brazilian market requirements.
--
-- Created: 2025-10-13
-- Purpose: LGPD Phase 0.3 - Critical security implementation
-- =====================================================

-- =====================================================
-- CONSENT MANAGEMENT TABLES
-- =====================================================

-- Consent types and definitions
CREATE TABLE IF NOT EXISTS public.consent_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL, -- 'data_processing', 'marketing', 'analytics', etc.
    is_required BOOLEAN DEFAULT FALSE,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- User consent records
CREATE TABLE IF NOT EXISTS public.user_consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    consent_type_id UUID NOT NULL REFERENCES public.consent_types(id) ON DELETE CASCADE,
    granted BOOLEAN NOT NULL,
    granted_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    revoked_at TIMESTAMPTZ DEFAULT NULL,
    ip_address INET,
    user_agent TEXT,
    consent_version INTEGER NOT NULL,
    legal_basis TEXT, -- 'consent', 'contract', 'legal_obligation', 'vital_interests', 'public_task', 'legitimate_interests'
    purpose TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Constraints
    CONSTRAINT valid_dates CHECK (revoked_at IS NULL OR revoked_at > granted_at),
    CONSTRAINT consent_version_positive CHECK (consent_version > 0),

    -- Unique constraint to prevent duplicate active consents
    UNIQUE(user_id, consent_type_id, granted_at)
);

-- Consent history for audit trail
CREATE TABLE IF NOT EXISTS public.consent_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_consent_id UUID NOT NULL REFERENCES public.user_consents(id) ON DELETE CASCADE,
    action VARCHAR(20) NOT NULL, -- 'granted', 'revoked', 'updated'
    previous_value BOOLEAN,
    new_value BOOLEAN NOT NULL,
    changed_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    changed_by UUID REFERENCES auth.users(id), -- User who made the change or admin
    ip_address INET,
    user_agent TEXT,
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Data processing activities
CREATE TABLE IF NOT EXISTS public.data_processing_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    purpose TEXT NOT NULL,
    legal_basis VARCHAR(100) NOT NULL,
    data_categories TEXT[], -- Array of data types processed
    retention_period_months INTEGER NOT NULL,
    third_party_sharing BOOLEAN DEFAULT FALSE,
    third_party_details TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- User data processing records
CREATE TABLE IF NOT EXISTS public.user_data_processing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    activity_id UUID NOT NULL REFERENCES public.data_processing_activities(id) ON DELETE CASCADE,
    consent_id UUID REFERENCES public.user_consents(id) ON DELETE SET NULL,
    processed_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    data_type VARCHAR(100) NOT NULL,
    purpose TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- =====================================================
-- INSERT DEFAULT CONSENT TYPES
-- =====================================================

INSERT INTO public.consent_types (name, description, category, is_required, version) VALUES
(
    'data_processing',
    'Consent for processing personal data for resume optimization services',
    'data_processing',
    TRUE,
    1
),
(
    'marketing',
    'Consent for receiving marketing communications and promotional materials',
    'marketing',
    FALSE,
    1
),
(
    'analytics',
    'Consent for usage analytics and service improvement',
    'analytics',
    FALSE,
    1
),
(
    'cookies',
    'Consent for using cookies and similar technologies',
    'technical',
    TRUE,
    1
),
(
    'data_sharing',
    'Consent for sharing data with trusted third-party services',
    'data_sharing',
    FALSE,
    1
),
(
    'ai_processing',
    'Consent for AI-powered resume analysis and improvement',
    'ai_processing',
    TRUE,
    1
)
ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- INSERT DEFAULT DATA PROCESSING ACTIVITIES
-- =====================================================

INSERT INTO public.data_processing_activities (name, description, purpose, legal_basis, data_categories, retention_period_months) VALUES
(
    'Resume Analysis',
    'Analysis of uploaded resumes for job matching and optimization',
    'Provide resume optimization and job matching services',
    'consent',
    ARRAY['personal_data', 'professional_data', 'contact_data'],
    60
),
(
    'User Account Management',
    'Management of user accounts and profiles',
    'Maintain user accounts and provide personalized services',
    'contract',
    ARRAY['personal_data', 'contact_data', 'account_data'],
    60
),
(
    'Service Analytics',
    'Analysis of service usage for improvement purposes',
    'Improve service quality and user experience',
    'legitimate_interests',
    ARRAY['usage_data', 'technical_data'],
    36
),
(
    'Marketing Communications',
    'Sending promotional materials and service updates',
    'Marketing and communication about services',
    'consent',
    ARRAY['contact_data', 'preferences_data'],
    24
)
ON CONFLICT DO NOTHING;

-- =====================================================
-- INDEXES
-- =====================================================

-- Consent indexes
CREATE INDEX idx_user_consents_user_id ON public.user_consents(user_id);
CREATE INDEX idx_user_consents_consent_type ON public.user_consents(consent_type_id);
CREATE INDEX idx_user_consents_granted_at ON public.user_consents(granted_at);
CREATE INDEX idx_user_consents_active ON public.user_consents(user_id, consent_type_id) WHERE revoked_at IS NULL;

-- Consent history indexes
CREATE INDEX idx_consent_history_consent_id ON public.consent_history(user_consent_id);
CREATE INDEX idx_consent_history_action ON public.consent_history(action);
CREATE INDEX idx_consent_history_changed_at ON public.consent_history(changed_at);

-- Data processing indexes
CREATE INDEX idx_user_data_processing_user_id ON public.user_data_processing(user_id);
CREATE INDEX idx_user_data_processing_activity_id ON public.user_data_processing(activity_id);
CREATE INDEX idx_user_data_processing_processed_at ON public.user_data_processing(processed_at);

-- =====================================================
-- FUNCTIONS FOR CONSENT MANAGEMENT
-- =====================================================

-- Function to record user consent
CREATE OR REPLACE FUNCTION public.record_user_consent(
    p_user_id UUID,
    p_consent_type_name VARCHAR(100),
    p_granted BOOLEAN,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_legal_basis TEXT DEFAULT 'consent',
    p_purpose TEXT DEFAULT NULL
)
RETURNS UUID
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
DECLARE
    v_consent_type_id UUID;
    v_consent_version INTEGER;
    v_user_consent_id UUID;
    v_existing_consent_id UUID;
BEGIN
    -- Get consent type and version
    SELECT id, version INTO v_consent_type_id, v_consent_version
    FROM public.consent_types
    WHERE name = p_consent_type_name AND is_active = TRUE;

    IF v_consent_type_id IS NULL THEN
        RAISE EXCEPTION 'Consent type % does not exist or is not active', p_consent_type_name;
    END IF;

    -- Check for existing active consent
    SELECT id INTO v_existing_consent_id
    FROM public.user_consents
    WHERE user_id = p_user_id
    AND consent_type_id = v_consent_type_id
    AND revoked_at IS NULL;

    -- Revoke existing consent if it exists
    IF v_existing_consent_id IS NOT NULL THEN
        UPDATE public.user_consents
        SET revoked_at = NOW(),
            updated_at = NOW()
        WHERE id = v_existing_consent_id;

        -- Record in history
        INSERT INTO public.consent_history (
            user_consent_id, action, previous_value, new_value, changed_by,
            ip_address, user_agent, reason
        ) VALUES (
            v_existing_consent_id, 'revoked', TRUE, FALSE, p_user_id,
            p_ip_address, p_user_agent, 'New consent provided'
        );
    END IF;

    -- Create new consent record if granted
    IF p_granted THEN
        INSERT INTO public.user_consents (
            user_id, consent_type_id, granted, granted_at, ip_address,
            user_agent, consent_version, legal_basis, purpose
        ) VALUES (
            p_user_id, v_consent_type_id, p_granted, NOW(), p_ip_address,
            p_user_agent, v_consent_version, p_legal_basis, p_purpose
        ) RETURNING id INTO v_user_consent_id;

        -- Record in history
        INSERT INTO public.consent_history (
            user_consent_id, action, new_value, changed_by,
            ip_address, user_agent, reason
        ) VALUES (
            v_user_consent_id, 'granted', p_granted, p_user_id,
            p_ip_address, p_user_agent, p_purpose
        );

        RETURN v_user_consent_id;
    END IF;

    RETURN NULL;
END;
$$;

-- Function to check if user has valid consent
CREATE OR REPLACE FUNCTION public.has_valid_consent(
    p_user_id UUID,
    p_consent_type_name VARCHAR(100)
)
RETURNS BOOLEAN
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
DECLARE
    v_has_consent BOOLEAN := FALSE;
BEGIN
    SELECT EXISTS(
        SELECT 1 FROM public.user_consents uc
        JOIN public.consent_types ct ON uc.consent_type_id = ct.id
        WHERE uc.user_id = p_user_id
        AND ct.name = p_consent_type_name
        AND uc.granted = TRUE
        AND uc.revoked_at IS NULL
        AND ct.is_active = TRUE
    ) INTO v_has_consent;

    RETURN v_has_consent;
END;
$$;

-- Function to get all user consents
CREATE OR REPLACE FUNCTION public.get_user_consents(p_user_id UUID)
RETURNS TABLE(
    consent_name VARCHAR(100),
    consent_description TEXT,
    category VARCHAR(50),
    granted BOOLEAN,
    granted_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ,
    is_required BOOLEAN,
    legal_basis TEXT
)
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        ct.name,
        ct.description,
        ct.category,
        uc.granted,
        uc.granted_at,
        uc.revoked_at,
        ct.is_required,
        uc.legal_basis
    FROM public.user_consents uc
    JOIN public.consent_types ct ON uc.consent_type_id = ct.id
    WHERE uc.user_id = p_user_id
    ORDER BY ct.is_required DESC, ct.name;
END;
$$;

-- Function to check if user has all required consents
CREATE OR REPLACE FUNCTION public.has_all_required_consents(p_user_id UUID)
RETURNS BOOLEAN
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
DECLARE
    v_required_count INTEGER;
    v_granted_count INTEGER;
BEGIN
    -- Count required consent types
    SELECT COUNT(*) INTO v_required_count
    FROM public.consent_types
    WHERE is_required = TRUE AND is_active = TRUE;

    -- Count granted required consents
    SELECT COUNT(*) INTO v_granted_count
    FROM public.user_consents uc
    JOIN public.consent_types ct ON uc.consent_type_id = ct.id
    WHERE uc.user_id = p_user_id
    AND ct.is_required = TRUE
    AND uc.granted = TRUE
    AND uc.revoked_at IS NULL
    AND ct.is_active = TRUE;

    RETURN v_required_count = v_granted_count;
END;
$$;

-- =====================================================
-- TRIGGERS FOR UPDATED_AT
-- =====================================================

-- Updated at trigger for consent_types
CREATE OR REPLACE FUNCTION public.update_consent_types_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER update_consent_types_updated_at
    BEFORE UPDATE ON public.consent_types
    FOR EACH ROW
    EXECUTE FUNCTION public.update_consent_types_updated_at();

-- Updated at trigger for user_consents
CREATE OR REPLACE FUNCTION public.update_user_consents_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER update_user_consents_updated_at
    BEFORE UPDATE ON public.user_consents
    FOR EACH ROW
    EXECUTE FUNCTION public.update_user_consents_updated_at();

-- Updated at trigger for data_processing_activities
CREATE OR REPLACE FUNCTION public.update_data_processing_activities_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER update_data_processing_activities_updated_at
    BEFORE UPDATE ON public.data_processing_activities
    FOR EACH ROW
    EXECUTE FUNCTION public.update_data_processing_activities_updated_at();

-- =====================================================
-- RLS POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE public.consent_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_consents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.consent_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.data_processing_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_data_processing ENABLE ROW LEVEL SECURITY;

-- Consent types - read only for authenticated users
CREATE POLICY "Authenticated users can view consent types"
    ON public.consent_types
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- User consents - users can manage their own consents
CREATE POLICY "Users can view own consents"
    ON public.user_consents
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own consents"
    ON public.user_consents
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own consents"
    ON public.user_consents
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Consent history - users can view their own consent history
CREATE POLICY "Users can view own consent history"
    ON public.consent_history
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.user_consents uc
            WHERE uc.id = user_consent_id AND uc.user_id = auth.uid()
        )
    );

-- Data processing activities - read only for authenticated users
CREATE POLICY "Authenticated users can view data processing activities"
    ON public.data_processing_activities
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- User data processing - users can view their own data processing records
CREATE POLICY "Users can view own data processing"
    ON public.user_data_processing
    FOR SELECT
    USING (auth.uid() = user_id);

-- =====================================================
-- GRANTS
-- =====================================================

-- Grant permissions to authenticated users
GRANT SELECT, INSERT, UPDATE ON public.user_consents TO authenticated;
GRANT SELECT ON public.consent_history TO authenticated;
GRANT SELECT ON public.consent_types TO authenticated;
GRANT SELECT ON public.data_processing_activities TO authenticated;
GRANT SELECT ON public.user_data_processing TO authenticated;

-- Grant execute permissions for functions
GRANT EXECUTE ON FUNCTION public.record_user_consent TO authenticated;
GRANT EXECUTE ON FUNCTION public.has_valid_consent TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_user_consents TO authenticated;
GRANT EXECUTE ON FUNCTION public.has_all_required_consents TO authenticated;

-- Grant all permissions to service role
GRANT ALL ON public.consent_types TO service_role;
GRANT ALL ON public.user_consents TO service_role;
GRANT ALL ON public.consent_history TO service_role;
GRANT ALL ON public.data_processing_activities TO service_role;
GRANT ALL ON public.user_data_processing TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE public.consent_types IS 'Types of consents available for users to grant';
COMMENT ON TABLE public.user_consents IS 'User consent records with timestamps and audit trail';
COMMENT ON TABLE public.consent_history IS 'History of all consent changes for audit purposes';
COMMENT ON TABLE public.data_processing_activities IS 'Activities that process user data';
COMMENT ON TABLE public.user_data_processing IS 'Records of data processing activities for each user';

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'LGPD Consent Management System Migration Complete';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Created consent management tables with audit trail';
    RAISE NOTICE 'Added 6 default consent types for Brazilian market';
    RAISE NOTICE 'Added data processing activity tracking';
    RAISE NOTICE 'Implemented RLS policies for user privacy';
    RAISE NOTICE 'Ready for LGPD compliance implementation';
    RAISE NOTICE '=================================================';
END $$;
