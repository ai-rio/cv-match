'use client';

import { useRouter } from 'next/navigation';
import { createContext, ReactNode, useContext, useEffect, useState } from 'react';
import { apiService } from '@/lib/api';

interface User {
  id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  user_metadata?: {
    first_name?: string;
    last_name?: string;
    bio?: string;
  };
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check for existing token on mount
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken) {
      setToken(storedToken);
      // Validate token and get user info
      validateToken(storedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const validateToken = async (authToken: string) => {
    try {
      const userData = await apiService.getCurrentUser(authToken);
      setUser(userData);
    } catch (error) {
      // TODO: Implement proper error logging
      // eslint-disable-next-line no-console
      console.error('Error validating token:', error);
      localStorage.removeItem('auth_token');
      setToken(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      const data = await apiService.login(email, password);
      const authToken = data.access_token;

      // Store token
      localStorage.setItem('auth_token', authToken);
      setToken(authToken);

      // Get user info
      await validateToken(authToken);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setToken(null);
    setUser(null);
    router.push('/');
  };

  const value: AuthContextType = {
    user,
    token,
    loading,
    login,
    logout,
    isAuthenticated: !!user && !!token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
