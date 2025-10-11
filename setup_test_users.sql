-- Test Users Setup Script
-- Run this in Supabase SQL Editor to set passwords for test users

-- IMPORTANT: You need to set these passwords via Supabase Auth
-- Go to Supabase Dashboard -> Authentication -> Users

-- Users created:
-- 1. carlos@ai.rio.br (Free, 3 credits)
-- 2. pro@testuser.com (Pro, 50 credits)
-- 3. enterprise@testuser.com (Enterprise, 1000 credits)

-- To set passwords:
-- 1. Go to http://localhost:54323 (Supabase Studio)
-- 2. Navigate to Authentication -> Users
-- 3. Find each user and click "Reset Password"
-- 4. Set password: "test123456" (or any password you prefer)

-- Current User Summary:
SELECT
  u.email,
  p.full_name,
  uc.credits_remaining,
  uc.tier,
  u.created_at as created_date,
  CASE uc.tier
    WHEN 'free' THEN '3 optimizations (free tier)'
    WHEN 'pro' THEN 'Unlimited optimizations (pro tier)'
    WHEN 'enterprise' THEN 'Unlimited optimizations (enterprise tier)'
  END as description
FROM auth.users u
JOIN profiles p ON u.id = p.id
JOIN user_credits uc ON u.id = uc.user_id
ORDER BY uc.credits_remaining DESC;