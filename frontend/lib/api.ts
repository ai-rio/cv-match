/**
 * API service for communicating with the backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_URL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    // Remove Content-Type header for FormData requests
    const headers = options.body instanceof FormData
      ? { ...defaultHeaders, ...options.headers, 'Content-Type': undefined }
      : { ...defaultHeaders, ...options.headers };

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        // Try to parse error response
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          // If response is not JSON, use default error message
        }
        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred');
    }
  }

  // Auth endpoints
  async login(email: string, password: string) {
    return this.request<{ access_token: string; token_type: string }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async getCurrentUser(token: string) {
    return this.request<{
      id: string;
      email: string;
      full_name?: string;
      avatar_url?: string;
    }>('/api/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async exchangeProviderToken(provider: string, token: string) {
    return this.request<{ access_token: string; token_type: string }>('/api/auth/provider-token', {
      method: 'POST',
      body: JSON.stringify({ provider, token }),
    });
  }

  // Generic GET method
  async get<T>(endpoint: string, token?: string) {
    const headers: Record<string, string> = {};
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    return this.request<T>(endpoint, {
      method: 'GET',
      headers,
    });
  }

  // Generic POST method
  async post<T>(endpoint: string, data?: any, token?: string) {
    const headers: Record<string, string> = {};
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
      headers,
    });
  }

  // Generic PUT method
  async put<T>(endpoint: string, data?: any, token?: string) {
    const headers: Record<string, string> = {};
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
      headers,
    });
  }

  // Generic DELETE method
  async delete<T>(endpoint: string, token?: string) {
    const headers: Record<string, string> = {};
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    return this.request<T>(endpoint, {
      method: 'DELETE',
      headers,
    });
  }
}

// Export singleton instance
export const apiService = new ApiService();