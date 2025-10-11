// API Response Base Types
export interface BaseAPIResponse<T = unknown> {
  status: 'success' | 'error';
  data?: T;
  error?: {
    message: string;
    code?: string;
    details?: unknown;
  };
  timestamp?: string;
}

// Health Check API Types
export interface HealthCheckResponse {
  status: 'ok' | 'error';
  backend: {
    status: string;
    version?: string;
    environment?: string;
  };
  backendUrl: string;
  timestamp: string;
}

// LLM API Types (Match backend exactly)
export interface LLMUsage {
  prompt_tokens: number;
  completion_tokens: number | null;
  total_tokens: number;
}

export interface TextGenerationRequest {
  prompt: string;
  model?: string;
  max_tokens?: number;
  temperature?: number;
  provider?: 'openai' | 'anthropic';
}

export interface TextGenerationResponse {
  text: string;
  model: string;
  usage: LLMUsage;
}

export interface EmbeddingRequest {
  text: string;
  model?: string;
  provider?: 'openai' | 'anthropic';
}

export interface EmbeddingResponse {
  embedding: number[];
  model: string;
  usage: LLMUsage;
}

// Resume/CV API Types
export interface Resume {
  id: string;
  user_id: string;
  title: string;
  content: string;
  file_url?: string;
  created_at: string;
  updated_at: string;
}

export interface ResumeCreateRequest {
  title: string;
  content: string;
  file?: File;
}

export interface ResumeUpdateRequest {
  title?: string;
  content?: string;
  file_url?: string;
}

export interface ResumeAnalysisRequest {
  resume_id: string;
  job_description?: string;
  analysis_type?: 'general' | 'ats' | 'keyword' | 'format';
}

export interface ResumeAnalysisResponse {
  score: number;
  strengths: string[];
  improvements: string[];
  keywords: string[];
  suggestions: string[];
  ats_compatibility: {
    score: number;
    issues: string[];
    recommendations: string[];
  };
}

// Job Description Types
export interface JobDescription {
  id: string;
  user_id: string;
  title: string;
  company?: string;
  description: string;
  requirements?: string[];
  created_at: string;
  updated_at: string;
}

export interface JobCreateRequest {
  title: string;
  company?: string;
  description: string;
  requirements?: string[];
}

// User Profile Types
export interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  subscription_tier?: 'free' | 'premium' | 'enterprise';
  credits_remaining: number;
  created_at: string;
  updated_at: string;
}

export interface UserProfileUpdateRequest {
  full_name?: string;
  avatar_url?: string;
}

// Subscription Types
export interface Subscription {
  id: string;
  user_id: string;
  tier: 'free' | 'premium' | 'enterprise';
  status: 'active' | 'inactive' | 'canceled' | 'past_due';
  current_period_end?: string;
  credits_total: number;
  credits_used: number;
  created_at: string;
  updated_at: string;
}

// API Error Types
export interface APIError {
  code: string;
  message: string;
  details?: unknown;
  field?: string;
  timestamp: string;
}

export interface ValidationError extends APIError {
  field: string;
  validation_type: 'required' | 'format' | 'length' | 'type' | 'custom';
}

// API Utility Types
export type APIEndpoint<TRequest = unknown, TResponse = unknown> = {
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  path: string;
  request?: TRequest;
  response: TResponse;
};

export type PaginatedResponse<T> = BaseAPIResponse<{
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}>;

// Search and Filter Types
export interface SearchParams {
  query?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  filters?: Record<string, unknown>;
}

export interface FilterOption {
  value: string;
  label: string;
  count?: number;
}
