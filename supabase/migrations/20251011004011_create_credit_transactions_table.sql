-- Create credit_transactions table for audit trail
-- This table provides LGPD compliant audit logging for all credit changes

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
