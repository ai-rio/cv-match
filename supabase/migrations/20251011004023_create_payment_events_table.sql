-- Create payment_events table for webhook idempotency
-- This table ensures Stripe webhook events are processed exactly once

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