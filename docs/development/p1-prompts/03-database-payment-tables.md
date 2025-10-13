# Agent Prompt: Database Payment Tables

**Agent**: database-architect
**Phase**: 2 - Database (After Phase 1 completes)
**Priority**: P0
**Estimated Time**: 1 hour
**Dependencies**: Phase 1 payment and usage services must be copied

---

## 🎯 Mission

Create database tables and migrations for payment tracking, credit management, and usage auditing with proper RLS policies and LGPD compliance.

---

## 📋 Tasks

### Task 1: Create User Credits Table (20 min)

**Actions**:

1. Create migration:

   ```bash
   cd /home/carlos/projects/cv-match
   supabase migration new create_user_credits_table
   ```

2. Add SQL:

   ```sql
   -- supabase/migrations/[timestamp]_create_user_credits_table.sql

   CREATE TABLE IF NOT EXISTS user_credits (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
       credits_remaining INTEGER NOT NULL DEFAULT 3,
       tier TEXT NOT NULL DEFAULT 'free',
       created_at TIMESTAMPTZ DEFAULT NOW(),
       updated_at TIMESTAMPTZ DEFAULT NOW(),
       UNIQUE(user_id),
       CONSTRAINT credits_non_negative CHECK (credits_remaining >= 0)
   );

   CREATE INDEX idx_user_credits_user_id ON user_credits(user_id);

   -- RLS Policies
   ALTER TABLE user_credits ENABLE ROW LEVEL SECURITY;

   CREATE POLICY "Users can view own credits"
       ON user_credits FOR SELECT
       USING (auth.uid() = user_id);

   CREATE POLICY "Service can manage credits"
       ON user_credits FOR ALL
       USING (true);

   -- Trigger for updated_at
   CREATE TRIGGER user_credits_updated_at
       BEFORE UPDATE ON user_credits
       FOR EACH ROW
       EXECUTE FUNCTION update_updated_at();

   COMMENT ON TABLE user_credits IS 'Tracks user credit balance';
   ```

**Success Criteria**:

- [x] Migration file created
- [x] Table has user reference
- [x] Credits cannot go negative
- [x] RLS policies active
- [x] Index on user_id

---

### Task 2: Create Credit Transactions Table (20 min)

**Actions**:

1. Create migration:

   ```bash
   supabase migration new create_credit_transactions_table
   ```

2. Add SQL:

   ```sql
   -- supabase/migrations/[timestamp]_create_credit_transactions_table.sql

   CREATE TYPE transaction_type AS ENUM ('credit', 'debit');
   CREATE TYPE transaction_source AS ENUM ('purchase', 'usage', 'refund', 'bonus');

   CREATE TABLE IF NOT EXISTS credit_transactions (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
       amount INTEGER NOT NULL,
       type transaction_type NOT NULL,
       source transaction_source NOT NULL,
       balance_after INTEGER NOT NULL,
       payment_id TEXT,
       operation_id TEXT,
       metadata JSONB DEFAULT '{}'::jsonb,
       created_at TIMESTAMPTZ DEFAULT NOW(),
       CONSTRAINT amount_positive CHECK (amount > 0)
   );

   CREATE INDEX idx_credit_transactions_user_id ON credit_transactions(user_id);
   CREATE INDEX idx_credit_transactions_payment_id ON credit_transactions(payment_id);
   CREATE INDEX idx_credit_transactions_operation_id ON credit_transactions(operation_id);
   CREATE INDEX idx_credit_transactions_created_at ON credit_transactions(created_at DESC);

   -- RLS Policies
   ALTER TABLE credit_transactions ENABLE ROW LEVEL SECURITY;

   CREATE POLICY "Users can view own transactions"
       ON credit_transactions FOR SELECT
       USING (auth.uid() = user_id);

   CREATE POLICY "Service can insert transactions"
       ON credit_transactions FOR INSERT
       WITH CHECK (true);

   COMMENT ON TABLE credit_transactions IS 'Audit trail for all credit changes';
   ```

**Success Criteria**:

- [x] Transaction types defined
- [x] Audit trail complete
- [x] Idempotency via operation_id
- [x] Balance tracking
- [x] Proper indexes

---

### Task 3: Create Payment Events Table (20 min)

**Actions**:

1. Create migration:

   ```bash
   supabase migration new create_payment_events_table
   ```

2. Add SQL:

   ```sql
   -- supabase/migrations/[timestamp]_create_payment_events_table.sql

   CREATE TABLE IF NOT EXISTS payment_events (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       event_id TEXT NOT NULL UNIQUE,
       event_type TEXT NOT NULL,
       user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
       stripe_customer_id TEXT,
       stripe_session_id TEXT,
       amount INTEGER,
       currency TEXT DEFAULT 'brl',
       status TEXT NOT NULL,
       payload JSONB NOT NULL,
       processed BOOLEAN DEFAULT FALSE,
       processed_at TIMESTAMPTZ,
       error_message TEXT,
       created_at TIMESTAMPTZ DEFAULT NOW(),
       CONSTRAINT payment_events_event_id_key UNIQUE (event_id)
   );

   CREATE INDEX idx_payment_events_event_id ON payment_events(event_id);
   CREATE INDEX idx_payment_events_user_id ON payment_events(user_id);
   CREATE INDEX idx_payment_events_session_id ON payment_events(stripe_session_id);
   CREATE INDEX idx_payment_events_processed ON payment_events(processed) WHERE NOT processed;
   CREATE INDEX idx_payment_events_created_at ON payment_events(created_at DESC);

   -- RLS Policies
   ALTER TABLE payment_events ENABLE ROW LEVEL SECURITY;

   CREATE POLICY "Users can view own payment events"
       ON payment_events FOR SELECT
       USING (auth.uid() = user_id);

   CREATE POLICY "Service can manage payment events"
       ON payment_events FOR ALL
       USING (true);

   COMMENT ON TABLE payment_events IS 'Webhook events from Stripe for idempotency';
   ```

**Success Criteria**:

- [x] Idempotency via event_id
- [x] Webhook payload stored
- [x] Processing status tracked
- [x] Error handling
- [x] Currency support (BRL)

---

### Task 4: Create Atomic Credit Deduction Function (15 min)

**Actions**:

1. Add to database migration:

   ```sql
   -- Add to supabase/migrations/[timestamp]_create_credit_functions.sql

   CREATE OR REPLACE FUNCTION deduct_credits(
       p_user_id UUID,
       p_amount INTEGER,
       p_operation_id TEXT
   )
   RETURNS JSON AS $$
   DECLARE
       v_current_credits INTEGER;
       v_new_balance INTEGER;
   BEGIN
       -- Check if operation already processed (idempotency)
       IF EXISTS (
           SELECT 1 FROM credit_transactions
           WHERE operation_id = p_operation_id
       ) THEN
           RETURN json_build_object(
               'success', true,
               'already_processed', true,
               'message', 'Operation already processed'
           );
       END IF;

       -- Lock row and get current credits
       SELECT credits_remaining INTO v_current_credits
       FROM user_credits
       WHERE user_id = p_user_id
       FOR UPDATE;

       -- Check sufficient credits
       IF v_current_credits < p_amount THEN
           RETURN json_build_object(
               'success', false,
               'error', 'Insufficient credits',
               'current_credits', v_current_credits,
               'required', p_amount
           );
       END IF;

       -- Deduct credits
       v_new_balance := v_current_credits - p_amount;

       UPDATE user_credits
       SET credits_remaining = v_new_balance,
           updated_at = NOW()
       WHERE user_id = p_user_id;

       -- Log transaction
       INSERT INTO credit_transactions (
           user_id,
           amount,
           type,
           source,
           balance_after,
           operation_id
       ) VALUES (
           p_user_id,
           p_amount,
           'debit',
           'usage',
           v_new_balance,
           p_operation_id
       );

       RETURN json_build_object(
           'success', true,
           'previous_balance', v_current_credits,
           'new_balance', v_new_balance,
           'deducted', p_amount
       );
   END;
   $$ LANGUAGE plpgsql SECURITY DEFINER;

   COMMENT ON FUNCTION deduct_credits IS 'Atomically deduct credits with idempotency';
   ```

**Success Criteria**:

- [x] Atomic operation (no race conditions)
- [x] Idempotency via operation_id
- [x] Prevents negative credits
- [x] Logs transaction
- [x] Returns detailed status

---

## 📊 Verification Checklist

```bash
cd /home/carlos/projects/cv-match

# 1. Apply migrations
supabase db push

# 2. Verify tables exist
docker compose exec backend python -c "
from app.core.database import get_supabase_client
client = get_supabase_client()

tables = ['user_credits', 'credit_transactions', 'payment_events']
for table in tables:
    result = client.table(table).select('count').execute()
    print(f'✅ Table {table} exists')
"

# 3. Test atomic deduction function
docker compose exec backend python -c "
from app.core.database import get_supabase_client
client = get_supabase_client()

# Test function exists
result = client.rpc('deduct_credits', {
    'p_user_id': '00000000-0000-0000-0000-000000000000',
    'p_amount': 1,
    'p_operation_id': 'test-op-123'
}).execute()

print(f'✅ Atomic function working: {result.data}')
"
```

---

## 📝 Deliverables

### Migration Files:

1. `supabase/migrations/[timestamp]_create_user_credits_table.sql`
2. `supabase/migrations/[timestamp]_create_credit_transactions_table.sql`
3. `supabase/migrations/[timestamp]_create_payment_events_table.sql`
4. `supabase/migrations/[timestamp]_create_credit_functions.sql`

### Git Commit:

```bash
git add supabase/migrations/
git commit -m "feat(database): Add payment and credit management tables

- Create user_credits table with tier support
- Create credit_transactions for audit trail
- Create payment_events for webhook idempotency
- Add atomic deduct_credits RPC function
- Implement proper RLS policies
- Add indexes for performance
- LGPD compliant audit logging

Features:
- Atomic credit deduction (no race conditions)
- Idempotency via operation_id
- Prevents negative credits (constraint)
- Complete audit trail
- Webhook deduplication
- BRL currency support

Related: P1 Payment Integration Phase 2
Tested: All tables verified, function tested"
```

---

## ⏱️ Timeline

- **00:00-00:20**: Task 1 (User credits table)
- **00:20-00:40**: Task 2 (Credit transactions table)
- **00:40-01:00**: Task 3 (Payment events table)
- **01:00-01:15**: Task 4 (Atomic functions)

**Total**: 1 hour

---

## 🎯 Success Definition

Mission complete when:

1. All 3 tables created
2. RLS policies active
3. Atomic deduction function working
4. Idempotency implemented
5. Migrations applied successfully
6. Ready for webhook implementation

---

**Status**: Ready for deployment 🚀
