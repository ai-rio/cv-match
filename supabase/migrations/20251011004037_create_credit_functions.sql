-- Create atomic credit deduction function with idempotency
-- This function ensures financial data integrity with atomic operations

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

    -- Lock row and get current credits, create if doesn't exist
    INSERT INTO user_credits (user_id, credits_remaining, tier)
    VALUES (p_user_id, 3, 'free')
    ON CONFLICT (user_id) DO NOTHING;

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
