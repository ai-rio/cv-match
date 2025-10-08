// Supabase User Types
export interface SupabaseUser {
  id: string;
  email?: string;
  phone?: string;
  user_metadata?: Record<string, any>;
  app_metadata?: Record<string, any>;
  created_at: string;
  updated_at?: string;
  aud: string;
  role: string;
}

export interface SupabaseSession {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
  user: SupabaseUser;
}

export interface AuthState {
  user: SupabaseUser | null;
  session: SupabaseSession | null;
  loading: boolean;
}

// Auth Event Types
export type AuthEvent = 'SIGNED_IN' | 'SIGNED_OUT' | 'USER_UPDATED' | 'TOKEN_REFRESHED' | 'PASSWORD_RECOVERY';

// Supabase Auth Response Types
export interface AuthResponse {
  user: SupabaseUser | null;
  session: SupabaseSession | null;
  error: any | null;
}

export interface OAuthResponse {
  provider: string;
  url: string;
  error: any | null;
}

// API Request/Response Types
export interface APIResponse<T = any> {
  data?: T;
  error?: {
    message: string;
    code?: string;
    details?: any;
  };
  status: 'success' | 'error';
}

// Environment Types
export interface ProcessEnv {
  NEXT_PUBLIC_SUPABASE_URL?: string;
  NEXT_PUBLIC_SUPABASE_ANON_KEY?: string;
  NEXT_PUBLIC_API_URL?: string;
  [key: string]: string | undefined;
}