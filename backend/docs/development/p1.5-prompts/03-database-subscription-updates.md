# 🎯 P1.5 Phase 2: Database Subscription Updates

**Agent**: database-architect  
**Phase**: 2 (Sequential - MUST wait for Phase 1 to complete)  
**Time Estimate**: 3 hours  
**Dependencies**: Phase 1.1 AND 1.2 must be complete

**Why database-architect?** This task involves database schema design, migrations, RLS policies, and LGPD compliance - core database architecture.

**⚠️ CRITICAL**: DO NOT start this phase until BOTH Prompt 01 AND Prompt 02 are complete!

---

## 📋 Mission

Create the database schema for subscription management. This includes creating the subscriptions table, updating existing tables to support subscriptions, implementing RLS policies, and ensuring LGPD compliance.

**What You're Building:**
- `subscriptions` table with all necessary fields
- Updates to `users` table for Stripe customer tracking
- `subscription_usage_history` table for audit trail
- RLS policies for multi-tenant security
- Indexes for performance
- LGPD compliance (soft deletes, audit trails, retention)

---

## 🔍 Context

### Current State
- ✅ Database has `users`, `resumes`, `optimizations` tables
- ✅ RLS policies exist for existing tables
- ❌ No subscriptions table
- ❌ No subscription usage tracking
- ❌ Users table missing Stripe customer fields

### Target State
- ✅ Complete subscription schema
- ✅ Stripe customer tracking in users table
- ✅ Usage history with audit trail
- ✅ RLS policies for tenant isolation
- ✅ Indexes for query performance
- ✅ LGPD compliant (5-year retention, soft deletes)

### Reference Architecture
You're adapting **QuoteKit's subscription database schema**:
- QuoteKit: `/home/carlos/projects/QuoteKit/docs/architecture/01-specifications/S004-comprehensive-subscription-schema.sql`

---

## 🛠️ CRITICAL: Tools You MUST Use

### 1. Supabase Studio
Access the database UI:
```bash
# Open Supabase Studio
http://localhost:54323

# Navigate to:
# - Table Editor: View current schema
# - SQL Editor: Test queries
# - Database: View migrations
```

### 2. Supabase CLI
```bash
# Create migration
supabase migration new add_subscription_tables

# Test migration locally
supabase db reset

# Apply migration
supabase db push
```

### 3. PostgreSQL CLI
```bash
# Connect to database
docker compose exec supabase psql -U postgres -d postgres

# Or use Supabase CLI
supabase db remote psql
```

---

## 📝 Implementation Tasks

### Task 1: Create Migration File (15 min)

**Create**: `/supabase/migrations/YYYYMMDDHHMMSS_add_subscription_tables.sql`

```bash
cd /home/carlos/projects/cv-match
supabase migration new add_subscription_tables
```

This creates a timestamped migration file. Use that file for the next tasks.

---

### Task 2: Update Users Table (20 min)

Add Stripe customer tracking to existing users table:

```sql
-- ============================================================================
-- UPDATE USERS TABLE - Add Stripe Customer Fields
-- ============================================================================

-- Add Stripe customer fields to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT UNIQUE,
ADD COLUMN IF NOT EXISTS stripe_customer_created_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS billing_email TEXT,
ADD COLUMN IF NOT EXISTS billing_address JSONB,
ADD COLUMN IF NOT EXISTS tax_ids JSONB;

-- Add comments for documentation
COMMENT ON COLUMN users.stripe_customer_id IS 'Stripe customer ID for payment processing';
COMMENT ON COLUMN users.billing_email IS 'Email for billing (may differ from account email)';
COMMENT ON COLUMN users.billing_address IS 'Billing address in JSON format: {line1, line2, city, state, postal_code, country}';
COMMENT ON COLUMN users.tax_ids IS 'Tax identification numbers (CPF/CNPJ for Brazil): [{type, value}]';

-- Create index on stripe_customer_id for fast lookups
CREATE INDEX IF NOT EXISTS idx_users_stripe_customer_id 
ON users(stripe_customer_id) 
WHERE stripe_customer_id IS NOT NULL;
```

---

### Task 3: Create Subscriptions Table (45 min)

Main subscription tracking table:

```sql
-- ============================================================================
-- SUBSCRIPTIONS TABLE - Core subscription management
-- ============================================================================

CREATE TABLE IF NOT EXISTS subscriptions (
  -- Primary key
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- User relationship
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Subscription tier (flow_starter, flow_pro, flow_business, flow_enterprise)
  tier_id TEXT NOT NULL,
  
  -- Subscription status
  status TEXT NOT NULL DEFAULT 'active' 
    CHECK (status IN ('active', 'canceled', 'past_due', 'paused', 'incomplete')),
  
  -- Stripe integration
  stripe_subscription_id TEXT UNIQUE,
  stripe_customer_id TEXT NOT NULL,
  stripe_price_id TEXT NOT NULL,
  
  -- Billing period
  current_period_start TIMESTAMPTZ NOT NULL,
  current_period_end TIMESTAMPTZ NOT NULL,
  
  -- Cancellation tracking
  cancel_at_period_end BOOLEAN DEFAULT FALSE,
  canceled_at TIMESTAMPTZ,
  cancellation_reason TEXT,
  
  -- Usage tracking (current period)
  analyses_used_this_period INTEGER DEFAULT 0 CHECK (analyses_used_this_period >= 0),
  analyses_rollover INTEGER DEFAULT 0 CHECK (analyses_rollover >= 0),
  
  -- Trial tracking (if applicable)
  trial_start TIMESTAMPTZ,
  trial_end TIMESTAMPTZ,
  
  -- Metadata
  metadata JSONB DEFAULT '{}',
  
  -- LGPD Compliance
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  deleted_at TIMESTAMPTZ,
  
  -- Constraints
  CONSTRAINT valid_period CHECK (current_period_end > current_period_start),
  CONSTRAINT valid_trial CHECK (trial_end IS NULL OR trial_end > trial_start),
  CONSTRAINT one_active_subscription_per_user UNIQUE (user_id, status) 
    WHERE status = 'active' AND deleted_at IS NULL
);

-- Add comments
COMMENT ON TABLE subscriptions IS 'User subscription management with usage tracking';
COMMENT ON COLUMN subscriptions.tier_id IS 'Subscription tier: flow_starter, flow_pro, flow_business, flow_enterprise';
COMMENT ON COLUMN subscriptions.analyses_used_this_period IS 'Number of analyses used in current billing period';
COMMENT ON COLUMN subscriptions.analyses_rollover IS 'Unused analyses rolled over from previous period';
COMMENT ON COLUMN subscriptions.cancel_at_period_end IS 'If true, subscription cancels at period end';
COMMENT ON COLUMN subscriptions.deleted_at IS 'Soft delete timestamp for LGPD compliance';

-- Indexes for performance
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_subscriptions_status ON subscriptions(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_subscriptions_stripe_subscription_id ON subscriptions(stripe_subscription_id) WHERE stripe_subscription_id IS NOT NULL;
CREATE INDEX idx_subscriptions_period_end ON subscriptions(current_period_end) WHERE status = 'active';

-- Partial index for active subscriptions (most common query)
CREATE INDEX idx_subscriptions_active ON subscriptions(user_id, status) 
WHERE status = 'active' AND deleted_at IS NULL;
```

---

### Task 4: Create Subscription Usage History Table (30 min)

Audit trail for all subscription usage events:

```sql
-- ============================================================================
-- SUBSCRIPTION USAGE HISTORY - Audit trail for LGPD compliance
-- ============================================================================

CREATE TABLE IF NOT EXISTS subscription_usage_history (
  -- Primary key
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Relationships
  subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
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
```

---

### Task 5: Create Webhook Events Table (20 min)

Track all Stripe webhook events for idempotency:

```sql
-- ============================================================================
-- STRIPE WEBHOOK EVENTS - Idempotency and event tracking
-- ============================================================================

CREATE TABLE IF NOT EXISTS stripe_webhook_events (
  -- Primary key
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Stripe event ID (unique constraint for idempotency)
  stripe_event_id TEXT UNIQUE NOT NULL,
  
  -- Event details
  event_type TEXT NOT NULL,
  event_data JSONB NOT NULL,
  
  -- Processing status
  processed BOOLEAN DEFAULT FALSE,
  processed_at TIMESTAMPTZ,
  processing_error TEXT,
  retry_count INTEGER DEFAULT 0,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Add comments
COMMENT ON TABLE stripe_webhook_events IS 'Stripe webhook event log for idempotency';
COMMENT ON COLUMN stripe_webhook_events.stripe_event_id IS 'Unique Stripe event ID prevents duplicate processing';
COMMENT ON COLUMN stripe_webhook_events.processed IS 'Whether event has been successfully processed';

-- Indexes
CREATE INDEX idx_webhook_events_stripe_event_id ON stripe_webhook_events(stripe_event_id);
CREATE INDEX idx_webhook_events_processed ON stripe_webhook_events(processed, created_at);
CREATE INDEX idx_webhook_events_type ON stripe_webhook_events(event_type);
```

---

### Task 6: Create RLS Policies (40 min)

Implement Row Level Security for multi-tenant isolation:

```sql
-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on subscriptions table
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- Policy 1: Users can view their own subscriptions
CREATE POLICY subscriptions_select_own ON subscriptions
  FOR SELECT
  USING (
    auth.uid() = user_id 
    AND deleted_at IS NULL
  );

-- Policy 2: Users can insert their own subscriptions (via service)
-- Note: In practice, only backend service creates subscriptions
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

-- Enable RLS on stripe_webhook_events
ALTER TABLE stripe_webhook_events ENABLE ROW LEVEL SECURITY;

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
```

---

### Task 7: Create Triggers for Audit Trail (20 min)

Automatic audit trail updates:

```sql
-- ============================================================================
-- TRIGGERS - Automatic audit trail
-- ============================================================================

-- Trigger function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to subscriptions table
DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON subscriptions;
CREATE TRIGGER update_subscriptions_updated_at
  BEFORE UPDATE ON subscriptions
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
```

---

### Task 8: Create Data Retention Function (15 min)

LGPD compliance - automatic data cleanup after 5 years:

```sql
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
```

---

## ✅ Verification Checklist

After completing all tasks:

### 1. Migration Applied Successfully
```bash
cd /home/carlos/projects/cv-match

# Apply migration
supabase db push

# Verify no errors
echo $?  # Should be 0
```

### 2. Tables Created
```bash
# Check tables exist
supabase db remote psql -c "
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
  AND tablename IN ('subscriptions', 'subscription_usage_history', 'stripe_webhook_events');
"
```

**Expected output:**
```
           tablename            
--------------------------------
 subscriptions
 subscription_usage_history
 stripe_webhook_events
```

### 3. Users Table Updated
```bash
supabase db remote psql -c "
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' 
  AND column_name IN ('stripe_customer_id', 'billing_email', 'billing_address');
"
```

**Expected**: All 3 columns exist.

### 4. Indexes Created
```bash
supabase db remote psql -c "
SELECT indexname 
FROM pg_indexes 
WHERE tablename = 'subscriptions';
"
```

**Expected**: At least 5 indexes including `idx_subscriptions_active`.

### 5. RLS Policies Enabled
```bash
supabase db remote psql -c "
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
  AND tablename IN ('subscriptions', 'subscription_usage_history');
"
```

**Expected**: `rowsecurity = t` (true) for both tables.

### 6. Triggers Created
```bash
supabase db remote psql -c "
SELECT tgname, tgrelid::regclass 
FROM pg_trigger 
WHERE tgrelid IN ('subscriptions'::regclass);
"
```

**Expected**: `update_subscriptions_updated_at` and `log_subscription_changes` triggers.

### 7. Test Subscription Insert
```bash
supabase db remote psql -c "
INSERT INTO subscriptions (
  user_id,
  tier_id,
  stripe_subscription_id,
  stripe_customer_id,
  stripe_price_id,
  current_period_start,
  current_period_end
) VALUES (
  gen_random_uuid(),
  'flow_pro',
  'sub_test_12345',
  'cus_test_12345',
  'price_test_12345',
  NOW(),
  NOW() + INTERVAL '1 month'
) RETURNING id;
"
```

**Expected**: Returns a UUID, no errors.

### 8. Test Audit Trail Trigger
```bash
supabase db remote psql -c "
SELECT COUNT(*) 
FROM subscription_usage_history 
WHERE event_type = 'subscription_created';
"
```

**Expected**: Count increases after insert (trigger working).

---

## 🚨 Common Issues & Solutions

### Issue 1: Migration Fails - Column Already Exists
**Error**: `ERROR: column "stripe_customer_id" of relation "users" already exists`

**Solution**:
```sql
-- Use IF NOT EXISTS
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT UNIQUE;
```

### Issue 2: RLS Policy Conflicts
**Error**: `ERROR: policy "subscriptions_select_own" for table "subscriptions" already exists`

**Solution**:
```sql
-- Drop and recreate
DROP POLICY IF EXISTS subscriptions_select_own ON subscriptions;
CREATE POLICY subscriptions_select_own ON subscriptions...
```

### Issue 3: Trigger Not Firing
**Error**: No entries in `subscription_usage_history` after insert

**Solution**:
```bash
# Check trigger exists
supabase db remote psql -c "\dft+ subscriptions"

# Verify trigger function
supabase db remote psql -c "\df log_subscription_change"
```

### Issue 4: Permission Denied
**Error**: `ERROR: permission denied for table subscriptions`

**Solution**:
```sql
-- Grant permissions to service role
GRANT ALL ON subscriptions TO service_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO service_role;
```

---

## 📊 Success Criteria

Phase 2 is complete when:
- ✅ All tables created successfully
- ✅ Users table updated with Stripe fields
- ✅ All indexes created
- ✅ RLS policies enabled and working
- ✅ Triggers create audit trail entries
- ✅ Test data can be inserted
- ✅ All verification tests pass
- ✅ Migration committed to git

---

## 🎯 Next Step

After completing Phase 2:
→ **Proceed to Phase 3**: Subscription API Endpoints
→ **Prompt**: `04-subscription-api-endpoints.md`

---

## 💡 Tips

1. **Test locally first** - Use `supabase db reset` to test migration
2. **Check pg_stat_statements** - Monitor query performance
3. **Use EXPLAIN ANALYZE** - Verify indexes are being used
4. **Document changes** - Add comments to all tables/columns
5. **Backup before production** - Always backup before running migrations

---

**Time check**: This should take ~3 hours. If taking longer, ask for help!

**Sequential Execution**: ⚠️ DO NOT start until Phase 1 is complete!

Good luck! 🚀
