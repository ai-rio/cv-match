// Main types index file for easy imports

// Supabase and Authentication Types
export * from './supabase';

// API Types
export * from './api';

// Component Types
export * from './components';

// Common utility types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type RequiredBy<T, K extends keyof T> = T & Required<Pick<T, K>>;
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// Common React types
export type ComponentWithChildren<P = {}> = React.FC<P & { children?: React.ReactNode }>;
export type AsyncComponent<T = any> = React.FC<{
  data?: T;
  loading?: boolean;
  error?: string | null;
}>;

// Form and Event types
export type FormEventHandler<T = any> = (data: T) => void | Promise<void>;
export type ChangeHandler = (value: string) => void;
export type AsyncChangeHandler = (value: string) => Promise<void>;

// Error handling types
export type ErrorWithMessage = Error & { message: string };
export type AsyncFunction<T = any> = () => Promise<T>;
export type AsyncFunctionWithParams<P = any, T = any> = (params: P) => Promise<T>;

// Common state patterns
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';
export type StateWithLoading<T> = {
  data: T | null;
  loading: boolean;
  error: string | null;
};

// ID and timestamp types
export type ID = string;
export type Timestamp = string;
export type JsonObject = Record<string, any>;

// Pagination types
export type PaginationParams = {
  page?: number;
  limit?: number;
  offset?: number;
};

export type PaginatedResult<T> = {
  items: T[];
  total: number;
  page: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
};
