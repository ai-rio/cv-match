/**
 * Enhanced Typography Component for CV-Match Phase 0.8
 *
 * Brazilian Portuguese optimized typography with full design system integration
 * WCAG 2.1 AA compliant with excellent accessibility
 *
 * Features:
 * - Complete typography scale (display, headings, body, text)
 * - Brazilian Portuguese character support and optimization
 * - Responsive typography with mobile-first approach
 * - Multiple text variants (lead, muted, gradient)
 * - Semantic HTML structure
 * - Full keyboard navigation support
 * - High contrast mode support
 * - Truncation and text utilities
 */

'use client';

import { cva, type VariantProps } from 'class-variance-authority';
import React, { forwardRef, HTMLAttributes } from 'react';

import { getTypographyStyles } from '@/lib/design-system/typography';
import { cn } from '@/lib/utils';

/**
 * Typography variants using class-variance-authority
 */
const typographyVariants = cva(
  // Base styles
  cn(
    'text-foreground',
    // Brazilian Portuguese optimization
    'font-sans antialiased',
    // Focus styles for interactive text
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
    // High contrast mode support
    '[forced-colors]:text-current'
  ),
  {
    variants: {
      variant: {
        // Display typography - for hero sections and major headings
        display: cn(
          getTypographyStyles('display').fontFamily,
          'text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight',
          'leading-[1.1] sm:leading-[1.1] md:leading-[1.1]',
          'text-foreground'
        ),

        // Heading levels
        h1: cn(
          getTypographyStyles('h1').fontFamily,
          'text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight',
          'leading-[1.2] sm:leading-[1.2]',
          'text-foreground'
        ),

        h2: cn(
          getTypographyStyles('h2').fontFamily,
          'text-xl sm:text-2xl md:text-3xl font-semibold tracking-tight',
          'leading-[1.25] sm:leading-[1.25]',
          'text-foreground'
        ),

        h3: cn(
          getTypographyStyles('h3').fontFamily,
          'text-lg sm:text-xl md:text-2xl font-semibold tracking-tight',
          'leading-[1.3] sm:leading-[1.3]',
          'text-foreground'
        ),

        h4: cn(
          getTypographyStyles('h4').fontFamily,
          'text-base sm:text-lg md:text-xl font-semibold tracking-tight',
          'leading-[1.35] sm:leading-[1.35]',
          'text-foreground'
        ),

        h5: cn(
          getTypographyStyles('h5').fontFamily,
          'text-sm sm:text-base md:text-lg font-medium tracking-tight',
          'leading-[1.4] sm:leading-[1.4]',
          'text-foreground'
        ),

        h6: cn(
          getTypographyStyles('h6').fontFamily,
          'text-sm md:text-base font-medium tracking-tight',
          'leading-[1.4] sm:leading-[1.4]',
          'text-foreground'
        ),

        // Body text variants
        'body-lg': cn(
          getTypographyStyles('body-lg').fontFamily,
          'text-base sm:text-lg font-normal',
          'leading-relaxed',
          'text-foreground'
        ),

        'body-md': cn(
          getTypographyStyles('body-md').fontFamily,
          'text-sm sm:text-base font-normal',
          'leading-relaxed',
          'text-foreground'
        ),

        'body-sm': cn(
          getTypographyStyles('body-sm').fontFamily,
          'text-sm font-normal',
          'leading-relaxed',
          'text-foreground'
        ),

        'body-xs': cn(
          getTypographyStyles('body-xs').fontFamily,
          'text-xs font-normal',
          'leading-relaxed',
          'text-foreground'
        ),

        // Special variants
        lead: cn('text-lg sm:text-xl font-normal', 'leading-relaxed', 'text-muted-foreground'),

        muted: cn('text-sm font-normal', 'leading-normal', 'text-muted-foreground'),

        caption: cn('text-xs font-normal', 'leading-normal', 'text-muted-foreground'),

        overline: cn(
          'text-xs font-medium uppercase tracking-wider',
          'leading-normal',
          'text-muted-foreground'
        ),

        label: cn('text-sm font-medium', 'leading-none', 'text-foreground'),

        // Gradient text for special emphasis
        gradient: cn(
          'text-lg sm:text-xl font-bold bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent',
          'leading-tight'
        ),

        // Code text
        code: cn('font-mono text-sm bg-muted px-1.5 py-0.5 rounded', 'text-foreground', 'border'),

        // Link text
        link: cn(
          'text-sm underline underline-offset-4',
          'text-primary hover:text-primary/80',
          'transition-colors'
        ),

        // Error text
        'error-text': cn('text-sm font-medium', 'text-destructive'),

        // Success text
        'success-text': cn('text-sm font-medium', 'text-success'),

        // Warning text
        'warning-text': cn('text-sm font-medium', 'text-warning'),
      },

      align: {
        left: cn('text-left'),
        center: cn('text-center'),
        right: cn('text-right'),
        justify: cn('text-justify'),
      },

      weight: {
        thin: cn('font-thin'),
        extralight: cn('font-extralight'),
        light: cn('font-light'),
        normal: cn('font-normal'),
        medium: cn('font-medium'),
        semibold: cn('font-semibold'),
        bold: cn('font-bold'),
        extrabold: cn('font-extrabold'),
        black: cn('font-black'),
      },

      transform: {
        none: cn('normal-case'),
        uppercase: cn('uppercase'),
        lowercase: cn('lowercase'),
        capitalize: cn('capitalize'),
      },

      truncate: {
        true: cn('truncate'),
        false: cn(''),
      },

      lineClamp: {
        1: cn('line-clamp-1'),
        2: cn('line-clamp-2'),
        3: cn('line-clamp-3'),
        4: cn('line-clamp-4'),
        5: cn('line-clamp-5'),
        6: cn('line-clamp-6'),
        none: cn(''),
      },
    },
    defaultVariants: {
      variant: 'body-md',
      align: 'left',
      weight: 'normal',
      transform: 'none',
      truncate: false,
      lineClamp: 'none',
    },
  }
);

export interface TypographyProps
  extends Omit<HTMLAttributes<HTMLElement>, 'color'>,
    VariantProps<typeof typographyVariants> {
  as?: keyof React.JSX.IntrinsicElements;
  children: React.ReactNode;
  color?: string;
}

/**
 * Enhanced Typography Component
 */
const Typography = forwardRef<HTMLElement, TypographyProps>(
  (
    {
      className,
      variant,
      as,
      align,
      weight,
      transform,
      truncate,
      lineClamp,
      color,
      children,
      ...props
    },
    ref
  ) => {
    // Map variants to semantic HTML elements
    const getDefaultElement = (): keyof React.JSX.IntrinsicElements => {
      switch (variant) {
        case 'display':
        case 'h1':
          return 'h1';
        case 'h2':
          return 'h2';
        case 'h3':
          return 'h3';
        case 'h4':
          return 'h4';
        case 'h5':
          return 'h5';
        case 'h6':
          return 'h6';
        case 'lead':
        case 'body-lg':
        case 'body-md':
        case 'body-sm':
        case 'body-xs':
          return 'p';
        case 'caption':
          return 'figcaption';
        case 'code':
          return 'code';
        case 'label':
          return 'label';
        default:
          return 'span';
      }
    };

    const Component = as || getDefaultElement();

    // Use proper typing to avoid SVG/HTML incompatibility
    const componentProps: Record<string, unknown> = { ...props };
    delete (componentProps as Record<string, unknown>).color;

    return React.createElement(
      Component as keyof React.JSX.IntrinsicElements,
      {
        ref,
        className: cn(
          typographyVariants({
            variant,
            align,
            weight,
            transform,
            truncate,
            lineClamp,
          }),
          // Custom color support
          color && `text-[${color}]`,
          className
        ),
        ...componentProps,
      },
      children
    );
  }
);

Typography.displayName = 'Typography';

/**
 * Heading Components for semantic clarity
 */
export interface HeadingProps extends Omit<TypographyProps, 'variant' | 'as'> {
  level: 1 | 2 | 3 | 4 | 5 | 6;
}

export const Heading = forwardRef<HTMLHeadingElement, HeadingProps>(
  ({ level, className, children, ...props }, ref) => {
    const variantMap = {
      1: 'h1' as const,
      2: 'h2' as const,
      3: 'h3' as const,
      4: 'h4' as const,
      5: 'h5' as const,
      6: 'h6' as const,
    };

    const componentMap = {
      1: 'h1' as const,
      2: 'h2' as const,
      3: 'h3' as const,
      4: 'h4' as const,
      5: 'h5' as const,
      6: 'h6' as const,
    };

    return (
      <Typography
        ref={ref}
        variant={variantMap[level]}
        as={componentMap[level]}
        className={cn('scroll-m-20', className)}
        {...props}
      >
        {children}
      </Typography>
    );
  }
);

Heading.displayName = 'Heading';

/**
 * Text Component for body text
 */
export interface TextProps extends Omit<TypographyProps, 'variant'> {
  size?: 'xs' | 'sm' | 'md' | 'lg';
}

export const Text = forwardRef<HTMLParagraphElement, TextProps>(
  ({ size = 'md', className, children, ...props }, ref) => {
    const variantMap = {
      xs: 'body-xs' as const,
      sm: 'body-sm' as const,
      md: 'body-md' as const,
      lg: 'body-lg' as const,
    };

    return (
      <Typography ref={ref} variant={variantMap[size]} as="p" className={className} {...props}>
        {children}
      </Typography>
    );
  }
);

Text.displayName = 'Text';

/**
 * Lead Component for introductory text
 */
export const Lead = forwardRef<HTMLParagraphElement, TypographyProps>(
  ({ className, children, ...props }, ref) => (
    <Typography
      ref={ref}
      variant="lead"
      as="p"
      className={cn('text-xl md:text-2xl', className)}
      {...props}
    >
      {children}
    </Typography>
  )
);

Lead.displayName = 'Lead';

/**
 * Gradient Text Component for emphasis
 */
export const GradientText = forwardRef<HTMLSpanElement, TypographyProps>(
  ({ className, children, ...props }, ref) => (
    <Typography ref={ref} variant="gradient" as="span" className={className} {...props}>
      {children}
    </Typography>
  )
);

GradientText.displayName = 'GradientText';

/**
 * Code Component
 */
export const Code = forwardRef<HTMLElement, TypographyProps>(
  ({ className, children, ...props }, ref) => (
    <Typography ref={ref} variant="code" as="code" className={cn('relative', className)} {...props}>
      {children}
    </Typography>
  )
);

Code.displayName = 'Code';

/**
 * Blockquote Component
 */
export interface BlockquoteProps extends TypographyProps {
  cite?: string;
}

export const Blockquote = forwardRef<HTMLQuoteElement, BlockquoteProps>(
  ({ className, cite, children, ...props }, ref) => (
    <blockquote
      ref={ref}
      className={cn('border-l-4 border-primary pl-4 italic', 'text-muted-foreground', className)}
      cite={cite}
      {...props}
    >
      <Typography variant="body-md" as="p">
        {children}
      </Typography>
      {cite && (
        <Typography variant="caption" as="cite" className="block mt-2 not-italic">
          — {cite}
        </Typography>
      )}
    </blockquote>
  )
);

Blockquote.displayName = 'Blockquote';

/**
 * List Components
 */
export interface ListProps extends TypographyProps {
  type?: 'unordered' | 'ordered';
}

export const List = forwardRef<HTMLUListElement | HTMLOListElement, ListProps>(
  ({ type = 'unordered', className, children, ...props }, ref) => {
    const Component = type === 'ordered' ? 'ol' : 'ul';

    return React.createElement(
      Component,
      {
        ref,
        className: cn(
          'my-6 ml-6 list-disc [&>li]:mt-2',
          type === 'ordered' && 'list-decimal',
          className
        ),
        ...props,
      },
      children
    );
  }
);

List.displayName = 'List';

export const ListItem = forwardRef<HTMLLIElement, TypographyProps>(
  ({ className, children, ...props }, ref) => (
    <li ref={ref} className={cn('', className)} {...props}>
      <Typography variant="body-md">{children}</Typography>
    </li>
  )
);

ListItem.displayName = 'ListItem';

/**
 * Utility Components
 */

/**
 * Truncated Text Component
 */
export interface TruncatedTextProps extends TypographyProps {
  maxLines?: number;
}

export const TruncatedText = forwardRef<HTMLSpanElement, TruncatedTextProps>(
  ({ maxLines = 1, className, children, ...props }, ref) => (
    <Typography
      ref={ref}
      lineClamp={maxLines as 1 | 2 | 3 | 4 | 5 | 6 | 'none'}
      className={className}
      {...props}
    >
      {children}
    </Typography>
  )
);

TruncatedText.displayName = 'TruncatedText';

/**
 * Highlight Text Component
 */
export const HighlightText = forwardRef<HTMLSpanElement, TypographyProps>(
  ({ className, children, ...props }, ref) => (
    <Typography
      ref={ref}
      as="mark"
      className={cn(
        'bg-yellow-200 text-yellow-900 px-1 py-0.5 rounded',
        'dark:bg-yellow-800 dark:text-yellow-100',
        className
      )}
      {...props}
    >
      {children}
    </Typography>
  )
);

HighlightText.displayName = 'HighlightText';

/**
 * Brazilian Portuguese specific typography utilities
 */
export const BrazilianTypography = {
  // Special components for Portuguese text patterns
  CPF: forwardRef<HTMLSpanElement, TypographyProps>((props, ref) => (
    <Typography ref={ref} as="span" className="font-mono text-sm" {...props} />
  )),

  CNPJ: forwardRef<HTMLSpanElement, TypographyProps>((props, ref) => (
    <Typography ref={ref} as="span" className="font-mono text-sm" {...props} />
  )),

  Currency: forwardRef<HTMLSpanElement, TypographyProps>(({ children, ...props }, ref) => (
    <Typography ref={ref} as="span" className="font-semibold tabular-nums" {...props}>
      R$ {children}
    </Typography>
  )),
};

BrazilianTypography.CPF.displayName = 'CPF';
BrazilianTypography.CNPJ.displayName = 'CNPJ';
BrazilianTypography.Currency.displayName = 'Currency';

export { Typography, typographyVariants };
export default Typography;
