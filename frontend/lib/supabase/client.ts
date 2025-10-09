'use client';

import { createClient as createSupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

if (!supabaseUrl || !supabaseAnonKey) {
  // TODO: Implement proper logging
  // eslint-disable-next-line no-console
  console.warn('Missing Supabase environment variables. Authentication might not work correctly.');
}

export function createClient() {
  return createSupabaseClient(supabaseUrl, supabaseAnonKey);
}
