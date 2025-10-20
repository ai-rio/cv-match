/**
 * Enhanced Separator Component for CV-Match Phase 0.8
 *
 * Brazilian market optimized separator with full design system integration
 * WCAG 2.1 AA compliant with excellent accessibility
 *
 * Features:
 * - Multiple orientation variants
 * - Brazilian market visual patterns
 * - Custom styling options
 * - Accessibility support
 */

'use client';

import * as React from 'react';

import { cn } from '@/lib/utils';

export interface SeparatorProps extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: 'horizontal' | 'vertical';
  decorative?: boolean;
  thickness?: 'thin' | 'medium' | 'thick';
  variant?: 'solid' | 'dashed' | 'dotted';
}

const Separator = React.forwardRef<HTMLDivElement, SeparatorProps>(
  (
    {
      className,
      orientation = 'horizontal',
      decorative = true,
      thickness = 'thin',
      variant = 'solid',
      ...props
    },
    ref
  ) => {
    const orientationClasses = {
      horizontal: 'h-px w-full',
      vertical: 'h-full w-px',
    };

    const thicknessClasses = {
      thin: {
        horizontal: 'h-px',
        vertical: 'w-px',
      },
      medium: {
        horizontal: 'h-0.5',
        vertical: 'w-0.5',
      },
      thick: {
        horizontal: 'h-1',
        vertical: 'w-1',
      },
    };

    const variantClasses = {
      solid: 'bg-border',
      dashed: 'border border-dashed border-border bg-transparent',
      dotted: 'border border-dotted border-border bg-transparent',
    };

    const isHorizontal = orientation === 'horizontal';

    return (
      <div
        ref={ref}
        role={decorative ? 'none' : 'separator'}
        aria-orientation={isHorizontal ? undefined : 'vertical'}
        className={cn(
          'shrink-0',
          orientationClasses[orientation],
          thicknessClasses[thickness][orientation],
          variantClasses[variant],
          // Brazilian market: enhanced visual separation
          'my-4 mx-0',
          isHorizontal ? 'my-4' : 'mx-4',
          className
        )}
        {...props}
      />
    );
  }
);

Separator.displayName = 'Separator';

/**
 * Enhanced Separator with label
 */
export interface LabeledSeparatorProps extends React.HTMLAttributes<HTMLDivElement> {
  label?: string;
  orientation?: 'horizontal' | 'vertical';
  position?: 'center' | 'start' | 'end';
}

export function LabeledSeparator({
  label,
  orientation = 'horizontal',
  position = 'center',
  className,
  ...props
}: LabeledSeparatorProps) {
  if (!label) {
    return <Separator orientation={orientation} className={className} {...props} />;
  }

  const isHorizontal = orientation === 'horizontal';

  if (isHorizontal) {
    const positionClasses = {
      center: 'items-center',
      start: 'items-start',
      end: 'items-end',
    };

    return (
      <div
        className={cn('flex w-full items-center gap-4', positionClasses[position], className)}
        {...props}
      >
        <Separator className="flex-1" />
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap">
          {label}
        </span>
        <Separator className="flex-1" />
      </div>
    );
  }

  // Vertical orientation
  const positionClasses = {
    center: 'justify-center',
    start: 'justify-start',
    end: 'justify-end',
  };

  return (
    <div
      className={cn(
        'flex h-full flex-col items-center gap-4',
        positionClasses[position],
        className
      )}
      {...props}
    >
      <Separator orientation="vertical" className="flex-1" />
      <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap transform -rotate-90">
        {label}
      </span>
      <Separator orientation="vertical" className="flex-1" />
    </div>
  );
}

/**
 * Section Separator - Enhanced visual separator for sections
 */
export interface SectionSeparatorProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  action?: React.ReactNode;
}

export function SectionSeparator({
  title,
  description,
  action,
  className,
  ...props
}: SectionSeparatorProps) {
  if (!title) {
    return <Separator className="my-8" {...props} />;
  }

  return (
    <div className={cn('py-6', className)} {...props}>
      <div className="flex items-center justify-between">
        <div className="min-w-0 flex-1">
          <h3 className="text-lg font-medium leading-6 text-foreground">{title}</h3>
          {description && <p className="mt-1 text-sm text-muted-foreground">{description}</p>}
        </div>
        {action && <div className="ml-4 flex-shrink-0">{action}</div>}
      </div>
      <Separator className="mt-4" />
    </div>
  );
}

/**
 * Spacer Component - For adding consistent spacing
 */
export interface SpacerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  direction?: 'vertical' | 'horizontal';
}

export function Spacer({ size = 'md', direction = 'vertical', className, ...props }: SpacerProps) {
  const sizeClasses = {
    xs: direction === 'vertical' ? 'h-2' : 'w-2',
    sm: direction === 'vertical' ? 'h-4' : 'w-4',
    md: direction === 'vertical' ? 'h-6' : 'w-6',
    lg: direction === 'vertical' ? 'h-8' : 'w-8',
    xl: direction === 'vertical' ? 'h-12' : 'w-12',
    '2xl': direction === 'vertical' ? 'h-16' : 'w-16',
  };

  return <div className={cn(sizeClasses[size], className)} aria-hidden="true" {...props} />;
}

export { Separator };
export default Separator;
