/**
 * Design System Entry Point for CV-Match Phase 0.8
 *
 * Brazilian market optimized design system
 * Complete design tokens and component library
 *
 * This file exports all design system components and utilities
 * for easy integration across the application.
 */

// Color system
export * from './colors';

// Typography system
export * from './typography';

// Design tokens
export * from './tokens';

// Theme context and provider
export {
  type Theme,
  type ThemeColors,
  type ThemeMode,
  ThemeProvider,
  themeUtils,
  useIsDarkTheme,
  useResolvedTheme,
  useTheme,
  useThemeColors,
} from '../../contexts/theme-context';

// Accessibility utilities
export * from '../accessibility/wcag-utils';

// Re-export commonly used combinations are already included above
export {
  calculateContrastRatio,
  checkContrastCompliance,
  runAccessibilityAudit,
  WCAG_STANDARDS,
} from '../accessibility/wcag-utils';

// Utility functions for design system usage
export const designSystemUtils = {
  /**
   * Get CSS custom property for design token
   */
  getToken: (category: string, name: string, scale?: string): string => {
    const token = scale ? `--${category}-${name}-${scale}` : `--${category}-${name}`;
    return `var(${token})`;
  },

  /**
   * Apply design system colors to CSS variables
   */
  applyColorVariables: (container?: HTMLElement) => {
    const target = container || document.documentElement;
    // This would be implemented with actual color tokens
    // TODO: Implement proper color variable application
  },

  /**
   * Get responsive value for Brazilian market
   */
  getResponsiveValue: <T>(mobile: T, tablet?: T, desktop?: T): string => {
    return `${mobile} ${tablet ? `md:${tablet}` : ''} ${desktop ? `lg:${desktop}` : ''}`.trim();
  },

  /**
   * Get Brazilian market specific spacing
   */
  getBrazilianSpacing: (multiplier: number = 1): string => {
    // Brazilian market prefers slightly more spacing for readability
    return `${0.25 * multiplier}rem`; // 4px base with multiplier
  },
};

export default designSystemUtils;
