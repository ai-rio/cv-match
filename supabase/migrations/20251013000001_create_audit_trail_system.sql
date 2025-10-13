-- =====================================================
-- CREATE AUDIT TRAIL SYSTEM FOR LGPD COMPLIANCE
-- =====================================================
-- This migration creates a comprehensive audit trail system
-- to track all data access and modifications for LGPD compliance.
--
-- Created: 2025-10-13
-- Purpose: LGPD Phase 0.3 - Critical security implementation
-- =====================================================

-- =====================================================
-- AUDIT TRAIL TABLES
-- =====================================================

-- Main audit log table
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL, -- 'create', 'read', 'update', 'delete', 'login', 'consent', etc.
    table_name VARCHAR(100), -- Table that was accessed
    record_id UUID, -- ID of the record that was accessed
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    user_email TEXT, -- Email for auditing even if user is deleted
    session_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    action VARCHAR(100) NOT NULL, -- Specific action performed
    details JSONB, -- Additional details (without PII)
    old_values JSONB, -- Previous values (for updates)
    new_values JSONB, -- New values (for updates)
    affected_fields TEXT[], -- List of fields that were changed
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Constraints
    CONSTRAINT valid_event_type CHECK (event_type IN (
        'create', 'read', 'update', 'delete', 'login', 'logout',
        'consent_granted', 'consent_revoked', 'data_access',
        'data_export', 'data_deletion', 'admin_action'
    ))
);

-- Data access log (for compliance tracking)
CREATE TABLE IF NOT EXISTS public.data_access_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    data_category VARCHAR(100) NOT NULL, -- 'profile', 'resumes', 'optimizations', etc.
    access_type VARCHAR(50) NOT NULL, -- 'view', 'export', 'download', 'modify'
    access_purpose TEXT, -- Purpose of data access
    record_count INTEGER DEFAULT 1, -- Number of records accessed
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    consent_verified BOOLEAN DEFAULT FALSE,
    legal_basis VARCHAR(100), -- 'consent', 'contract', 'legal_obligation', etc.
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- System event log (for security monitoring)
CREATE TABLE IF NOT EXISTS public.system_event_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL, -- 'security_alert', 'system_error', 'policy_violation'
    severity VARCHAR(20) NOT NULL, -- 'low', 'medium', 'high', 'critical'
    source VARCHAR(100), -- Service or component that generated the event
    description TEXT NOT NULL,
    details JSONB, -- Additional event details
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    ip_address INET,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    resolved_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Constraints
    CONSTRAINT valid_severity CHECK (severity IN ('low', 'medium', 'high', 'critical'))
);

-- Compliance monitoring log
CREATE TABLE IF NOT EXISTS public.compliance_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    compliance_type VARCHAR(100) NOT NULL, -- 'lgpd', 'data_retention', 'consent_management'
    check_type VARCHAR(100) NOT NULL, -- 'data_access', 'retention_policy', 'consent_validation'
    status VARCHAR(20) NOT NULL, -- 'compliant', 'non_compliant', 'warning'
    details JSONB, -- Compliance check details
    affected_records INTEGER DEFAULT 0, -- Number of records affected
    required_action TEXT, -- Action required to achieve compliance
    due_date TIMESTAMPTZ, -- When action must be completed
    completed_at TIMESTAMPTZ, -- When action was completed
    completed_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Constraints
    CONSTRAINT valid_compliance_status CHECK (status IN ('compliant', 'non_compliant', 'warning')),
    CONSTRAINT valid_check_type CHECK (check_type IN (
        'data_access', 'retention_policy', 'consent_validation',
        'pii_detection', 'data_subject_rights'
    ))
);

-- =====================================================
-- INDEXES FOR AUDIT TRAILS
-- =====================================================

-- Audit logs indexes
CREATE INDEX idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX idx_audit_logs_table_name ON public.audit_logs(table_name);
CREATE INDEX idx_audit_logs_event_type ON public.audit_logs(event_type);
CREATE INDEX idx_audit_logs_created_at ON public.audit_logs(created_at);
CREATE INDEX idx_audit_logs_ip_address ON public.audit_logs(ip_address);
CREATE INDEX idx_audit_logs_success ON public.audit_logs(success) WHERE success = FALSE;
CREATE INDEX idx_audit_logs_composite ON public.audit_logs(user_id, created_at, event_type);

-- Data access logs indexes
CREATE INDEX idx_data_access_logs_user_id ON public.data_access_logs(user_id);
CREATE INDEX idx_data_access_logs_category ON public.data_access_logs(data_category);
CREATE INDEX idx_data_access_logs_access_type ON public.data_access_logs(access_type);
CREATE INDEX idx_data_access_logs_created_at ON public.data_access_logs(created_at);
CREATE INDEX idx_data_access_logs_composite ON public.data_access_logs(user_id, data_category, created_at);

-- System event logs indexes
CREATE INDEX idx_system_event_logs_type ON public.system_event_logs(event_type);
CREATE INDEX idx_system_event_logs_severity ON public.system_event_logs(severity);
CREATE INDEX idx_system_event_logs_created_at ON public.system_event_logs(created_at);
CREATE INDEX idx_system_event_logs_resolved ON public.system_event_logs(resolved) WHERE resolved = FALSE;

-- Compliance logs indexes
CREATE INDEX idx_compliance_logs_type ON public.compliance_logs(compliance_type);
CREATE INDEX idx_compliance_logs_status ON public.compliance_logs(status);
CREATE INDEX idx_compliance_logs_created_at ON public.compliance_logs(created_at);
CREATE INDEX idx_compliance_logs_due_date ON public.compliance_logs(due_date) WHERE due_date IS NOT NULL;

-- =====================================================
-- AUDIT FUNCTIONS
-- =====================================================

-- Function to log data access
CREATE OR REPLACE FUNCTION public.log_data_access(
    p_user_id UUID,
    p_data_category VARCHAR(100),
    p_access_type VARCHAR(50),
    p_access_purpose TEXT DEFAULT NULL,
    p_record_count INTEGER DEFAULT 1,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_session_id VARCHAR(255) DEFAULT NULL,
    p_consent_verified BOOLEAN DEFAULT FALSE,
    p_legal_basis VARCHAR(100) DEFAULT NULL
)
RETURNS UUID
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
DECLARE
    v_log_id UUID;
BEGIN
    INSERT INTO public.data_access_logs (
        user_id, data_category, access_type, access_purpose, record_count,
        ip_address, user_agent, session_id, consent_verified, legal_basis
    ) VALUES (
        p_user_id, p_data_category, p_access_type, p_access_purpose, p_record_count,
        p_ip_address, p_user_agent, p_session_id, p_consent_verified, p_legal_basis
    ) RETURNING id INTO v_log_id;

    RETURN v_log_id;
END;
$$;

-- Function to log audit events
CREATE OR REPLACE FUNCTION public.log_audit_event(
    p_event_type VARCHAR(50),
    p_table_name VARCHAR(100) DEFAULT NULL,
    p_record_id UUID DEFAULT NULL,
    p_user_id UUID DEFAULT NULL,
    p_user_email TEXT DEFAULT NULL,
    p_action VARCHAR(100) NOT NULL,
    p_details JSONB DEFAULT NULL,
    p_old_values JSONB DEFAULT NULL,
    p_new_values JSONB DEFAULT NULL,
    p_affected_fields TEXT[] DEFAULT NULL,
    p_success BOOLEAN DEFAULT TRUE,
    p_error_message TEXT DEFAULT NULL,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_session_id VARCHAR(255) DEFAULT NULL
)
RETURNS UUID
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
DECLARE
    v_log_id UUID;
BEGIN
    -- Get user email if not provided
    IF p_user_email IS NULL AND p_user_id IS NOT NULL THEN
        SELECT email INTO p_user_email
        FROM public.profiles
        WHERE id = p_user_id;
    END IF;

    INSERT INTO public.audit_logs (
        event_type, table_name, record_id, user_id, user_email, session_id,
        ip_address, user_agent, action, details, old_values, new_values,
        affected_fields, success, error_message
    ) VALUES (
        p_event_type, p_table_name, p_record_id, p_user_id, p_user_email, p_session_id,
        p_ip_address, p_user_agent, p_action, p_details, p_old_values, p_new_values,
        p_affected_fields, p_success, p_error_message
    ) RETURNING id INTO v_log_id;

    RETURN v_log_id;
END;
$$;

-- Function to log compliance events
CREATE OR REPLACE FUNCTION public.log_compliance_event(
    p_compliance_type VARCHAR(100),
    p_check_type VARCHAR(100),
    p_status VARCHAR(20),
    p_details JSONB DEFAULT NULL,
    p_affected_records INTEGER DEFAULT 0,
    p_required_action TEXT DEFAULT NULL,
    p_due_date TIMESTAMPTZ DEFAULT NULL
)
RETURNS UUID
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
DECLARE
    v_log_id UUID;
BEGIN
    INSERT INTO public.compliance_logs (
        compliance_type, check_type, status, details, affected_records,
        required_action, due_date
    ) VALUES (
        p_compliance_type, p_check_type, p_status, p_details, p_affected_records,
        p_required_action, p_due_date
    ) RETURNING id INTO v_log_id;

    RETURN v_log_id;
END;
$$;

-- Function to log system events
CREATE OR REPLACE FUNCTION public.log_system_event(
    p_event_type VARCHAR(100),
    p_severity VARCHAR(20),
    p_source VARCHAR(100),
    p_description TEXT,
    p_details JSONB DEFAULT NULL,
    p_user_id UUID DEFAULT NULL,
    p_ip_address INET DEFAULT NULL
)
RETURNS UUID
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
DECLARE
    v_log_id UUID;
BEGIN
    INSERT INTO public.system_event_logs (
        event_type, severity, source, description, details, user_id, ip_address
    ) VALUES (
        p_event_type, p_severity, p_source, p_description, p_details, p_user_id, ip_address
    ) RETURNING id INTO v_log_id;

    RETURN v_log_id;
END;
$$;

-- =====================================================
-- AUDIT TRIGGERS FOR KEY TABLES
-- =====================================================

-- Function to create audit trigger for any table
CREATE OR REPLACE FUNCTION public.audit_trigger_function()
RETURNS TRIGGER
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_id UUID;
    v_user_email TEXT;
    v_old_data JSONB;
    v_new_data JSONB;
    v_affected_fields TEXT[];
    v_field_name TEXT;
BEGIN
    -- Get current user from session
    v_user_id := auth.uid();

    -- Get user email
    SELECT email INTO v_user_email
    FROM public.profiles
    WHERE id = v_user_id;

    -- Prepare data based on operation
    IF TG_OP = 'INSERT' THEN
        v_new_data := to_jsonb(NEW);
        v_old_data := NULL;

        -- Get field names
        v_affected_fields := ARRAY(
            SELECT jsonb_object_keys(v_new_data)
        );

        -- Log the insertion
        PERFORM public.log_audit_event(
            'create',
            TG_TABLE_NAME,
            NEW.id,
            v_user_id,
            v_user_email,
            'INSERT',
            NULL,
            NULL,
            v_new_data,
            v_affected_fields,
            TRUE,
            NULL,
            inet_client_addr(),
            current_setting('request.headers', true)::json->>'user-agent'
        );

        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := to_jsonb(NEW);

        -- Get changed fields
        v_affected_fields := ARRAY(
            SELECT jsonb_object_keys(
                jsonb_build_object(
                    SELECT key, value
                    FROM jsonb_each(v_new_data)
                    WHERE NOT jsonb_build_object(key, value) @> jsonb_build_object(key, v_old_data -> key)
                )
            )
        );

        -- Log the update
        PERFORM public.log_audit_event(
            'update',
            TG_TABLE_NAME,
            NEW.id,
            v_user_id,
            v_user_email,
            'UPDATE',
            NULL,
            v_old_data,
            v_new_data,
            v_affected_fields,
            TRUE,
            NULL,
            inet_client_addr(),
            current_setting('request.headers', true)::json->>'user-agent'
        );

        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := NULL;

        -- Get field names
        v_affected_fields := ARRAY(
            SELECT jsonb_object_keys(v_old_data)
        );

        -- Log the deletion
        PERFORM public.log_audit_event(
            'delete',
            TG_TABLE_NAME,
            OLD.id,
            v_user_id,
            v_user_email,
            'DELETE',
            NULL,
            v_old_data,
            NULL,
            v_affected_fields,
            TRUE,
            NULL,
            inet_client_addr(),
            current_setting('request.headers', true)::json->>'user-agent'
        );

        RETURN OLD;
    END IF;

    RETURN NULL;
END;
$$;

-- =====================================================
-- RLS POLICIES FOR AUDIT TABLES
-- =====================================================

-- Enable RLS on audit tables
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.data_access_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.system_event_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.compliance_logs ENABLE ROW LEVEL SECURITY;

-- Audit logs - users can view their own audit logs
CREATE POLICY "Users can view own audit logs"
    ON public.audit_logs
    FOR SELECT
    USING (auth.uid() = user_id);

-- Data access logs - users can view their own access logs
CREATE POLICY "Users can view own data access logs"
    ON public.data_access_logs
    FOR SELECT
    USING (auth.uid() = user_id);

-- System event logs - read only for authenticated users (general info)
CREATE POLICY "Authenticated users can view system events"
    ON public.system_event_logs
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Compliance logs - read only for authenticated users
CREATE POLICY "Authenticated users can view compliance logs"
    ON public.compliance_logs
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- =====================================================
-- GRANTS
-- =====================================================

-- Grant permissions to authenticated users
GRANT SELECT ON public.audit_logs TO authenticated;
GRANT SELECT ON public.data_access_logs TO authenticated;
GRANT SELECT ON public.system_event_logs TO authenticated;
GRANT SELECT ON public.compliance_logs TO authenticated;

-- Grant execute permissions for audit functions
GRANT EXECUTE ON FUNCTION public.log_data_access TO authenticated;
GRANT EXECUTE ON FUNCTION public.log_audit_event TO authenticated;
GRANT EXECUTE ON FUNCTION public.log_compliance_event TO authenticated;
GRANT EXECUTE ON FUNCTION public.log_system_event TO authenticated;

-- Grant all permissions to service role
GRANT ALL ON public.audit_logs TO service_role;
GRANT ALL ON public.data_access_logs TO service_role;
GRANT ALL ON public.system_event_logs TO service_role;
GRANT ALL ON public.compliance_logs TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE public.audit_logs IS 'Main audit trail for all data operations';
COMMENT ON TABLE public.data_access_logs IS 'Specific logs for data access events';
COMMENT ON TABLE public.system_event_logs IS 'System events and security alerts';
COMMENT ON TABLE public.compliance_logs IS 'LGPD compliance monitoring and tracking';

COMMENT ON FUNCTION public.log_data_access IS 'Logs data access events for LGPD compliance';
COMMENT ON FUNCTION public.log_audit_event IS 'General audit event logging function';
COMMENT ON FUNCTION public.log_compliance_event IS 'Logs compliance check results';
COMMENT ON FUNCTION public.log_system_event IS 'Logs system events and security alerts';

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Audit Trail System Migration Complete';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Created comprehensive audit trail tables';
    RAISE NOTICE 'Added audit logging functions';
    RAISE NOTICE 'Configured RLS policies for privacy';
    RAISE NOTICE 'Ready for LGPD compliance monitoring';
    RAISE NOTICE '=================================================';
END $$;
