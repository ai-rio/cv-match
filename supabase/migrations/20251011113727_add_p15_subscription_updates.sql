-- ============================================================================
-- P1.5 SUBSCRIPTION SYSTEM DATABASE UPDATES
-- Migration for enhanced subscription management with usage tracking and LGPD compliance
-- ============================================================================

-- ============================================================================
-- UPDATE PROFILES TABLE - Add Stripe Customer Fields
-- ============================================================================

-- Add Stripe customer fields to profiles table
ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT UNIQUE,
ADD COLUMN IF NOT EXISTS stripe_customer_created_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS billing_email TEXT,
ADD COLUMN IF NOT EXISTS billing_address JSONB,
ADD COLUMN IF NOT EXISTS tax_ids JSONB;

-- Add comments for documentation
COMMENT ON COLUMN profiles.stripe_customer_id IS 'Stripe customer ID for payment processing';
COMMENT ON COLUMN profiles.billing_email IS 'Email for billing (may differ from account email)';
COMMENT ON COLUMN profiles.billing_address IS 'Billing address in JSON format: {line1, line2, city, state, postal_code, country}';
COMMENT ON COLUMN profiles.tax_ids IS 'Tax identification numbers (CPF/CNPJ for Brazil): [{type, value}]';

-- Create index on stripe_customer_id for fast lookups
CREATE INDEX IF NOT EXISTS idx_profiles_stripe_customer_id
ON profiles(stripe_customer_id)
WHERE stripe_customer_id IS NOT NULL;

-- ============================================================================
-- UPDATE SUBSCRIPTIONS TABLE - Add missing fields for P1.5 requirements
-- ============================================================================

-- Add tier_id column for subscription tiers
ALTER TABLE subscriptions
ADD COLUMN IF NOT EXISTS tier_id TEXT NOT NULL DEFAULT 'flow_starter';

-- Add usage tracking columns
ALTER TABLE subscriptions
ADD COLUMN IF NOT EXISTS analyses_used_this_period INTEGER DEFAULT 0 CHECK (analyses_used_this_period >= 0),
ADD COLUMN IF NOT EXISTS analyses_rollover INTEGER DEFAULT 0 CHECK (analyses_rollover >= 0);

-- Add cancellation reason column
ALTER TABLE subscriptions
ADD COLUMN IF NOT EXISTS cancellation_reason TEXT;

-- Add soft delete column for LGPD compliance
ALTER TABLE subscriptions
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- Update status check constraint to include new statuses
ALTER TABLE subscriptions
DROP CONSTRAINT IF EXISTS subscriptions_status_check;
ALTER TABLE subscriptions
ADD CONSTRAINT subscriptions_status_check
CHECK (status IN ('active', 'canceled', 'past_due', 'paused', 'incomplete', 'trialing', 'unpaid', 'incomplete_expired'));

-- Add stripe_price_id if it doesn't exist
ALTER TABLE subscriptions
ADD COLUMN IF NOT EXISTS stripe_price_id TEXT;

-- Add comments for new columns
COMMENT ON COLUMN subscriptions.tier_id IS 'Subscription tier: flow_starter, flow_pro, flow_business, flow_enterprise';
COMMENT ON COLUMN subscriptions.analyses_used_this_period IS 'Number of analyses used in current billing period';
COMMENT ON COLUMN subscriptions.analyses_rollover IS 'Unused analyses rolled over from previous period';
COMMENT ON COLUMN subscriptions.cancellation_reason IS 'Reason for subscription cancellation';
COMMENT ON COLUMN subscriptions.deleted_at IS 'Soft delete timestamp for LGPD compliance';
COMMENT ON COLUMN subscriptions.stripe_price_id IS 'Stripe price ID for the subscription';

-- Add unique constraint for active subscriptions
CREATE UNIQUE INDEX one_active_subscription_per_user ON subscriptions(user_id, status)
WHERE status = 'active' AND deleted_at IS NULL;

-- Create new indexes for performance
CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON subscriptions(user_id, status)
WHERE status = 'active' AND deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_subscriptions_deleted_at ON subscriptions(deleted_at);

-- ============================================================================
-- CREATE SUBSCRIPTION USAGE HISTORY TABLE - Audit trail for LGPD compliance
-- ============================================================================

CREATE TABLE IF NOT EXISTS subscription_usage_history (
  -- Primary key
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Relationships
  subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

  -- Event type
  event_type TEXT NOT NULL CHECK (event_type IN (
    'analysis_used',
    'subscription_created',
    'subscription_renewed',
    'subscription_upgraded',
    'subscription_downgraded',
    'subscription_canceled',
    'period_renewed',
    'rollover_applied'
  )),

  -- Usage details
  analyses_before INTEGER,
  analyses_after INTEGER,
  rollover_before INTEGER,
  rollover_after INTEGER,

  -- Period tracking
  period_start TIMESTAMPTZ,
  period_end TIMESTAMPTZ,

  -- Event metadata
  event_metadata JSONB DEFAULT '{}',

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Add comments
COMMENT ON TABLE subscription_usage_history IS 'Audit trail for all subscription events (LGPD compliance)';
COMMENT ON COLUMN subscription_usage_history.event_type IS 'Type of subscription event';
COMMENT ON COLUMN subscription_usage_history.event_metadata IS 'Additional event data (tier_id, reason, etc.)';

-- Indexes for querying history
CREATE INDEX idx_usage_history_subscription_id ON subscription_usage_history(subscription_id);
CREATE INDEX idx_usage_history_user_id ON subscription_usage_history(user_id);
CREATE INDEX idx_usage_history_event_type ON subscription_usage_history(event_type);
CREATE INDEX idx_usage_history_created_at ON subscription_usage_history(created_at DESC);

-- Composite index for user event history
CREATE INDEX idx_usage_history_user_events ON subscription_usage_history(user_id, created_at DESC);

-- ============================================================================
-- UPDATE STRIPE WEBHOOK EVENTS TABLE - Add missing fields
-- ============================================================================

-- Add missing columns if they don't exist
ALTER TABLE stripe_webhook_events
ADD COLUMN IF NOT EXISTS processing_error TEXT,
ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL;

-- Add comments
COMMENT ON COLUMN stripe_webhook_events.processing_error IS 'Error message if processing failed';
COMMENT ON COLUMN stripe_webhook_events.retry_count IS 'Number of processing retry attempts';

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on subscriptions table (if not already enabled)
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- Update existing policies and add new ones
DROP POLICY IF EXISTS "Users can manage own subscriptions" ON subscriptions;
DROP POLICY IF EXISTS subscriptions_select_own ON subscriptions;
DROP POLICY IF EXISTS subscriptions_insert_own ON subscriptions;
DROP POLICY IF EXISTS subscriptions_update_own ON subscriptions;
DROP POLICY IF EXISTS subscriptions_service_all ON subscriptions;

-- Policy 1: Users can view their own subscriptions
CREATE POLICY subscriptions_select_own ON subscriptions
  FOR SELECT
  USING (
    auth.uid() = user_id
    AND deleted_at IS NULL
  );

-- Policy 2: Users can insert their own subscriptions (via service)
CREATE POLICY subscriptions_insert_own ON subscriptions
  FOR INSERT
  WITH CHECK (
    auth.uid() = user_id
  );

-- Policy 3: Users can update their own subscriptions
CREATE POLICY subscriptions_update_own ON subscriptions
  FOR UPDATE
  USING (
    auth.uid() = user_id
    AND deleted_at IS NULL
  )
  WITH CHECK (
    auth.uid() = user_id
  );

-- Policy 4: Service role can do everything (backend operations)
CREATE POLICY subscriptions_service_all ON subscriptions
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Enable RLS on subscription_usage_history
ALTER TABLE subscription_usage_history ENABLE ROW LEVEL SECURITY;

-- Policy 1: Users can view their own usage history
CREATE POLICY usage_history_select_own ON subscription_usage_history
  FOR SELECT
  USING (
    auth.uid() = user_id
  );

-- Policy 2: Service role can insert usage events
CREATE POLICY usage_history_insert_service ON subscription_usage_history
  FOR INSERT
  WITH CHECK (true);

-- Update webhook events policies
DROP POLICY IF EXISTS "Authenticated users can read webhook_events" ON stripe_webhook_events;
DROP POLICY IF EXISTS webhook_events_service_only ON stripe_webhook_events;

-- Policy: Only service role can access webhook events
CREATE POLICY webhook_events_service_only ON stripe_webhook_events
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Grant necessary permissions to service role
GRANT ALL ON subscriptions TO service_role;
GRANT ALL ON subscription_usage_history TO service_role;
GRANT ALL ON stripe_webhook_events TO service_role;

-- Grant read access to authenticated users (via RLS)
GRANT SELECT ON subscriptions TO authenticated;
GRANT SELECT ON subscription_usage_history TO authenticated;

-- ============================================================================
-- TRIGGERS - Automatic audit trail
-- ============================================================================

-- Create trigger function: Update updated_at timestamp (if doesn't exist)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to subscriptions table (update existing)
DROP TRIGGER IF EXISTS handle_subscriptions_updated_at ON subscriptions;
DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON subscriptions;
CREATE TRIGGER update_subscriptions_updated_at
  BEFORE UPDATE ON subscriptions
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to stripe_webhook_events table
DROP TRIGGER IF EXISTS update_stripe_webhook_events_updated_at ON stripe_webhook_events;
CREATE TRIGGER update_stripe_webhook_events_updated_at
  BEFORE UPDATE ON stripe_webhook_events
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Trigger function: Log subscription changes to usage history
CREATE OR REPLACE FUNCTION log_subscription_change()
RETURNS TRIGGER AS $$
BEGIN
  -- Log subscription status changes
  IF (TG_OP = 'INSERT') THEN
    INSERT INTO subscription_usage_history (
      subscription_id,
      user_id,
      event_type,
      analyses_before,
      analyses_after,
      rollover_before,
      rollover_after,
      period_start,
      period_end,
      event_metadata
    ) VALUES (
      NEW.id,
      NEW.user_id,
      'subscription_created',
      0,
      0,
      0,
      NEW.analyses_rollover,
      NEW.current_period_start,
      NEW.current_period_end,
      jsonb_build_object('tier_id', NEW.tier_id)
    );
  ELSIF (TG_OP = 'UPDATE') THEN
    -- Log usage changes
    IF (OLD.analyses_used_this_period != NEW.analyses_used_this_period) THEN
      INSERT INTO subscription_usage_history (
        subscription_id,
        user_id,
        event_type,
        analyses_before,
        analyses_after,
        rollover_before,
        rollover_after,
        period_start,
        period_end
      ) VALUES (
        NEW.id,
        NEW.user_id,
        'analysis_used',
        OLD.analyses_used_this_period,
        NEW.analyses_used_this_period,
        OLD.analyses_rollover,
        NEW.analyses_rollover,
        NEW.current_period_start,
        NEW.current_period_end
      );
    END IF;

    -- Log period renewals
    IF (OLD.current_period_start != NEW.current_period_start) THEN
      INSERT INTO subscription_usage_history (
        subscription_id,
        user_id,
        event_type,
        analyses_before,
        analyses_after,
        rollover_before,
        rollover_after,
        period_start,
        period_end,
        event_metadata
      ) VALUES (
        NEW.id,
        NEW.user_id,
        'period_renewed',
        OLD.analyses_used_this_period,
        NEW.analyses_used_this_period,
        OLD.analyses_rollover,
        NEW.analyses_rollover,
        NEW.current_period_start,
        NEW.current_period_end,
        jsonb_build_object(
          'rollover_applied', NEW.analyses_rollover
        )
      );
    END IF;

    -- Log cancellations
    IF (OLD.status != 'canceled' AND NEW.status = 'canceled') THEN
      INSERT INTO subscription_usage_history (
        subscription_id,
        user_id,
        event_type,
        period_start,
        period_end,
        event_metadata
      ) VALUES (
        NEW.id,
        NEW.user_id,
        'subscription_canceled',
        NEW.current_period_start,
        NEW.current_period_end,
        jsonb_build_object(
          'reason', NEW.cancellation_reason,
          'canceled_at', NEW.canceled_at
        )
      );
    END IF;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to subscriptions table
DROP TRIGGER IF EXISTS log_subscription_changes ON subscriptions;
CREATE TRIGGER log_subscription_changes
  AFTER INSERT OR UPDATE ON subscriptions
  FOR EACH ROW
  EXECUTE FUNCTION log_subscription_change();

-- ============================================================================
-- LGPD COMPLIANCE - Data Retention (5 years)
-- ============================================================================

-- Function to soft-delete old subscription data
CREATE OR REPLACE FUNCTION cleanup_old_subscription_data()
RETURNS void AS $$
BEGIN
  -- Soft delete subscriptions older than 5 years
  UPDATE subscriptions
  SET deleted_at = NOW()
  WHERE
    created_at < NOW() - INTERVAL '5 years'
    AND deleted_at IS NULL
    AND status IN ('canceled', 'incomplete');

  -- Log cleanup event
  RAISE NOTICE 'Cleaned up old subscription data (5 year retention)';
END;
$$ LANGUAGE plpgsql;

-- Schedule cleanup (run monthly via cron or external scheduler)
-- Note: pg_cron extension required, or run via external scheduler
COMMENT ON FUNCTION cleanup_old_subscription_data IS
  'LGPD compliance: Soft-delete subscription data older than 5 years';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Add a record that this migration has been applied
DO $$
BEGIN
  RAISE NOTICE 'P1.5 Subscription Updates migration applied successfully';
END $$;
