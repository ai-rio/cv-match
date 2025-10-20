/**
 * Enhanced Toast Component for CV-Match Phase 0.8
 *
 * Brazilian market optimized toast with full design system integration
 * WCAG 2.1 AA compliant with excellent accessibility
 *
 * Features:
 * - Multiple toast variants
 * - Brazilian market notification patterns
 * - Auto-dismiss functionality
 * - Keyboard navigation support
 * - Rich content support
 */

'use client';

import { cva, type VariantProps } from 'class-variance-authority';
import { AlertCircle, AlertTriangle, CheckCircle, Info, X } from 'lucide-react';
import * as React from 'react';

import { cn } from '@/lib/utils';

/**
 * Toast context for managing toasts
 */
interface Toast {
  id: string;
  title?: string;
  description?: string;
  variant?: 'default' | 'destructive' | 'success' | 'warning' | 'info';
  duration?: number;
  action?: React.ReactNode;
  onDismiss?: () => void;
}

interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
}

const ToastContext = React.createContext<ToastContextType | undefined>(undefined);

export function useToast() {
  const context = React.useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

/**
 * Toast Provider
 */
export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<Toast[]>([]);

  const addToast = React.useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast = { ...toast, id };

    setToasts((prev) => [...prev, newToast]);

    // Auto-dismiss after duration (default 5 seconds)
    const duration = toast.duration || 5000;
    setTimeout(() => {
      removeToast(id);
    }, duration);
  }, []);

  const removeToast = React.useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const clearToasts = React.useCallback(() => {
    setToasts([]);
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast, clearToasts }}>
      {children}
      <ToastViewport />
    </ToastContext.Provider>
  );
}

/**
 * Toast variants
 */
const toastVariants = cva(
  'group pointer-events-auto relative flex w-full items-center justify-between space-x-4 overflow-hidden rounded-md border p-6 pr-8 shadow-lg transition-all data-[swipe=cancel]:translate-x-0 data-[swipe=end]:translate-x-[var(--radix-toast-swipe-end-x)] data-[swipe=move]:translate-x-[var(--radix-toast-swipe-move-x)] data-[swipe=move]:transition-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[swipe=end]:animate-out data-[state=closed]:fade-out-80 data-[state=closed]:slide-out-to-right-full data-[state=open]:slide-in-from-top-full data-[state=open]:sm:slide-in-from-bottom-full',
  {
    variants: {
      variant: {
        default: 'border bg-background text-foreground',
        destructive: 'destructive border-destructive bg-destructive text-destructive-foreground',
        success: 'border-success bg-success text-success-foreground',
        warning: 'border-warning bg-warning text-warning-foreground',
        info: 'border-info bg-info text-info-foreground',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

/**
 * Toast Component
 */
export interface ToastProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof toastVariants> {
  title?: string;
  description?: string;
  action?: React.ReactNode;
  onDismiss?: () => void;
}

const Toast = React.forwardRef<HTMLDivElement, ToastProps>(
  ({ className, variant, title, description, action, onDismiss, ...props }, ref) => {
    const getIcon = () => {
      switch (variant) {
        case 'success':
          return <CheckCircle className="h-5 w-5" />;
        case 'destructive':
          return <AlertCircle className="h-5 w-5" />;
        case 'warning':
          return <AlertTriangle className="h-5 w-5" />;
        case 'info':
          return <Info className="h-5 w-5" />;
        default:
          return null;
      }
    };

    return (
      <div ref={ref} className={cn(toastVariants({ variant }), className)} {...props}>
        <div className="grid gap-1">
          {title && (
            <div className="flex items-center gap-2">
              {getIcon()}
              <div className="text-sm font-semibold">{title}</div>
            </div>
          )}
          {description && <div className="text-sm opacity-90">{description}</div>}
        </div>
        {action}
        <button
          onClick={onDismiss}
          className="absolute right-2 top-2 rounded-md p-1 text-foreground/50 opacity-0 transition-opacity hover:text-foreground focus:opacity-100 focus:outline-none focus:ring-2 group-hover:opacity-100"
          aria-label="Fechar notificação"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    );
  }
);

Toast.displayName = 'Toast';

/**
 * Toast Viewport - Container for all toasts
 */
export function ToastViewport() {
  const { toasts, removeToast } = useToast();

  if (toasts.length === 0) {
    return null;
  }

  return (
    <div
      className="fixed top-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 sm:bottom-0 sm:right-0 sm:top-auto sm:flex-col md:max-w-[420px]"
      role="region"
      aria-label="Notificações"
      aria-live="polite"
      aria-atomic="true"
    >
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          variant={toast.variant}
          title={toast.title}
          description={toast.description}
          action={toast.action}
          onDismiss={() => {
            removeToast(toast.id);
            toast.onDismiss?.();
          }}
          className="mb-2"
        />
      ))}
    </div>
  );
}

/**
 * Toast action hook for easy usage
 */
export function toast() {
  const { addToast } = useToast();

  return React.useMemo(
    () => ({
      success: (
        title: string,
        description?: string,
        options?: Partial<Omit<Toast, 'id' | 'title' | 'description' | 'variant'>>
      ) => addToast({ title, description, variant: 'success', ...options }),
      error: (
        title: string,
        description?: string,
        options?: Partial<Omit<Toast, 'id' | 'title' | 'description' | 'variant'>>
      ) => addToast({ title, description, variant: 'destructive', ...options }),
      warning: (
        title: string,
        description?: string,
        options?: Partial<Omit<Toast, 'id' | 'title' | 'description' | 'variant'>>
      ) => addToast({ title, description, variant: 'warning', ...options }),
      info: (
        title: string,
        description?: string,
        options?: Partial<Omit<Toast, 'id' | 'title' | 'description' | 'variant'>>
      ) => addToast({ title, description, variant: 'info', ...options }),
      default: (
        title: string,
        description?: string,
        options?: Partial<Omit<Toast, 'id' | 'title' | 'description' | 'variant'>>
      ) => addToast({ title, description, variant: 'default', ...options }),
    }),
    [addToast]
  );
}

export { Toast, toastVariants };
export default Toast;
