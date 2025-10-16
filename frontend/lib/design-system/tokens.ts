/**
 * Design System Tokens for CV-Match Phase 0.8
 *
 * Centralized design tokens for spacing, shadows, borders, and animations
 * Optimized for Brazilian market and modern web standards
 *
 * Key Features:
 * - Consistent spacing system based on 4px grid
 * - Brazilian market optimized sizing
 * - Modern shadow and elevation system
 * - Smooth animations with reduced motion support
 * - Mobile-first responsive design tokens
 */

import { colors } from './colors';
import { typography } from './typography';

/**
 * Spacing System - 4px Grid Base
 * Consistent spacing for Brazilian mobile-first design
 */
export const spacing = {
  0: '0',
  px: '1px',
  0.5: '0.125rem', // 2px
  1: '0.25rem', // 4px
  1.5: '0.375rem', // 6px
  2: '0.5rem', // 8px
  2.5: '0.625rem', // 10px
  3: '0.75rem', // 12px
  3.5: '0.875rem', // 14px
  4: '1rem', // 16px
  5: '1.25rem', // 20px
  6: '1.5rem', // 24px
  7: '1.75rem', // 28px
  8: '2rem', // 32px
  9: '2.25rem', // 36px
  10: '2.5rem', // 40px
  11: '2.75rem', // 44px
  12: '3rem', // 48px
  14: '3.5rem', // 56px
  16: '4rem', // 64px
  20: '5rem', // 80px
  24: '6rem', // 96px
  28: '7rem', // 112px
  32: '8rem', // 128px
  36: '9rem', // 144px
  40: '10rem', // 160px
  44: '11rem', // 176px
  48: '12rem', // 192px
  52: '13rem', // 208px
  56: '14rem', // 224px
  60: '15rem', // 240px
  64: '16rem', // 256px
  72: '18rem', // 288px
  80: '20rem', // 320px
  96: '24rem', // 384px
} as const;

/**
 * Container Sizes - Brazilian Mobile Optimized
 */
export const containers = {
  xs: '475px', // Small mobile
  sm: '640px', // Large mobile
  md: '768px', // Tablet
  lg: '1024px', // Small desktop
  xl: '1280px', // Desktop
  '2xl': '1536px', // Large desktop
} as const;

/**
 * Breakpoints - Brazilian Device Usage
 * Optimized for common Brazilian device sizes
 */
export const breakpoints = {
  sm: '640px', // Large mobile
  md: '768px', // Tablet
  lg: '1024px', // Small desktop
  xl: '1280px', // Desktop
  '2xl': '1536px', // Large desktop
} as const;

/**
 * Border Radius System
 */
export const borderRadius = {
  none: '0',
  sm: '0.125rem', // 2px
  base: '0.25rem', // 4px
  md: '0.375rem', // 6px
  lg: '0.5rem', // 8px
  xl: '0.75rem', // 12px
  '2xl': '1rem', // 16px
  '3xl': '1.5rem', // 24px
  full: '9999px',
} as const;

/**
 * Shadow System - Material Design Inspired
 */
export const shadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  base: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
  inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',

  // Brazilian theme specific shadows
  'brazilian-primary': '0 4px 14px 0 rgb(14 165 233 / 0.15)',
  'brazilian-success': '0 4px 14px 0 rgb(34 197 94 / 0.15)',
  'brazilian-warning': '0 4px 14px 0 rgb(245 158 11 / 0.15)',
  'brazilian-error': '0 4px 14px 0 rgb(239 68 68 / 0.15)',
} as const;

/**
 * Z-Index System
 */
export const zIndex = {
  hide: -1,
  auto: 'auto',
  base: 0,
  docked: 10,
  dropdown: 1000,
  sticky: 1100,
  banner: 1200,
  overlay: 1300,
  modal: 1400,
  popover: 1500,
  skipLink: 1600,
  toast: 1700,
  tooltip: 1800,
} as const;

/**
 * Animation System
 */
export const animations = {
  // Durations
  duration: {
    fast: '150ms',
    normal: '250ms',
    slow: '350ms',
    slower: '500ms',
  },

  // Timing functions
  easing: {
    linear: 'linear',
    ease: 'ease',
    easeIn: 'ease-in',
    easeOut: 'ease-out',
    easeInOut: 'ease-in-out',
    'bounce-in': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    'smooth-step': 'cubic-bezier(0.4, 0, 0.2, 1)',
  },

  // Keyframes
  keyframes: {
    'fade-in': {
      from: { opacity: '0' },
      to: { opacity: '1' },
    },
    'fade-out': {
      from: { opacity: '1' },
      to: { opacity: '0' },
    },
    'slide-up': {
      from: { transform: 'translateY(100%)', opacity: '0' },
      to: { transform: 'translateY(0)', opacity: '1' },
    },
    'slide-down': {
      from: { transform: 'translateY(-100%)', opacity: '0' },
      to: { transform: 'translateY(0)', opacity: '1' },
    },
    'slide-left': {
      from: { transform: 'translateX(100%)', opacity: '0' },
      to: { transform: 'translateX(0)', opacity: '1' },
    },
    'slide-right': {
      from: { transform: 'translateX(-100%)', opacity: '0' },
      to: { transform: 'translateX(0)', opacity: '1' },
    },
    'scale-in': {
      from: { transform: 'scale(0.9)', opacity: '0' },
      to: { transform: 'scale(1)', opacity: '1' },
    },
    'scale-out': {
      from: { transform: 'scale(1)', opacity: '1' },
      to: { transform: 'scale(0.9)', opacity: '0' },
    },
    bounce: {
      '0%, 20%, 53%, 80%, 100%': { transform: 'translate3d(0, 0, 0)' },
      '40%, 43%': { transform: 'translate3d(0, -30px, 0)' },
      '70%': { transform: 'translate3d(0, -15px, 0)' },
      '90%': { transform: 'translate3d(0, -4px, 0)' },
    },
    pulse: {
      '0%, 100%': { opacity: '1' },
      '50%': { opacity: '0.5' },
    },
    spin: {
      from: { transform: 'rotate(0deg)' },
      to: { transform: 'rotate(360deg)' },
    },
  },
} as const;

/**
 * Border System
 */
export const borders = {
  width: {
    0: '0px',
    1: '1px',
    2: '2px',
    4: '4px',
    8: '8px',
  },
  style: {
    solid: 'solid',
    dashed: 'dashed',
    dotted: 'dotted',
    double: 'double',
    groove: 'groove',
    ridge: 'ridge',
    inset: 'inset',
    outset: 'outset',
  },
} as const;

/**
 * Sizing System
 */
export const sizes = {
  // Icon sizes
  icon: {
    xs: '0.75rem', // 12px
    sm: '1rem', // 16px
    md: '1.25rem', // 20px
    lg: '1.5rem', // 24px
    xl: '2rem', // 32px
    '2xl': '2.5rem', // 40px
    '3xl': '3rem', // 48px
  },

  // Touch targets (minimum 44px for accessibility)
  touch: {
    sm: '2.75rem', // 44px
    md: '3rem', // 48px
    lg: '3.5rem', // 56px
    xl: '4rem', // 64px
  },

  // Component specific sizes
  button: {
    height: {
      sm: '2.25rem', // 36px
      md: '2.75rem', // 44px
      lg: '3rem', // 48px
      xl: '3.5rem', // 56px
    },
    padding: {
      sm: '0.5rem 1rem',
      md: '0.75rem 1.5rem',
      lg: '1rem 2rem',
      xl: '1.25rem 2.5rem',
    },
  },

  // Input sizes
  input: {
    height: {
      sm: '2.25rem', // 36px
      md: '2.75rem', // 44px
      lg: '3rem', // 48px
    },
    padding: {
      sm: '0.5rem 0.75rem',
      md: '0.75rem 1rem',
      lg: '1rem 1.25rem',
    },
  },
} as const;

/**
 * Brazilian Market Specific Tokens
 */
export const brazilianTokens = {
  // Localized spacing adjustments
  spacing: {
    // Extra space for Portuguese text (often longer than English)
    textPadding: '1.5rem',
    buttonSpacing: '1rem',
    cardSpacing: '1.5rem',
  },

  // Localized colors
  colors: {
    // Brazilian market preferred colors
    trust: colors.primary[500].hex,
    prosperity: colors.secondary[500].hex,
    energy: colors.accent[500].hex,
  },

  // Localized sizing
  sizing: {
    // Larger touch targets for mobile-first Brazilian users
    minTouchTarget: '44px',
    preferredButtonHeight: '48px',
    cardMinHeight: '120px',
  },
} as const;

/**
 * Responsive Design Utilities
 */
export const responsive = {
  // Mobile-first approach
  mobileFirst: true,

  // Container queries support
  container: {
    sm: containers.sm,
    md: containers.md,
    lg: containers.lg,
    xl: containers.xl,
    '2xl': containers['2xl'],
  },

  // Grid systems
  grid: {
    columns: 12,
    gap: spacing[4],
    maxWidth: containers.xl,
  },
} as const;

/**
 * Export all tokens for easy access
 */
export const designTokens = {
  spacing,
  containers,
  breakpoints,
  borderRadius,
  shadows,
  zIndex,
  animations,
  borders,
  sizes,
  colors,
  typography,
  brazilianTokens,
  responsive,
} as const;

export type SpacingKey = keyof typeof spacing;
export type BorderRadiusKey = keyof typeof borderRadius;
export type ShadowKey = keyof typeof shadows;
export type ZIndexKey = keyof typeof zIndex;
export type AnimationDuration = keyof typeof animations.duration;
export type AnimationEasing = keyof typeof animations.easing;
