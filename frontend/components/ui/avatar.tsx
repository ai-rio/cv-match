/**
 * Enhanced Avatar Component for CV-Match Phase 0.8
 *
 * Brazilian market optimized avatar with full design system integration
 * WCAG 2.1 AA compliant with excellent accessibility
 *
 * Features:
 * - Multiple avatar variants
 * - Brazilian market visual patterns
 * - Fallback handling
 * - Loading states
 * - Accessibility support
 */

'use client';

import * as React from 'react';

import { cn } from '@/lib/utils';

export interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
  src?: string;
  alt?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  fallback?: string;
  isLoading?: boolean;
  onLoadingStatusChange?: (status: 'loading' | 'loaded' | 'error') => void;
}

const Avatar = React.forwardRef<HTMLDivElement, AvatarProps>(
  (
    {
      className,
      src,
      alt,
      size = 'md',
      fallback,
      isLoading = false,
      onLoadingStatusChange,
      children,
      ...props
    },
    ref
  ) => {
    const [imageStatus, setImageStatus] = React.useState<'loading' | 'loaded' | 'error'>('loading');
    const [showFallback, setShowFallback] = React.useState(!src);

    const sizeClasses = {
      xs: 'h-6 w-6 text-xs',
      sm: 'h-8 w-8 text-sm',
      md: 'h-10 w-10 text-base',
      lg: 'h-12 w-12 text-lg',
      xl: 'h-16 w-16 text-xl',
      '2xl': 'h-20 w-20 text-2xl',
    };

    // Brazilian market: slightly larger touch targets
    const touchTargetClasses = {
      xs: 'min-h-[32px] min-w-[32px]',
      sm: 'min-h-[36px] min-w-[36px]',
      md: 'min-h-[44px] min-w-[44px]',
      lg: 'min-h-[48px] min-w-[48px]',
      xl: 'min-h-[56px] min-w-[56px]',
      '2xl': 'min-h-[64px] min-w-[64px]',
    };

    React.useEffect(() => {
      if (src) {
        setImageStatus('loading');
        setShowFallback(false);

        const img = new Image();
        img.onload = () => {
          setImageStatus('loaded');
          onLoadingStatusChange?.('loaded');
        };
        img.onerror = () => {
          setImageStatus('error');
          setShowFallback(true);
          onLoadingStatusChange?.('error');
        };
        img.src = src;
      } else {
        setShowFallback(true);
        setImageStatus('loaded');
      }
    }, [src, onLoadingStatusChange]);

    const getInitials = (name: string) => {
      return name
        .split(' ')
        .map((word) => word.charAt(0).toUpperCase())
        .join('')
        .substring(0, 2);
    };

    const renderFallback = () => {
      if (children) {
        return <div className="flex h-full w-full items-center justify-center">{children}</div>;
      }

      if (fallback) {
        return (
          <div className="flex h-full w-full items-center justify-center font-medium text-muted-foreground">
            {getInitials(fallback)}
          </div>
        );
      }

      return (
        <div className="flex h-full w-full items-center justify-center">
          <svg
            className="h-1/2 w-1/2 text-muted-foreground"
            fill="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path d="M24 20.993V24H0v-2.996A14.977 14.977 0 0112.004 15c4.904 0 9.26 2.354 11.996 5.993zM16.002 8.999a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </div>
      );
    };

    return (
      <div
        ref={ref}
        className={cn(
          'relative inline-flex shrink-0 overflow-hidden rounded-full',
          'bg-muted',
          'ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
          sizeClasses[size],
          touchTargetClasses[size],
          className
        )}
        {...props}
      >
        {src && !showFallback && (
          <img
            src={src}
            alt={alt || fallback || 'Avatar'}
            className={cn(
              'aspect-square h-full w-full object-cover',
              imageStatus === 'loading' && 'opacity-0',
              imageStatus === 'loaded' && 'opacity-100',
              imageStatus === 'error' && 'hidden'
            )}
            onLoad={() => setImageStatus('loaded')}
            onError={() => {
              setImageStatus('error');
              setShowFallback(true);
            }}
          />
        )}

        {(showFallback || imageStatus === 'loading') && renderFallback()}

        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-muted/50">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
          </div>
        )}
      </div>
    );
  }
);

Avatar.displayName = 'Avatar';

/**
 * Avatar Group Component
 */
export interface AvatarGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  max?: number;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  spacing?: 'compact' | 'normal' | 'loose';
}

export function AvatarGroup({
  children,
  max = 5,
  size = 'md',
  spacing = 'normal',
  className,
  ...props
}: AvatarGroupProps) {
  const avatars = React.Children.toArray(children);
  const visibleAvatars = avatars.slice(0, max);
  const remainingCount = avatars.length - max;

  const spacingClasses = {
    compact: '-space-x-2',
    normal: '-space-x-3',
    loose: '-space-x-4',
  };

  return (
    <div className={cn('flex items-center', spacingClasses[spacing], className)} {...props}>
      {visibleAvatars.map((avatar, index) => (
        <div key={index} className="relative ring-2 ring-background">
          {avatar}
        </div>
      ))}

      {remainingCount > 0 && (
        <div
          className={cn(
            'relative flex shrink-0 items-center justify-center rounded-full bg-muted text-muted-foreground font-medium ring-2 ring-background',
            size === 'xs' && 'h-6 w-6 text-xs min-h-[32px] min-w-[32px]',
            size === 'sm' && 'h-8 w-8 text-sm min-h-[36px] min-w-[36px]',
            size === 'md' && 'h-10 w-10 text-base min-h-[44px] min-w-[44px]',
            size === 'lg' && 'h-12 w-12 text-lg min-h-[48px] min-w-[48px]',
            size === 'xl' && 'h-16 w-16 text-xl min-h-[56px] min-w-[56px]',
            size === '2xl' && 'h-20 w-20 text-2xl min-h-[64px] min-w-[64px]'
          )}
        >
          +{remainingCount}
        </div>
      )}
    </div>
  );
}

/**
 * Avatar with Status Indicator
 */
export interface AvatarWithStatusProps extends AvatarProps {
  status?: 'online' | 'offline' | 'away' | 'busy';
  showStatusLabel?: boolean;
}

export function AvatarWithStatus({
  status,
  showStatusLabel = false,
  className,
  ...props
}: AvatarWithStatusProps) {
  const statusColors = {
    online: 'bg-green-500',
    offline: 'bg-gray-400',
    away: 'bg-yellow-500',
    busy: 'bg-red-500',
  };

  const statusLabels = {
    online: 'Online',
    offline: 'Offline',
    away: 'Ausente',
    busy: 'Ocupado',
  };

  return (
    <div className={cn('relative inline-flex flex-col items-center', className)}>
      <div className="relative">
        <Avatar {...props} />
        {status && (
          <div
            className={cn(
              'absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-background',
              statusColors[status]
            )}
            aria-label={statusLabels[status]}
          />
        )}
      </div>

      {showStatusLabel && status && (
        <span className="mt-1 text-xs text-muted-foreground">{statusLabels[status]}</span>
      )}
    </div>
  );
}

export { Avatar };
export default Avatar;
