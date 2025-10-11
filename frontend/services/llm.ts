import { supabase } from './supabase';

// Type declaration for process.env
declare const process: {
  env: {
    NEXT_PUBLIC_API_URL?: string;
    [key: string]: string | undefined;
  };
};

// API Base URL
// For client-side code, use the environment variable or localhost
// The environment variable is set in docker-compose.yml
const API_URL =
  typeof window !== 'undefined'
    ? process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    : 'http://backend:8000'; // When running server-side in Docker, use the service name

// Import types from central type definitions
import {
  EmbeddingRequest,
  EmbeddingResponse,
  TextGenerationRequest,
  TextGenerationResponse,
} from '../types/api';

// Re-export types for convenience
export type { EmbeddingRequest, EmbeddingResponse, TextGenerationRequest, TextGenerationResponse };

// Helper to get authentication token
async function getAuthToken() {
  const {
    data: { session },
  } = await supabase.auth.getSession();
  return session?.access_token;
}

// API request types
type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

// Helper to make authenticated API requests
async function apiRequest<T = unknown>(
  endpoint: string,
  method: HTTPMethod,
  body?: Record<string, unknown>
): Promise<T> {
  const token = await getAuthToken();

  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      Accept: 'application/json',
    },
    mode: 'cors',
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    let errorMessage = `API request failed with status ${response.status}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      // If we can't parse the error as JSON, just use the status message
    }
    throw new Error(errorMessage);
  }

  return response.json() as Promise<T>;
}

// LLM API functions
export async function generateText(
  request: TextGenerationRequest
): Promise<TextGenerationResponse> {
  return apiRequest('/api/llm/generate', 'POST', request as unknown as Record<string, unknown>);
}

export async function createEmbedding(request: EmbeddingRequest): Promise<EmbeddingResponse> {
  return apiRequest('/api/llm/embedding', 'POST', request as unknown as Record<string, unknown>);
}
