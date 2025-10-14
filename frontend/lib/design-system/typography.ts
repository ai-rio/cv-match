/**
 * Typography System for CV-Match Phase 0.8
 *
 * Brazilian Portuguese optimized typography with Inter font family
 * Supports Portuguese diacritics, accented characters, and special characters
 * Designed for excellent readability on both mobile and desktop
 *
 * Key Features:
 * - Inter font family optimized for UI and Portuguese text
 * - Responsive typography scale
 * - Brazilian Portuguese character support
 * - WCAG 2.1 AA compliant contrast and sizing
 * - Optimal line height and letter spacing for Portuguese
 */

export interface TypographyToken {
  fontFamily: string;
  fontSize: string;
  fontWeight: number;
  lineHeight: number;
  letterSpacing: number;
  fontSizeRem: number;
}

export interface TypographyScale {
  display: TypographyToken;
  h1: TypographyToken;
  h2: TypographyToken;
  h3: TypographyToken;
  h4: TypographyToken;
  h5: TypographyToken;
  h6: TypographyToken;
  'body-lg': TypographyToken;
  'body-md': TypographyToken;
  'body-sm': TypographyToken;
  'body-xs': TypographyToken;
  caption: TypographyToken;
  overline: TypographyToken;
  label: TypographyToken;
}

/**
 * Font Family Configuration
 * Optimized for Brazilian Portuguese character rendering
 */
export const fontFamilies = {
  // Primary font family - Inter
  // Excellent for UI, supports Portuguese diacritics perfectly
  sans: [
    'Inter var',
    'Inter',
    '-apple-system',
    'BlinkMacSystemFont',
    'Segoe UI',
    'Roboto',
    'Oxygen',
    'Ubuntu',
    'Cantarell',
    'Fira Sans',
    'Droid Sans',
    'Helvetica Neue',
    'Arial',
    'sans-serif',
  ].join(', '),

  // Monospace font for code and technical content
  mono: [
    'JetBrains Mono',
    'Fira Code',
    'Consolas',
    'Monaco',
    'Cascadia Code',
    'SF Mono',
    'Ubuntu Mono',
    'Roboto Mono',
    'Courier New',
    'monospace',
  ].join(', '),

  // Display font for headings (optional premium font)
  display: [
    'Inter Display',
    'Inter var',
    'Inter',
    '-apple-system',
    'BlinkMacSystemFont',
    'sans-serif',
  ].join(', '),
};

/**
 * Font Weights
 * Standardized weights available in Inter font family
 */
export const fontWeights = {
  thin: 100,
  extralight: 200,
  light: 300,
  normal: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
  extrabold: 800,
  black: 900,
} as const;

/**
 * Font Sizes - Responsive Typography Scale
 * Optimized for Brazilian Portuguese reading patterns
 * Mobile-first approach with desktop scaling
 */
export const fontSizes = {
  // Display typography
  display: {
    mobile: '2.5rem', // 40px
    desktop: '4rem', // 64px
  },
  h1: {
    mobile: '2rem', // 32px
    desktop: '3rem', // 48px
  },
  h2: {
    mobile: '1.75rem', // 28px
    desktop: '2.25rem', // 36px
  },
  h3: {
    mobile: '1.5rem', // 24px
    desktop: '1.875rem', // 30px
  },
  h4: {
    mobile: '1.25rem', // 20px
    desktop: '1.5rem', // 24px
  },
  h5: {
    mobile: '1.125rem', // 18px
    desktop: '1.25rem', // 20px
  },
  h6: {
    mobile: '1rem', // 16px
    desktop: '1.125rem', // 18px
  },

  // Body typography
  'body-lg': {
    mobile: '1.125rem', // 18px
    desktop: '1.25rem', // 20px
  },
  'body-md': {
    mobile: '1rem', // 16px
    desktop: '1.125rem', // 18px
  },
  'body-sm': {
    mobile: '0.875rem', // 14px
    desktop: '1rem', // 16px
  },
  'body-xs': {
    mobile: '0.75rem', // 12px
    desktop: '0.875rem', // 14px
  },

  // UI elements
  caption: '0.75rem', // 12px
  overline: '0.625rem', // 10px
  label: '0.875rem', // 14px
} as const;

/**
 * Line Heights - Optimized for Portuguese Text
 * Portuguese text benefits from slightly more line height than English
 * for better readability of accented characters and longer words
 */
export const lineHeights = {
  display: 1.1,
  h1: 1.2,
  h2: 1.25,
  h3: 1.3,
  h4: 1.35,
  h5: 1.4,
  h6: 1.4,
  'body-lg': 1.6,
  'body-md': 1.6,
  'body-sm': 1.5,
  'body-xs': 1.5,
  caption: 1.4,
  overline: 1.4,
  label: 1.4,
} as const;

/**
 * Letter Spacing - Brazilian Portuguese Optimized
 * Slightly increased spacing for better readability of accented characters
 */
export const letterSpacings = {
  display: -0.02,
  h1: -0.02,
  h2: -0.01,
  h3: 0,
  h4: 0,
  h5: 0,
  h6: 0,
  'body-lg': 0,
  'body-md': 0,
  'body-sm': 0.01,
  'body-xs': 0.02,
  caption: 0.02,
  overline: 0.1,
  label: 0.01,
} as const;

/**
 * Complete Typography Scale
 */
export const typography: TypographyScale = {
  display: {
    fontFamily: fontFamilies.display,
    fontSize: fontSizes.display.mobile,
    fontWeight: fontWeights.black,
    lineHeight: lineHeights.display,
    letterSpacing: letterSpacings.display,
    fontSizeRem: 4,
  },
  h1: {
    fontFamily: fontFamilies.display,
    fontSize: fontSizes.h1.mobile,
    fontWeight: fontWeights.bold,
    lineHeight: lineHeights.h1,
    letterSpacing: letterSpacings.h1,
    fontSizeRem: 3,
  },
  h2: {
    fontFamily: fontFamilies.display,
    fontSize: fontSizes.h2.mobile,
    fontWeight: fontWeights.semibold,
    lineHeight: lineHeights.h2,
    letterSpacing: letterSpacings.h2,
    fontSizeRem: 2.25,
  },
  h3: {
    fontFamily: fontFamilies.sans,
    fontSize: fontSizes.h3.mobile,
    fontWeight: fontWeights.semibold,
    lineHeight: lineHeights.h3,
    letterSpacing: letterSpacings.h3,
    fontSizeRem: 1.875,
  },
  h4: {
    fontFamily: fontFamilies.sans,
    fontSize: fontSizes.h4.mobile,
    fontWeight: fontWeights.semibold,
    lineHeight: lineHeights.h4,
    letterSpacing: letterSpacings.h4,
    fontSizeRem: 1.5,
  },
  h5: {
    fontFamily: fontFamilies.sans,
    fontSize: fontSizes.h5.mobile,
    fontWeight: fontWeights.medium,
    lineHeight: lineHeights.h5,
    letterSpacing: letterSpacings.h5,
    fontSizeRem: 1.25,
  },
  h6: {
    fontFamily: fontFamilies.sans,
    fontSize: fontSizes.h6.mobile,
    fontWeight: fontWeights.medium,
    lineHeight: lineHeights.h6,
    letterSpacing: letterSpacings.h6,
    fontSizeRem: 1.125,
  },
  'body-lg': {
    fontFamily: fontFamilies.sans,
    fontSize: fontSizes['body-lg'].mobile,
    fontWeight: fontWeights.normal,
    lineHeight: lineHeights['body-lg'],
    letterSpacing: letterSpacings['body-lg'],
    fontSizeRem: 1.25,
  },
  'body-md': {
    fontFamily: fontFamilies.sans,
    fontSize: fontSizes['body-md'].mobile,
    fontWeight: fontWeights.normal,
    lineHeight: lineHeights['body-md'],
    letterSpacing: letterSpacings['body-md'],
    fontSizeRem: 1.125,
  },
  'body-sm': {
    fontFamily: fontFamilies.sans,
    fontSize: fontSizes['body-sm'].mobile,
    fontWeight: fontWeights.normal,
    lineHeight: lineHeights['body-sm'],
    letterSpacing: letterSpacings['body-sm'],
    fontSizeRem: 1,
  },
  'body-xs': {
    fontFamily: fontFamilies.sans,
    fontSize: fontSizes['body-xs'].mobile,
    fontWeight: fontWeights.normal,
    lineHeight: lineHeights['body-xs'],
    letterSpacing: letterSpacings['body-xs'],
    fontSizeRem: 0.875,
  },
  caption: {
    fontFamily: fontFamilies.sans,
    fontSize: fontSizes.caption,
    fontWeight: fontWeights.normal,
    lineHeight: lineHeights.caption,
    letterSpacing: letterSpacings.caption,
    fontSizeRem: 0.75,
  },
  overline: {
    fontFamily: fontFamilies.sans,
    fontSize: fontSizes.overline,
    fontWeight: fontWeights.medium,
    lineHeight: lineHeights.overline,
    letterSpacing: letterSpacings.overline,
    fontSizeRem: 0.625,
  },
  label: {
    fontFamily: fontFamilies.sans,
    fontSize: fontSizes.label,
    fontWeight: fontWeights.medium,
    lineHeight: lineHeights.label,
    letterSpacing: letterSpacings.label,
    fontSizeRem: 0.875,
  },
};

/**
 * Typography Utilities
 */

/**
 * Get typography styles for a specific element
 */
export const getTypographyStyles = (element: keyof TypographyScale): TypographyToken => {
  return typography[element];
};

/**
 * Generate responsive typography classes
 */
export const getResponsiveTypography = (element: keyof TypographyScale) => {
  const styles = typography[element];
  const fontSizeEntry = fontSizes[element as keyof typeof fontSizes];
  const mobileSize =
    typeof fontSizeEntry === 'string' ? fontSizeEntry : fontSizeEntry?.mobile || styles.fontSize;
  const desktopSize =
    typeof fontSizeEntry === 'string' ? fontSizeEntry : fontSizeEntry?.desktop || styles.fontSize;

  return {
    fontFamily: styles.fontFamily,
    fontWeight: styles.fontWeight,
    lineHeight: styles.lineHeight,
    letterSpacing: styles.letterSpacing,
    fontSize: mobileSize,
    '@media (min-width: 768px)': {
      fontSize: desktopSize,
    },
  };
};

/**
 * Brazilian Portuguese specific typography optimizations
 */
export const brazilianTypographyOptimizations = {
  // Hyphenation for Portuguese text
  hyphenation: 'auto',

  // Language attribute for proper Portuguese rendering
  lang: 'pt-BR',

  // Text alignment optimizations for Portuguese
  textAlign: 'left' as const,

  // Common Portuguese text transformations
  textTransform: {
    uppercase: 'uppercase',
    lowercase: 'lowercase',
    capitalize: 'capitalize',
    'pt-br': 'none', // Portuguese doesn't typically use title case
  },
};

/**
 * Accessibility utilities
 */
export const typographyAccessibility = {
  // Minimum readable sizes according to WCAG
  minReadableSize: '16px', // 1rem

  // High contrast mode support
  highContrast: {
    fontFamily: fontFamilies.sans,
    fontSize: '18px', // Slightly larger for high contrast
    fontWeight: fontWeights.normal,
    lineHeight: 1.6,
  },

  // Reduced motion support
  reducedMotion: {
    transition: 'none',
  },
};

/**
 * Text content utilities for Brazilian Portuguese
 */
export const brazilianTextContent = {
  // Common Portuguese words that might need special handling
  longWords: [
    'extraordinariamente',
    'constitucionalmente',
    'internacionalização',
    'desenvolvimento',
    'profissionalização',
  ],

  // Diacritic support test strings
  diacriticTest: 'ÀÁÂÃÄÅàáâãäå Ææ Çç ÐÐÈÉÊËèéêë ÌÍÎÏìíîï Ññ ÒÓÔÕÖØòóôõöø ÙÚÛÜùúûü Ýýÿ Þþ',

  // Portuguese specific punctuation
  punctuation: {
    openingQuotes: '"«',
    closingQuotes: '"»',
    ellipsis: '...',
    emDash: '—',
    enDash: '–',
  },
};

export type TypographyKey = keyof TypographyScale;
export type FontWeight = (typeof fontWeights)[keyof typeof fontWeights];
export type FontFamily = keyof typeof fontFamilies;
