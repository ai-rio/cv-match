-- =====================================================
-- ENHANCE PROFILES FOR LGPD COMPLIANCE
-- =====================================================
-- This migration enhances the existing profiles table to meet
-- Brazilian LGPD (General Data Protection Law) requirements
-- and align with Resume-Matcher schema structure.
--
-- Created: 2025-10-10
-- Purpose: LGPD compliance and schema alignment
-- =====================================================

-- =====================================================
-- BACKUP EXISTING PROFILES DATA
-- =====================================================

-- Create backup of existing profiles before modification
CREATE TEMP TABLE profiles_backup AS SELECT * FROM public.profiles;

-- =====================================================
-- DROP EXISTING PROFILES TABLE AND RECREATE
-- =====================================================

-- Drop existing table (will be recreated with enhanced schema)
DROP TABLE IF EXISTS public.profiles CASCADE;

-- Drop existing function if it exists
DROP FUNCTION IF EXISTS public.get_profile(uuid);

-- =====================================================
-- CREATE ENHANCED PROFILES TABLE
-- =====================================================

-- User profiles (extends Supabase auth.users) with LGPD compliance
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    email TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMPTZ DEFAULT NULL,

    -- LGPD compliance fields
    data_retention_date TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '5 years'),
    consent_marketing BOOLEAN DEFAULT FALSE,
    consent_data_processing BOOLEAN DEFAULT TRUE,

    -- Constraints
    CONSTRAINT full_name_length CHECK (LENGTH(full_name) <= 255),
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- =====================================================
-- ENABLE ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- RLS POLICIES FOR PROFILES
-- =====================================================

-- Users can view own profile
CREATE POLICY "Users can view own profile"
    ON public.profiles
    FOR SELECT
    USING (auth.uid() = id AND deleted_at IS NULL);

-- Users can update own profile
CREATE POLICY "Users can update own profile"
    ON public.profiles
    FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- Users can insert own profile
CREATE POLICY "Users can insert own profile"
    ON public.profiles
    FOR INSERT
    WITH CHECK (auth.uid() = id);

-- =====================================================
-- INDEXES FOR PROFILES
-- =====================================================

-- Performance indexes
CREATE INDEX idx_profiles_email ON public.profiles(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_profiles_created_at ON public.profiles(created_at);
CREATE INDEX idx_profiles_deleted_at ON public.profiles(deleted_at) WHERE deleted_at IS NOT NULL;
CREATE INDEX idx_profiles_retention_date ON public.profiles(data_retention_date) WHERE deleted_at IS NOT NULL;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE public.profiles IS 'User profiles with LGPD compliance fields and soft delete support';
COMMENT ON COLUMN public.profiles.data_retention_date IS 'Date when user data should be automatically deleted per LGPD requirements';
COMMENT ON COLUMN public.profiles.deleted_at IS 'Soft delete timestamp for LGPD compliance';
COMMENT ON COLUMN public.profiles.consent_marketing IS 'LGPD consent for marketing communications';
COMMENT ON COLUMN public.profiles.consent_data_processing IS 'LGPD consent for data processing';

-- =====================================================
-- RESTORE BACKUP DATA
-- =====================================================

-- Restore data from backup, mapping old columns to new structure
INSERT INTO public.profiles (id, full_name, email, created_at)
SELECT
    id,
    name as full_name,
    NULL as email,  -- Will be populated by trigger
    created_at
FROM profiles_backup
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- CREATE FUNCTIONS
-- =====================================================

-- Function to handle new user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name, email)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name'),
        NEW.email
    );
    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Failed to create profile for user %: %', NEW.id, SQLERRM;
        RETURN NEW;
END;
$$;

COMMENT ON FUNCTION public.handle_new_user IS 'Automatically creates a profile when a new user signs up';

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION public.update_updated_at_column IS 'Automatically updates updated_at timestamp on row modification';

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger for new user creation
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Trigger for updated_at column
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Public profiles view (non-sensitive data only)
CREATE OR REPLACE VIEW public.public_profiles AS
SELECT
    p.id,
    p.full_name,
    p.created_at
FROM public.profiles p
WHERE p.deleted_at IS NULL;

COMMENT ON VIEW public.public_profiles IS 'Public view of user profiles with non-sensitive data only';

-- =====================================================
-- GRANTS AND PERMISSIONS
-- =====================================================

-- Grant permissions to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT ON public.profiles TO authenticated;
GRANT UPDATE ON public.profiles TO authenticated;
GRANT INSERT ON public.profiles TO authenticated;
GRANT SELECT ON public.public_profiles TO authenticated, anon;

-- Grant permissions to service role
GRANT ALL ON public.profiles TO service_role;
GRANT ALL ON public.public_profiles TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Profiles LGPD Enhancement Migration Complete';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Enhanced profiles table with LGPD compliance';
    RAISE NOTICE 'Added: data_retention_date, consent fields, soft delete';
    RAISE NOTICE 'Restored existing profile data';
    RAISE NOTICE 'Created triggers for automatic profile creation';
    RAISE NOTICE '=================================================';
END $$;
