/**
 * Enhanced Tooltip Component for CV-Match Phase 0.8
 *
 * Brazilian market optimized tooltip with full design system integration
 * WCAG 2.1 AA compliant with excellent accessibility
 *
 * Features:
 * - Multiple tooltip variants
 * - Brazilian market interaction patterns
 * - Full keyboard navigation support
 * - Rich content support
 * - Delay configuration
 */

'use client';

import * as TooltipPrimitive from '@radix-ui/react-tooltip';
import * as React from 'react';

import { cn } from '@/lib/utils';

const TooltipProvider = TooltipPrimitive.Provider;

const Tooltip = TooltipPrimitive.Root;

const TooltipTrigger = TooltipPrimitive.Trigger;

const TooltipContent = React.forwardRef<
  React.ElementRef<typeof TooltipPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Content>
>(({ className, sideOffset = 4, ...props }, ref) => (
  <TooltipPrimitive.Content
    ref={ref}
    sideOffset={sideOffset}
    className={cn(
      'z-50 overflow-hidden rounded-md border bg-popover px-3 py-1.5 text-sm text-popover-foreground shadow-md animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2',
      'max-w-xs', // Brazilian market: readable width
      className
    )}
    {...props}
  />
));
TooltipContent.displayName = TooltipPrimitive.Content.displayName;

/**
 * Enhanced Tooltip with Brazilian market optimizations
 */
export interface EnhancedTooltipProps {
  children: React.ReactNode;
  content: React.ReactNode;
  delayDuration?: number;
  skipDelayDuration?: number;
  disableHoverableContent?: boolean;
  side?: 'top' | 'right' | 'bottom' | 'left';
  align?: 'start' | 'center' | 'end';
  alignOffset?: number;
  sideOffset?: number;
  avoidCollisions?: boolean;
  collisionBoundary?: Element[];
  collisionPadding?: number;
  arrowPadding?: number;
  sticky?: 'partial' | 'always';
  hideWhenDetached?: boolean;
  updatePositionStrategy?: 'always' | 'optimized';
  className?: string;
}

export function EnhancedTooltip({
  children,
  content,
  delayDuration = 400, // Brazilian market: slightly longer delay
  skipDelayDuration = 300,
  disableHoverableContent = false,
  side = 'top',
  align = 'center',
  alignOffset = 0,
  sideOffset = 4,
  avoidCollisions = true,
  collisionBoundary = [],
  collisionPadding = 0,
  arrowPadding = 0,
  sticky = 'partial',
  hideWhenDetached = false,
  updatePositionStrategy = 'optimized',
  className,
}: EnhancedTooltipProps) {
  return (
    <TooltipProvider delayDuration={delayDuration} skipDelayDuration={skipDelayDuration}>
      <Tooltip disableHoverableContent={disableHoverableContent}>
        <TooltipTrigger asChild>{children}</TooltipTrigger>
        <TooltipContent
          side={side}
          align={align}
          alignOffset={alignOffset}
          sideOffset={sideOffset}
          avoidCollisions={avoidCollisions}
          collisionBoundary={collisionBoundary}
          collisionPadding={collisionPadding}
          arrowPadding={arrowPadding}
          sticky={sticky}
          hideWhenDetached={hideWhenDetached}
          updatePositionStrategy={updatePositionStrategy}
          className={className}
        >
          {content}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

/**
 * Simple tooltip for quick usage
 */
export interface SimpleTooltipProps {
  children: React.ReactNode;
  title: string;
  description?: string;
  side?: 'top' | 'right' | 'bottom' | 'left';
  className?: string;
}

export function SimpleTooltip({
  children,
  title,
  description,
  side = 'top',
  className,
}: SimpleTooltipProps) {
  return (
    <EnhancedTooltip
      content={
        <div className="space-y-1">
          <div className="font-medium">{title}</div>
          {description && <div className="text-xs opacity-80">{description}</div>}
        </div>
      }
      side={side}
      className={className}
    >
      {children}
    </EnhancedTooltip>
  );
}

/**
 * Icon tooltip for help text
 */
export interface IconTooltipProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  side?: 'top' | 'right' | 'bottom' | 'left';
  className?: string;
}

export function IconTooltip({
  icon = <span className="h-4 w-4">ⓘ</span>,
  title,
  description,
  side = 'top',
  className,
}: IconTooltipProps) {
  return (
    <SimpleTooltip title={title} description={description} side={side} className={className}>
      <span className="inline-flex items-center justify-center w-4 h-4 text-muted-foreground hover:text-foreground cursor-help">
        {icon}
      </span>
    </SimpleTooltip>
  );
}

/**
 * Form field tooltip for validation messages
 */
export interface FormTooltipProps {
  children: React.ReactNode;
  error?: string;
  warning?: string;
  info?: string;
  side?: 'top' | 'right' | 'bottom' | 'left';
  className?: string;
}

export function FormTooltip({
  children,
  error,
  warning,
  info,
  side = 'right',
  className,
}: FormTooltipProps) {
  if (!error && !warning && !info) {
    return <>{children}</>;
  }

  const getVariant = () => {
    if (error) return 'destructive';
    if (warning) return 'warning';
    return 'info';
  };

  const getContent = () => {
    if (error) return error;
    if (warning) return warning;
    return info;
  };

  return (
    <EnhancedTooltip
      content={
        <div
          className={`flex items-center space-x-2 ${getVariant() === 'destructive' ? 'text-destructive' : getVariant() === 'warning' ? 'text-warning' : 'text-info'}`}
        >
          {getVariant() === 'destructive' && <span className="h-4 w-4">⚠</span>}
          {getVariant() === 'warning' && <span className="h-4 w-4">⚠</span>}
          {getVariant() === 'info' && <span className="h-4 w-4">ℹ</span>}
          <span>{getContent()}</span>
        </div>
      }
      side={side}
      className={className}
    >
      {children}
    </EnhancedTooltip>
  );
}

export { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger };
export default Tooltip;
