-- Create user_credits table with proper constraints and RLS policies
-- This table tracks user credit balance with LGPD compliance

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
    EXECUTE FUNCTION handle_updated_at();

COMMENT ON TABLE user_credits IS 'Tracks user credit balance';
