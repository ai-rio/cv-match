// Shared API types between frontend and backend

// Base API Response Types
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

// Authentication Types
export interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  subscription_tier?: 'free' | 'premium' | 'enterprise';
  credits_remaining?: number;
  created_at?: string;
  updated_at?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string; // "bearer" or "Bearer"
}

export interface LoginRequest {
  email: string;
  password: string;
}

// LLM Service Types
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
  finish_reason?: string;
  created?: number;
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
  dimensions?: number;
}

// Resume Types
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

export interface ResumeUploadRequest {
  filename: string;
  file_content: ArrayBuffer; // For frontend
  // For backend: file_content: bytes
}

export interface ResumeUploadResponse {
  id: string;
  filename: string;
  extracted_text?: string;
  content_type: string;
  created_at: string;
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

// Optimization Types
export interface OptimizationStatus {
  PENDING_PAYMENT: 'pending_payment';
  PROCESSING: 'processing';
  COMPLETED: 'completed';
  FAILED: 'failed';
}

export interface StartOptimizationRequest {
  resume_id: string;
  job_description: string;
  job_title?: string;
  company?: string;
}

export interface OptimizationResponse {
  id: string;
  resume_id: string;
  job_description_id: string;
  match_score?: number;
  improvements: string[];
  keywords: string[];
  status: keyof OptimizationStatus;
  created_at: string;
  completed_at?: string;
  error_message?: string;
}

// Payment and Usage Types
export interface UserCredits {
  user_id: string;
  credits_remaining: number;
  total_credits: number;
  is_pro: boolean;
  tier: 'free' | 'premium' | 'enterprise';
}

export interface UsageLimitCheckResponse {
  can_optimize: boolean;
  is_pro: boolean;
  free_optimizations_used: number;
  free_optimizations_limit: number;
  remaining_free_optimizations: number;
  reason?: string;
  upgrade_prompt?: string;
}

// Pagination Types
export interface PaginationParams {
  page?: number;
  limit?: number;
  offset?: number;
  page_size?: number;
}

export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

// Error Types
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