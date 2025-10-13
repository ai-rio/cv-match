-- =============================================================================
-- CV-MATCH PAYMENT TABLES FOR BRAZILIAN MARKET
-- =============================================================================
-- Migration: Create payment processing tables
-- Created: 2025-01-07
-- Purpose: Support Brazilian BRL payments and subscriptions

-- =============================================================================
-- PAYMENT HISTORY TABLE
-- =============================================================================
-- Tracks all payment transactions for Brazilian market
CREATE TABLE IF NOT EXISTS public.payment_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    stripe_payment_id TEXT UNIQUE,
    stripe_checkout_session_id TEXT,
    stripe_subscription_id TEXT,
    stripe_customer_id TEXT,
    amount INTEGER NOT NULL,  -- Amount in cents (BRL)
    currency TEXT NOT NULL DEFAULT 'brl',
    status TEXT NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'refunded', 'partially_refunded')),
    payment_type TEXT NOT NULL CHECK (payment_type IN ('one_time', 'subscription_payment', 'subscription_setup')),
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.payment_history ENABLE ROW LEVEL SECURITY;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_payment_history_user_id ON public.payment_history(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_history_stripe_payment_id ON public.payment_history(stripe_payment_id);
CREATE INDEX IF NOT EXISTS idx_payment_history_status ON public.payment_history(status);
CREATE INDEX IF NOT EXISTS idx_payment_history_created_at ON public.payment_history(created_at);

-- RLS Policy: Users can manage their own payment history
DROP POLICY IF EXISTS "Users can manage own payment_history" ON public.payment_history;
CREATE POLICY "Users can manage own payment_history"
  ON public.payment_history
  FOR ALL
  USING (auth.uid() = user_id);

-- =============================================================================
-- SUBSCRIPTIONS TABLE
-- =============================================================================
-- Tracks active subscriptions for Brazilian market
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    stripe_subscription_id TEXT UNIQUE NOT NULL,
    stripe_customer_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('trialing', 'active', 'past_due', 'canceled', 'unpaid', 'incomplete', 'incomplete_expired')),
    price_id TEXT,
    product_id TEXT,
    current_period_start TIMESTAMPTZ NOT NULL,
    current_period_end TIMESTAMPTZ NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    canceled_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    trial_start TIMESTAMPTZ,
    trial_end TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON public.subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_subscription_id ON public.subscriptions(stripe_subscription_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON public.subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_current_period_end ON public.subscriptions(current_period_end);

-- RLS Policy: Users can manage their own subscriptions
DROP POLICY IF EXISTS "Users can manage own subscriptions" ON public.subscriptions;
CREATE POLICY "Users can manage own subscriptions"
  ON public.subscriptions
  FOR ALL
  USING (auth.uid() = user_id);

-- =============================================================================
-- STRIPE WEBHOOK EVENTS TABLE
-- =============================================================================
-- Tracks all Stripe webhook events for audit and debugging
CREATE TABLE IF NOT EXISTS public.stripe_webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stripe_event_id TEXT UNIQUE NOT NULL,
    event_type TEXT NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    processing_started_at TIMESTAMPTZ,
    processing_completed_at TIMESTAMPTZ,
    processed_at TIMESTAMPTZ,
    error_message TEXT,
    processing_time_ms NUMERIC,
    data JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    request_id TEXT,
    client_ip TEXT,
    user_agent TEXT
);

-- Enable Row Level Security (admin only for audit)
ALTER TABLE public.stripe_webhook_events ENABLE ROW LEVEL SECURITY;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_stripe_webhook_events_stripe_event_id ON public.stripe_webhook_events(stripe_event_id);
CREATE INDEX IF NOT EXISTS idx_stripe_webhook_events_event_type ON public.stripe_webhook_events(event_type);
CREATE INDEX IF NOT EXISTS idx_stripe_webhook_events_processed ON public.stripe_webhook_events(processed);
CREATE INDEX IF NOT EXISTS idx_stripe_webhook_events_created_at ON public.stripe_webhook_events(created_at);

-- RLS Policy: Only authenticated users can read webhook events
DROP POLICY IF EXISTS "Authenticated users can read webhook_events" ON public.stripe_webhook_events;
CREATE POLICY "Authenticated users can read webhook_events"
  ON public.stripe_webhook_events
  FOR SELECT
  USING (auth.role() = 'authenticated');

-- =============================================================================
-- USER PAYMENT PROFILE TABLE
-- =============================================================================
-- Extends user profile with payment-specific information
CREATE TABLE IF NOT EXISTS public.user_payment_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    stripe_customer_id TEXT UNIQUE,
    plan_type TEXT NOT NULL DEFAULT 'free' CHECK (plan_type IN ('free', 'pro', 'enterprise', 'lifetime')),
    credits_balance INTEGER NOT NULL DEFAULT 0,
    credits_used INTEGER NOT NULL DEFAULT 0,
    billing_address JSONB,
    payment_methods JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.user_payment_profiles ENABLE ROW LEVEL SECURITY;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_payment_profiles_user_id ON public.user_payment_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_payment_profiles_stripe_customer_id ON public.user_payment_profiles(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_user_payment_profiles_plan_type ON public.user_payment_profiles(plan_type);

-- RLS Policy: Users can manage their own payment profile
DROP POLICY IF EXISTS "Users can manage own payment_profile" ON public.user_payment_profiles;
CREATE POLICY "Users can manage own payment_profile"
  ON public.user_payment_profiles
  FOR ALL
  USING (auth.uid() = user_id);

-- =============================================================================
-- TRIGGERS AND FUNCTIONS
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS handle_payment_history_updated_at ON public.payment_history;
CREATE TRIGGER handle_payment_history_updated_at
    BEFORE UPDATE ON public.payment_history
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

DROP TRIGGER IF EXISTS handle_subscriptions_updated_at ON public.subscriptions;
CREATE TRIGGER handle_subscriptions_updated_at
    BEFORE UPDATE ON public.subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

DROP TRIGGER IF EXISTS handle_user_payment_profiles_updated_at ON public.user_payment_profiles;
CREATE TRIGGER handle_user_payment_profiles_updated_at
    BEFORE UPDATE ON public.user_payment_profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- Active subscriptions view
CREATE OR REPLACE VIEW public.active_subscriptions AS
SELECT
    s.*,
    u.email as user_email,
    u.raw_user_meta_data as user_metadata
FROM public.subscriptions s
JOIN auth.users u ON s.user_id = u.id
WHERE s.status = 'active';

-- User payment summary view
CREATE OR REPLACE VIEW public.user_payment_summary AS
SELECT
    upp.user_id,
    upp.plan_type,
    upp.credits_balance,
    upp.credits_used,
    COUNT(DISTINCT ph.id) as total_payments,
    COALESCE(SUM(CASE WHEN ph.status = 'completed' THEN ph.amount ELSE 0 END), 0) as total_spent,
    COUNT(DISTINCT s.id) as total_subscriptions,
    MAX(CASE WHEN s.status = 'active' THEN s.current_period_end ELSE NULL END) as next_billing_date
FROM public.user_payment_profiles upp
LEFT JOIN public.payment_history ph ON upp.user_id = ph.user_id
LEFT JOIN public.subscriptions s ON upp.user_id = s.user_id AND s.status IN ('active', 'trialing')
GROUP BY upp.user_id, upp.plan_type, upp.credits_balance, upp.credits_used;

-- =============================================================================
-- INITIAL DATA
-- =============================================================================

-- Insert default payment profiles for existing users
INSERT INTO public.user_payment_profiles (user_id, plan_type, credits_balance)
SELECT
    id as user_id,
    'free' as plan_type,
    5 as credits_balance  -- 5 free analyses per month for Brazilian market
FROM auth.users
WHERE id NOT IN (SELECT user_id FROM public.user_payment_profiles);

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON TABLE public.payment_history IS 'Tracks all payment transactions for Brazilian market with BRL currency';
COMMENT ON TABLE public.subscriptions IS 'Manages subscription plans for Brazilian users';
COMMENT ON TABLE public.stripe_webhook_events IS 'Audit log for all Stripe webhook events';
COMMENT ON TABLE public.user_payment_profiles IS 'Extended user profile with payment information';

COMMENT ON COLUMN public.payment_history.amount IS 'Amount in cents (BRL - Brazilian Real)';
COMMENT ON COLUMN public.payment_history.currency IS 'Always BRL for Brazilian market';
COMMENT ON COLUMN public.subscriptions.stripe_subscription_id IS 'Stripe subscription identifier';
COMMENT ON COLUMN public.user_payment_profiles.credits_balance IS 'Number of CV analysis credits available';
COMMENT ON COLUMN public.user_payment_profiles.plan_type IS 'Current plan: free, pro, enterprise, or lifetime';
