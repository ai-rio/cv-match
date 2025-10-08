import { TextGenerationRequest, TextGenerationResponse } from '@/services/llm';

// Form and UI Component Types
export interface FormState {
  google: boolean;
  linkedin: boolean;
  email: boolean;
}

export interface AuthMode {
  mode: 'signin' | 'signup' | 'reset';
}

// Text Generator Component Types
export interface TextGeneratorState {
  prompt: string;
  response: TextGenerationResponse | null;
  isLoading: boolean;
  error: string | null;
  settings: Omit<TextGenerationRequest, 'prompt'>;
}

// Common UI Props
export interface BaseButtonProps {
  disabled?: boolean;
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

export interface IconButtonProps extends BaseButtonProps {
  icon?: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
}

// Input Component Types
export interface InputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
  type?: 'text' | 'email' | 'password' | 'number';
  autoComplete?: string;
  id?: string;
  name?: string;
}

export interface SelectProps {
  value: string;
  onChange: (value: string) => void;
  options: Array<{ value: string; label: string }>;
  disabled?: boolean;
  className?: string;
  id?: string;
}

// Modal and Overlay Types
export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  className?: string;
}

// Loading and Error States
export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  error: string | null;
}

// List and Table Types
export interface Column<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: any, row: T) => React.ReactNode;
}

export interface TableProps<T> {
  data: T[];
  columns: Column<T>[];
  loading?: boolean;
  emptyMessage?: string;
  className?: string;
}

// Pagination Types
export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  showFirstLast?: boolean;
}

// Toast/Notification Types
export interface ToastProps {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  onClose: (id: string) => void;
}