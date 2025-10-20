/**
 * Enhanced Button Component for CV-Match Phase 0.8
 *
 * Brazilian market optimized button with full design system integration
 * WCAG 2.1 AA compliant with excellent accessibility
 *
 * Features:
 * - Multiple variants (primary, secondary, outline, ghost, link)
 * - Size variants (sm, md, lg, xl)
 * - Brazilian market touch target optimization
 * - Loading states and animations
 * - Full keyboard navigation support
 * - Reduced motion support
 * - High contrast mode support
 */

'use client';

import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { Loader2 } from 'lucide-react';
import React, { ButtonHTMLAttributes, forwardRef } from 'react';

import { cn } from '@/lib/utils';

/**
 * Button variants using class-variance-authority
 */
const buttonVariants = cva(
  // Base styles - Brazilian mobile-first approach
  cn(
    'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium',
    'ring-offset-background transition-colors',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
    'disabled:pointer-events-none disabled:opacity-50',
    // Brazilian market: larger touch targets for mobile
    'min-h-[44px] min-w-[44px]', // WCAG minimum touch target
    // Responsive padding
    'px-4 py-2.5',
    // Motion preferences
    '[&:not([data-state=loading])]:transition-all [&:not([data-state=loading])]:duration-200',
    '[&:not([data-state=loading])]:ease-in-out',
    // High contrast mode support
    '[forced-colors:active]:outline-1 [forced-colors:active]:outline-button'
  ),
  {
    variants: {
      variant: {
        // Primary variant - Brazilian brand colors
        primary: cn(
          'bg-primary text-primary-foreground shadow-lg hover:shadow-xl',
          'hover:bg-primary/90 active:scale-[0.98]',
          'shadow-primary/25',
          'dark:shadow-primary/20'
        ),

        // Secondary variant
        secondary: cn(
          'bg-secondary text-secondary-foreground shadow-sm',
          'hover:bg-secondary/80 active:scale-[0.98]',
          'border border-border/50'
        ),

        // Outline variant
        outline: cn(
          'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
          'active:scale-[0.98]'
        ),

        // Ghost variant
        ghost: cn('hover:bg-accent hover:text-accent-foreground', 'active:scale-[0.98]'),

        // Destructive variant
        destructive: cn(
          'bg-destructive text-destructive-foreground shadow-lg hover:shadow-xl',
          'hover:bg-destructive/90 active:scale-[0.98]',
          'shadow-destructive/25',
          'dark:shadow-destructive/20'
        ),

        // Success variant - Brazilian market emphasis
        success: cn(
          'bg-success text-success-foreground shadow-lg hover:shadow-xl',
          'hover:bg-success/90 active:scale-[0.98]',
          'shadow-success/25',
          'dark:shadow-success/20'
        ),

        // Warning variant
        warning: cn(
          'bg-warning text-warning-foreground shadow-lg hover:shadow-xl',
          'hover:bg-warning/90 active:scale-[0.98]',
          'shadow-warning/25',
          'dark:shadow-warning/20'
        ),

        // Info variant
        info: cn(
          'bg-info text-info-foreground shadow-lg hover:shadow-xl',
          'hover:bg-info/90 active:scale-[0.98]',
          'shadow-info/25',
          'dark:shadow-info/20'
        ),

        // Link variant
        link: cn(
          'text-primary underline-offset-4 hover:underline',
          'focus-visible:underline',
          'h-auto p-0 min-h-0 min-w-0'
        ),

        // Default for backward compatibility
        default: cn(
          'bg-primary text-primary-foreground shadow-sm hover:bg-primary/90',
          'active:scale-[0.98]'
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
          'h-11 px-4 text-sm',
          'min-h-[44px]' // WCAG standard
        ),

        // Large size
        lg: cn(
          'h-12 px-6 text-base',
          'min-h-[48px]' // Better touch target
        ),

        // Extra large size
        xl: cn(
          'h-14 px-8 text-lg',
          'min-h-[56px]' // Excellent for Brazilian mobile users
        ),

        // Icon size
        icon: cn('h-10 w-10 p-0', 'min-h-[40px] min-w-[40px]'),

        // Default for backward compatibility
        default: cn('h-9 px-4 py-2', 'min-h-[36px]'),
      },
      fullWidth: {
        true: cn('w-full'),
        false: cn('w-auto'),
      },
      loading: {
        true: cn('pointer-events-none opacity-70'),
        false: cn(''),
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
      fullWidth: false,
      loading: false,
    },
  }
);

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
  loadingText?: string;
  success?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
}

/**
 * Enhanced Button Component
 */
const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      asChild = false,
      loading = false,
      loadingText,
      success = false,
      icon,
      iconPosition = 'left',
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const Comp = asChild ? Slot : 'button';

    // Handle loading state
    const isLoading = loading;
    const isDisabled = disabled || isLoading;

    // Render content based on state
    const renderContent = () => {
      if (isLoading && loadingText) {
        return (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            {loadingText}
          </>
        );
      }

      if (isLoading) {
        return (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            {children}
          </>
        );
      }

      if (icon && iconPosition === 'right') {
        return (
          <>
            {children}
            {icon}
          </>
        );
      }

      return (
        <>
          {icon}
          {children}
        </>
      );
    };

    return (
      <Comp
        className={cn(
          buttonVariants({
            variant: success ? 'success' : variant,
            size,
            fullWidth: props.fullWidth,
            loading: isLoading,
          }),
          // Success state animation
          success && 'animate-pulse',
          // Loading state cursor
          isLoading && 'cursor-wait',
          className
        )}
        ref={ref}
        disabled={isDisabled}
        data-state={isLoading ? 'loading' : 'idle'}
        data-success={success}
        aria-disabled={isDisabled}
        aria-describedby={isLoading ? 'loading-description' : undefined}
        {...props}
      >
        {renderContent()}

        {/* Loading screen reader announcement */}
        {isLoading && (
          <span id="loading-description" className="sr-only">
            Carregando...
          </span>
        )}
      </Comp>
    );
  }
);

Button.displayName = 'Button';

/**
 * Button Group Component for Brazilian market
 */
export interface ButtonGroupProps {
  children: React.ReactNode;
  orientation?: 'horizontal' | 'vertical';
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'default';
  className?: string;
}

export function ButtonGroup({
  children,
  orientation = 'horizontal',
  size = 'default',
  className,
}: ButtonGroupProps) {
  const isVertical = orientation === 'vertical';

  return (
    <div
      className={cn(
        'inline-flex',
        isVertical ? 'flex-col' : 'flex-row',
        // Spacing between buttons
        isVertical ? 'space-y-1' : 'space-x-1',
        // Brazilian mobile optimization
        'w-full sm:w-auto',
        className
      )}
      role="group"
      aria-label="Button group"
    >
      {React.Children.map(children, (child, index) => {
        if (React.isValidElement(child) && child.type === Button) {
          const childProps = child.props as ButtonProps;
          return React.cloneElement(child as React.ReactElement<ButtonProps>, {
            size,
            // Remove border radius for middle buttons
            className: cn(
              childProps.className,
              // First button
              index === 0 && (isVertical ? 'rounded-b-none' : 'rounded-r-none'),
              // Last button
              index === React.Children.count(children) - 1 &&
                (isVertical ? 'rounded-t-none' : 'rounded-l-none'),
              // Middle buttons
              index > 0 && index < React.Children.count(children) - 1 && 'rounded-none'
            ),
          });
        }
        return child;
      })}
    </div>
  );
}

export { Button, buttonVariants };
export default Button;
