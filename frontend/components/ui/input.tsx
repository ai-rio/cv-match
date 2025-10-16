/**
 * Enhanced Input Component for CV-Match Phase 0.8
 *
 * Brazilian market optimized input with full design system integration
 * WCAG 2.1 AA compliant with excellent accessibility
 *
 * Features:
 * - Multiple variants (default, outlined, filled, ghost)
 * - Size variants (sm, md, lg, xl)
 * - Brazilian market mobile optimization
 * - Error and validation states
 * - Loading states and icons
 * - Full keyboard navigation support
 * - Auto-complete and type optimizations
 * - High contrast mode support
 */

'use client';

import { cva, type VariantProps } from 'class-variance-authority';
import { Eye, EyeOff, Loader2, Search } from 'lucide-react';
import React, { forwardRef, InputHTMLAttributes, useState } from 'react';

import { cn } from '@/lib/utils';

/**
 * Input variants using class-variance-authority
 */
const inputVariants = cva(
  // Base styles - Brazilian mobile-first approach
  cn(
    'flex w-full rounded-md border bg-background text-sm ring-offset-background',
    'file:text-foreground file:border-0 file:bg-transparent file:text-sm file:font-medium',
    'placeholder:text-muted-foreground',
    'selection:bg-primary selection:text-primary-foreground',
    'disabled:cursor-not-allowed disabled:opacity-50',
    'transition-all duration-200 ease-in-out',
    // Brazilian market: larger touch targets for mobile
    'min-h-[44px]', // WCAG minimum touch target
    // Focus styles
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
    // High contrast mode support
    '[forced-colors]:border-2 [forced-colors:border-current'
  ),
  {
    variants: {
      variant: {
        // Default variant - standard input
        default: cn(
          'border-input px-3 py-2',
          'focus-visible:border-ring',
          'aria-invalid:border-destructive focus-visible:ring-destructive/20'
        ),

        // Outlined variant - more prominent border
        outlined: cn(
          'border-2 border-input px-3 py-2',
          'focus-visible:border-ring focus-visible:border-ring',
          'aria-invalid:border-destructive focus-visible:ring-destructive/20'
        ),

        // Filled variant - solid background
        filled: cn(
          'border-0 bg-muted px-3 py-2',
          'focus-visible:bg-background focus-visible:ring-2 focus-visible:ring-ring',
          'aria-invalid:bg-destructive/10 focus-visible:ring-destructive/20'
        ),

        // Underlined variant - bottom border only
        underlined: cn(
          'border-0 border-b-2 border-input rounded-none px-1 py-2 bg-transparent',
          'focus-visible:border-ring',
          'aria-invalid:border-destructive'
        ),

        // Ghost variant - minimal styling
        ghost: cn(
          'border-0 px-3 py-2 bg-transparent',
          'focus-visible:bg-muted focus-visible:ring-2 focus-visible:ring-ring',
          'aria-invalid:bg-destructive/5 focus-visible:ring-destructive/20'
        ),

        // Search variant - with search icon
        search: cn(
          'border-input px-3 py-2 pl-10',
          'focus-visible:border-ring',
          'aria-invalid:border-destructive focus-visible:ring-destructive/20'
        ),
      },

      size: {
        // Small size
        sm: cn(
          'h-9 px-3 text-xs',
          'min-h-[36px]' // Still meets WCAG guidelines
        ),

        // Default size - Brazilian mobile optimized
        md: cn(
          'h-11 px-3 text-sm',
          'min-h-[44px]' // WCAG standard
        ),

        // Large size
        lg: cn(
          'h-12 px-4 text-base',
          'min-h-[48px]' // Better touch target
        ),

        // Extra large size
        xl: cn(
          'h-14 px-4 text-lg',
          'min-h-[56px]' // Excellent for Brazilian mobile users
        ),
      },

      state: {
        default: cn(''),
        error: cn('border-destructive text-destructive', 'focus-visible:ring-destructive/20'),
        success: cn('border-success text-success', 'focus-visible:ring-success/20'),
        warning: cn('border-warning text-warning', 'focus-visible:ring-warning/20'),
      },

      fullWidth: {
        true: cn('w-full'),
        false: cn('w-auto'),
      },

      loading: {
        true: cn('opacity-70'),
        false: cn(''),
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
      state: 'default',
      fullWidth: true,
      loading: false,
    },
  }
);

export interface InputProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'>,
    VariantProps<typeof inputVariants> {
  error?: boolean;
  success?: boolean;
  warning?: boolean;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  showPasswordToggle?: boolean;
  onClear?: () => void;
}

/**
 * Enhanced Input Component
 */
const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      variant,
      size,
      state,
      fullWidth,
      loading = false,
      error,
      success,
      warning,
      leftIcon,
      rightIcon,
      showPasswordToggle,
      onClear,
      type,
      disabled,
      ...props
    },
    ref
  ) => {
    const [showPassword, setShowPassword] = useState(false);
    const [isFocused, setIsFocused] = useState(false);

    // Determine state based on props
    const inputState = error ? 'error' : success ? 'success' : warning ? 'warning' : state;

    // Handle password visibility
    const togglePassword = () => setShowPassword(!showPassword);
    const inputType = type === 'password' && showPassword ? 'text' : type;

    // Render left icon
    const renderLeftIcon = () => {
      if (variant === 'search') {
        return (
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        );
      }
      if (leftIcon) {
        return (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
            {leftIcon}
          </div>
        );
      }
      return null;
    };

    // Render right icon(s)
    const renderRightIcon = () => {
      const icons = [];

      if (loading) {
        icons.push(
          <Loader2 key="loading" className="h-4 w-4 animate-spin text-muted-foreground" />
        );
      }

      if (rightIcon) {
        icons.push(
          <div key="right-icon" className="text-muted-foreground">
            {rightIcon}
          </div>
        );
      }

      if (type === 'password' && showPasswordToggle) {
        icons.push(
          <button
            key="password-toggle"
            type="button"
            onClick={togglePassword}
            className="text-muted-foreground hover:text-foreground transition-colors"
            aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
            disabled={disabled}
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        );
      }

      if (onClear && props.value && !disabled) {
        icons.push(
          <button
            key="clear"
            type="button"
            onClick={onClear}
            className="text-muted-foreground hover:text-foreground transition-colors"
            aria-label="Limpar campo"
            disabled={disabled}
          >
            ×
          </button>
        );
      }

      if (icons.length === 0) return null;

      return (
        <div className="absolute right-3 top-1/2 flex -translate-y-1/2 items-center gap-1">
          {icons}
        </div>
      );
    };

    // Calculate padding based on icons
    const getPaddingClasses = () => {
      let classes = '';

      if (variant === 'search' || leftIcon) {
        classes += 'pl-10 ';
      }

      const hasRightIcon =
        rightIcon ||
        loading ||
        (type === 'password' && showPasswordToggle) ||
        (onClear && props.value);
      if (hasRightIcon) {
        classes += 'pr-10 ';
      }

      return classes;
    };

    return (
      <div className={cn('relative w-full', fullWidth && 'max-w-full')}>
        {renderLeftIcon()}
        <input
          type={inputType}
          className={cn(
            inputVariants({
              variant,
              size,
              state: inputState,
              fullWidth,
              loading,
            }),
            getPaddingClasses(),
            // Brazilian Portuguese input optimizations
            '[&::placeholder]:text-muted-foreground/70',
            // Focus state handling
            isFocused && 'ring-2 ring-ring ring-offset-2',
            className
          )}
          ref={ref}
          disabled={disabled || loading}
          aria-invalid={error || undefined}
          aria-describedby={error ? 'input-error' : undefined}
          onFocus={(e) => {
            setIsFocused(true);
            props.onFocus?.(e);
          }}
          onBlur={(e) => {
            setIsFocused(false);
            props.onBlur?.(e);
          }}
          {...props}
        />
        {renderRightIcon()}
      </div>
    );
  }
);

Input.displayName = 'Input';

/**
 * Input Group Component for related inputs
 */
export interface InputGroupProps {
  children: React.ReactNode;
  label?: string;
  description?: string;
  error?: string;
  success?: string;
  warning?: string;
  required?: boolean;
  className?: string;
}

export function InputGroup({
  children,
  label,
  description,
  error,
  success,
  warning,
  required,
  className,
}: InputGroupProps) {
  const hasValidation = error || success || warning;

  return (
    <div className={cn('space-y-2 w-full', className)}>
      {label && (
        <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
          {label}
          {required && <span className="text-destructive ml-1">*</span>}
        </label>
      )}

      {children}

      {description && <p className="text-xs text-muted-foreground">{description}</p>}

      {hasValidation && (
        <p
          id="input-error"
          className={cn(
            'text-xs',
            error && 'text-destructive',
            success && 'text-success',
            warning && 'text-warning'
          )}
          role="alert"
        >
          {error || success || warning}
        </p>
      )}
    </div>
  );
}

/**
 * Form Field Component for comprehensive form handling
 */
export interface FormFieldProps {
  name: string;
  label?: string;
  description?: string;
  error?: string;
  success?: string;
  warning?: string;
  required?: boolean;
  children: React.ReactNode;
  className?: string;
}

export function FormField({
  name,
  label,
  description,
  error,
  success,
  warning,
  required,
  children,
  className,
}: FormFieldProps) {
  return (
    <div className={cn('space-y-2 w-full', className)}>
      {label && (
        <label
          htmlFor={name}
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          {label}
          {required && <span className="text-destructive ml-1">*</span>}
        </label>
      )}

      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(
            child as React.ReactElement<React.InputHTMLAttributes<HTMLInputElement>>,
            {
              id: name,
              'aria-describedby': [
                description && `${name}-description`,
                error && `${name}-error`,
                success && `${name}-success`,
                warning && `${name}-warning`,
              ]
                .filter(Boolean)
                .join(' '),
              'aria-invalid': error ? 'true' : undefined,
            }
          );
        }
        return child;
      })}

      {description && (
        <p id={`${name}-description`} className="text-xs text-muted-foreground">
          {description}
        </p>
      )}

      {(error || success || warning) && (
        <p
          id={`${name}-${error ? 'error' : success ? 'success' : 'warning'}`}
          className={cn(
            'text-xs',
            error && 'text-destructive',
            success && 'text-success',
            warning && 'text-warning'
          )}
          role={error ? 'alert' : 'status'}
        >
          {error || success || warning}
        </p>
      )}
    </div>
  );
}

export { Input, inputVariants };
export default Input;
