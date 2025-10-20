import { cn } from '@/lib/utils';

interface TypographyProps {
  children: React.ReactNode;
  className?: string;
}

// H1 - Hero Headlines
export function H1({ children, className }: TypographyProps) {
  return (
    <h1
      className={cn(
        'font-serif text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight',
        'text-foreground',
        className
      )}
    >
      {children}
    </h1>
  );
}

// H2 - Section Headers
export function H2({ children, className }: TypographyProps) {
  return (
    <h2
      className={cn(
        'font-sans text-2xl md:text-3xl font-semibold tracking-tight',
        'text-foreground',
        className
      )}
    >
      {children}
    </h2>
  );
}

// H3 - Subsection Headers
export function H3({ children, className }: TypographyProps) {
  return (
    <h3 className={cn('font-sans text-xl md:text-2xl font-semibold', 'text-foreground', className)}>
      {children}
    </h3>
  );
}

// H4 - Card Titles
export function H4({ children, className }: TypographyProps) {
  return (
    <h4 className={cn('font-sans text-lg md:text-xl font-semibold', 'text-foreground', className)}>
      {children}
    </h4>
  );
}

// Body - Paragraph Text
export function P({ children, className }: TypographyProps) {
  return (
    <p className={cn('font-sans text-base leading-normal', 'text-foreground', className)}>
      {children}
    </p>
  );
}

// Lead - Intro/Lead Paragraph
export function Lead({ children, className }: TypographyProps) {
  return (
    <p
      className={cn(
        'font-sans text-lg md:text-xl leading-relaxed',
        'text-muted-foreground',
        className
      )}
    >
      {children}
    </p>
  );
}

// Small - Fine Print
export function Small({ children, className }: TypographyProps) {
  return (
    <small className={cn('font-sans text-sm leading-none', 'text-muted-foreground', className)}>
      {children}
    </small>
  );
}

// Muted - Secondary Text
export function Muted({ children, className }: TypographyProps) {
  return <p className={cn('font-sans text-sm', 'text-muted-foreground', className)}>{children}</p>;
}

// Code - Inline Code
export function Code({ children, className }: TypographyProps) {
  return (
    <code
      className={cn(
        'font-mono text-sm',
        'relative rounded bg-muted px-[0.3rem] py-[0.2rem]',
        'text-foreground',
        className
      )}
    >
      {children}
    </code>
  );
}

// Blockquote
export function Blockquote({ children, className }: TypographyProps) {
  return (
    <blockquote
      className={cn(
        'font-serif text-lg italic',
        'border-l-4 border-primary pl-6',
        'text-muted-foreground',
        className
      )}
    >
      {children}
    </blockquote>
  );
}
