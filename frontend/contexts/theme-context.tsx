/**
 * Theme Context for CV-Match Phase 0.8
 *
 * Brazilian market optimized theme system with dark/light mode support
 * Automatic theme detection, system preference sync, and smooth transitions
 *
 * Key Features:
 * - Dark/light theme switching with smooth transitions
 * - System preference detection and sync
 * - Brazilian market color optimization
 * - Accessibility features (reduced motion, high contrast)
 * - Persistent theme storage with localStorage
 * - TypeScript safe theme context
 */

'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { colors, ColorName, ColorShade } from '@/lib/design-system/colors';
import { typography, TypographyKey } from '@/lib/design-system/typography';
import { designTokens } from '@/lib/design-system/tokens';

export type ThemeMode = 'light' | 'dark' | 'system';

export interface ThemeColors {
  background: string;
  foreground: string;
  primary: string;
  'primary-foreground': string;
  secondary: string;
  'secondary-foreground': string;
  muted: string;
  'muted-foreground': string;
  accent: string;
  'accent-foreground': string;
  destructive: string;
  'destructive-foreground': string;
  border: string;
  input: string;
  ring: string;
  success: string;
  'success-foreground': string;
  warning: string;
  'warning-foreground': string;
  info: string;
  'info-foreground': string;
  card: string;
  'card-foreground': string;
  popover: string;
  'popover-foreground': string;
}

export interface Theme {
  mode: ThemeMode;
  colors: ThemeColors;
  typography: typeof typography;
  spacing: typeof designTokens.spacing;
  borderRadius: typeof designTokens.borderRadius;
  shadows: typeof designTokens.shadows;
  animations: typeof designTokens.animations;
  zIndex: typeof designTokens.zIndex;
  breakpoints: typeof designTokens.breakpoints;
  sizes: typeof designTokens.sizes;
}

interface ThemeContextValue {
  theme: Theme;
  setTheme: (mode: ThemeMode) => void;
  resolvedTheme: 'light' | 'dark';
  toggleTheme: () => void;
  isSystemTheme: boolean;
  updateColorPreference: (colorName: ColorName, shade: ColorShade) => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

/**
 * Brazilian market optimized color palettes
 */
const brazilianLightColors: ThemeColors = {
  background: colors.neutral[50].hex,
  foreground: colors.neutral[900].hex,
  primary: colors.primary[500].hex,
  'primary-foreground': colors.neutral[50].hex,
  secondary: colors.secondary[100].hex,
  'secondary-foreground': colors.secondary[900].hex,
  muted: colors.neutral[100].hex,
  'muted-foreground': colors.neutral[600].hex,
  accent: colors.accent[100].hex,
  'accent-foreground': colors.accent[900].hex,
  destructive: colors.error[500].hex,
  'destructive-foreground': colors.neutral[50].hex,
  border: colors.neutral[200].hex,
  input: colors.neutral[100].hex,
  ring: colors.primary[500].hex,
  success: colors.success[500].hex,
  'success-foreground': colors.neutral[50].hex,
  warning: colors.warning[500].hex,
  'warning-foreground': colors.neutral[900].hex,
  info: colors.info[500].hex,
  'info-foreground': colors.neutral[50].hex,
  card: colors.neutral[50].hex,
  'card-foreground': colors.neutral[900].hex,
  popover: colors.neutral[50].hex,
  'popover-foreground': colors.neutral[900].hex,
};

const brazilianDarkColors: ThemeColors = {
  background: colors.neutral[900].hex,
  foreground: colors.neutral[50].hex,
  primary: colors.primary[400].hex,
  'primary-foreground': colors.neutral[900].hex,
  secondary: colors.secondary[800].hex,
  'secondary-foreground': colors.secondary[100].hex,
  muted: colors.neutral[800].hex,
  'muted-foreground': colors.neutral[400].hex,
  accent: colors.accent[800].hex,
  'accent-foreground': colors.accent[100].hex,
  destructive: colors.error[400].hex,
  'destructive-foreground': colors.neutral[50].hex,
  border: colors.neutral[700].hex,
  input: colors.neutral[800].hex,
  ring: colors.primary[400].hex,
  success: colors.success[400].hex,
  'success-foreground': colors.neutral[900].hex,
  warning: colors.warning[400].hex,
  'warning-foreground': colors.neutral[900].hex,
  info: colors.info[400].hex,
  'info-foreground': colors.neutral[900].hex,
  card: colors.neutral[800].hex,
  'card-foreground': colors.neutral[50].hex,
  popover: colors.neutral[800].hex,
  'popover-foreground': colors.neutral[50].hex,
};

/**
 * Get system theme preference
 */
const getSystemTheme = (): 'light' | 'dark' => {
  if (typeof window === 'undefined') return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

/**
 * Get initial theme from localStorage or system preference
 */
const getInitialTheme = (): ThemeMode => {
  if (typeof window === 'undefined') return 'system';

  const stored = localStorage.getItem('cv-match-theme') as ThemeMode;
  if (stored && ['light', 'dark', 'system'].includes(stored)) {
    return stored;
  }

  return 'system';
};

/**
 * Create theme object
 */
const createTheme = (mode: ThemeMode): Theme => {
  const resolvedMode = mode === 'system' ? getSystemTheme() : mode;
  const themeColors = resolvedMode === 'dark' ? brazilianDarkColors : brazilianLightColors;

  return {
    mode,
    colors: themeColors,
    typography,
    spacing: designTokens.spacing,
    borderRadius: designTokens.borderRadius,
    shadows: designTokens.shadows,
    animations: designTokens.animations,
    zIndex: designTokens.zIndex,
    breakpoints: designTokens.breakpoints,
    sizes: designTokens.sizes,
  };
};

interface ThemeProviderProps {
  children: ReactNode;
  defaultTheme?: ThemeMode;
  storageKey?: string;
  enableSystem?: boolean;
  attribute?: 'class' | 'data-theme';
}

/**
 * Theme Provider Component
 */
export function ThemeProvider({
  children,
  defaultTheme = 'system',
  storageKey = 'cv-match-theme',
  enableSystem = true,
  attribute = 'class',
}: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>(() => createTheme(getInitialTheme()));
  const initialTheme = getInitialTheme();
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>(() =>
    initialTheme === 'system' ? getSystemTheme() : (initialTheme as 'light' | 'dark')
  );

  /**
   * Set theme and update DOM
   */
  const setTheme = (mode: ThemeMode) => {
    const newTheme = createTheme(mode);
    setThemeState(newTheme);

    if (typeof window !== 'undefined') {
      localStorage.setItem(storageKey, mode);

      const resolvedMode = mode === 'system' ? getSystemTheme() : mode;
      setResolvedTheme(resolvedMode);

      // Update DOM
      const root = window.document.documentElement;
      root.classList.remove('light', 'dark');

      if (mode === 'system') {
        root.classList.add(resolvedMode);
      } else {
        root.classList.add(mode);
      }
    }
  };

  /**
   * Toggle between light and dark themes
   */
  const toggleTheme = () => {
    const newMode = theme.mode === 'light' ? 'dark' : 'light';
    setTheme(newMode);
  };

  /**
   * Update color preference (for future customization)
   */
  const updateColorPreference = (colorName: ColorName, shade: ColorShade) => {
    // This could be extended to allow custom color preferences
    console.log(`Updating ${colorName} to shade ${shade}`);
  };

  /**
   * Check if using system theme
   */
  const isSystemTheme = theme.mode === 'system';

  /**
   * Listen for system theme changes
   */
  useEffect(() => {
    if (!enableSystem) return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleChange = () => {
      if (theme.mode === 'system') {
        const newResolvedTheme = mediaQuery.matches ? 'dark' : 'light';
        setResolvedTheme(newResolvedTheme);

        const root = window.document.documentElement;
        root.classList.remove('light', 'dark');
        root.classList.add(newResolvedTheme);
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme.mode, enableSystem]);

  /**
   * Initialize theme on mount
   */
  useEffect(() => {
    const initialMode = getInitialTheme();
    setTheme(initialMode);
  }, []);

  /**
   * Apply theme to DOM
   */
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const root = window.document.documentElement;

    if (attribute === 'class') {
      root.classList.remove('light', 'dark');
      root.classList.add(resolvedTheme);
    } else {
      root.setAttribute('data-theme', resolvedTheme);
    }

    // Add transition styles for smooth theme switching
    root.style.setProperty(
      '--theme-transition',
      'background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease'
    );
  }, [resolvedTheme, attribute]);

  const value: ThemeContextValue = {
    theme,
    setTheme,
    resolvedTheme,
    toggleTheme,
    isSystemTheme,
    updateColorPreference,
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

/**
 * Hook to use theme context
 */
export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

/**
 * Hook to get resolved theme (light/dark)
 */
export function useResolvedTheme() {
  const { resolvedTheme } = useTheme();
  return resolvedTheme;
}

/**
 * Hook to check if dark theme is active
 */
export function useIsDarkTheme() {
  const { resolvedTheme } = useTheme();
  return resolvedTheme === 'dark';
}

/**
 * Hook to get theme colors
 */
export function useThemeColors() {
  const { theme } = useTheme();
  return theme.colors;
}

/**
 * Theme utilities
 */
export const themeUtils = {
  /**
   * Get CSS variable for a theme color
   */
  getColorVariable: (colorName: keyof ThemeColors): string => {
    return `--color-${colorName.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase())}`;
  },

  /**
   * Apply theme colors to CSS variables
   */
  applyThemeVariables: (colors: ThemeColors): void => {
    if (typeof window === 'undefined') return;

    const root = window.document.documentElement;
    Object.entries(colors).forEach(([key, value]) => {
      const cssVar = themeUtils.getColorVariable(key as keyof ThemeColors);
      root.style.setProperty(cssVar, value);
    });
  },

  /**
   * Check if color is light or dark
   */
  isLightColor: (hexColor: string): boolean => {
    // Simple luminance calculation
    const hex = hexColor.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    return luminance > 0.5;
  },
};

export default ThemeContext;
