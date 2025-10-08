import { createClient, type User, type Session } from '@supabase/supabase-js';
import type { SupabaseUser, SupabaseSession, AuthEvent, AuthResponse, OAuthResponse } from '@/types/supabase';

// Initialize the Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('Missing Supabase environment variables. Authentication might not work correctly.');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Authentication helpers
export async function signInWithGoogle(): Promise<OAuthResponse> {
  try {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });
    return {
      provider: 'google',
      url: data?.url || '',
      error
    };
  } catch (error) {
    return {
      provider: 'google',
      url: '',
      error
    };
  }
}

export async function signInWithLinkedIn(): Promise<OAuthResponse> {
  try {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'linkedin',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });
    return {
      provider: 'linkedin',
      url: data?.url || '',
      error
    };
  } catch (error) {
    return {
      provider: 'linkedin',
      url: '',
      error
    };
  }
}

// Email password authentication
export async function signInWithEmail(email: string, password: string): Promise<AuthResponse> {
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    return {
      user: data.user as SupabaseUser | null,
      session: data.session as SupabaseSession | null,
      error
    };
  } catch (error) {
    return {
      user: null,
      session: null,
      error
    };
  }
}

export async function signUpWithEmail(email: string, password: string): Promise<AuthResponse> {
  try {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/callback`,
      },
    });
    return {
      user: data.user as SupabaseUser | null,
      session: data.session as SupabaseSession | null,
      error
    };
  } catch (error) {
    return {
      user: null,
      session: null,
      error
    };
  }
}

export async function resetPassword(email: string): Promise<{ error: any | null }> {
  try {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/reset-password`,
    });
    return { error };
  } catch (error) {
    return { error };
  }
}

export async function signOut(): Promise<{ error: any | null }> {
  try {
    const { error } = await supabase.auth.signOut();
    return { error };
  } catch (error) {
    return { error };
  }
}

export async function getCurrentUser(): Promise<SupabaseUser | null> {
  try {
    const {
      data: { user },
    } = await supabase.auth.getUser();
    return user as SupabaseUser | null;
  } catch (error) {
    console.error('Error getting current user:', error);
    return null;
  }
}

// Session management
export function onAuthStateChange(
  callback: (event: AuthEvent, session: Session | null) => void
) {
  return supabase.auth.onAuthStateChange((event, session) => {
    callback(event as AuthEvent, session);
  });
}
