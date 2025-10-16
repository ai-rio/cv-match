/**
 * WCAG 2.1 AA Accessibility Utilities for CV-Match Phase 0.8
 *
 * Brazilian market optimized accessibility framework
 * Comprehensive WCAG testing and validation utilities
 *
 * Features:
 * - WCAG 2.1 AA compliance checking
 * - Color contrast validation
 * - Keyboard navigation testing
 * - Screen reader optimization
 * - Focus management
 * - ARIA validation
 * - Brazilian Portuguese accessibility support
 */

import { colors, ColorToken } from '@/lib/design-system/colors';

/**
 * WCAG 2.1 AA Standards
 */
export const WCAG_STANDARDS = {
  // Contrast ratios
  CONTRAST: {
    AA_NORMAL: 4.5, // 1:4.5 for normal text
    AA_LARGE: 3.0, // 1:3 for large text (18pt+ or 14pt+ bold)
    AAA_NORMAL: 7.0, // 1:7 for enhanced contrast
    AAA_LARGE: 4.5, // 1:4.5 for large text enhanced
    AA_GRAPHICS: 3.0, // 1:3 for graphical objects
  },

  // Touch target sizes
  TOUCH_TARGET: {
    MINIMUM: 44, // 44x44px minimum (WCAG recommendation)
    RECOMMENDED: 48, // 48x48px recommended
  },

  // Font sizes
  FONT_SIZES: {
    LARGE_TEXT: 18, // 18pt or larger
    LARGE_TEXT_BOLD: 14, // 14pt or larger if bold
  },

  // Timing
  TIME_LIMITS: {
    AUTO_HIDE: 5000, // 5 seconds for auto-dismissing content
    WARNING: 20, // 20 seconds before timeout
  },
} as const;

/**
 * Color contrast calculation utilities
 */

/**
 * Calculate relative luminance of a color
 */
export function calculateLuminance(hexColor: string): number {
  // Remove # if present
  const hex = hexColor.replace('#', '');

  // Convert to RGB
  const r = parseInt(hex.substr(0, 2), 16) / 255;
  const g = parseInt(hex.substr(2, 2), 16) / 255;
  const b = parseInt(hex.substr(4, 2), 16) / 255;

  // Apply gamma correction
  const gammaCorrect = (value: number) =>
    value <= 0.03928 ? value / 12.92 : Math.pow((value + 0.055) / 1.055, 2.4);

  const R = gammaCorrect(r);
  const G = gammaCorrect(g);
  const B = gammaCorrect(b);

  // Calculate luminance
  return 0.2126 * R + 0.7152 * G + 0.0722 * B;
}

/**
 * Calculate contrast ratio between two colors
 */
export function calculateContrastRatio(color1: string, color2: string): number {
  const lum1 = calculateLuminance(color1);
  const lum2 = calculateLuminance(color2);

  const brightest = Math.max(lum1, lum2);
  const darkest = Math.min(lum1, lum2);

  return (brightest + 0.05) / (darkest + 0.05);
}

/**
 * Check WCAG compliance for color contrast
 */
export interface ContrastResult {
  ratio: number;
  passesAA: boolean;
  passesAAA: boolean;
  passesAALarge: boolean;
  passesAAALarge: boolean;
  recommendation: string;
}

export function checkContrastCompliance(
  foreground: string,
  background: string,
  isLargeText = false
): ContrastResult {
  const ratio = calculateContrastRatio(foreground, background);

  const passesAA = ratio >= WCAG_STANDARDS.CONTRAST.AA_NORMAL;
  const passesAAA = ratio >= WCAG_STANDARDS.CONTRAST.AAA_NORMAL;
  const passesAALarge = ratio >= WCAG_STANDARDS.CONTRAST.AA_LARGE;
  const passesAAALarge = ratio >= WCAG_STANDARDS.CONTRAST.AAA_LARGE;

  let recommendation = '';
  if (!passesAA) {
    recommendation = `Contrast ratio of ${ratio.toFixed(2)}:1 is too low. WCAG AA requires ${WCAG_STANDARDS.CONTRAST.AA_NORMAL}:1 for normal text.`;
  } else if (!passesAAA) {
    recommendation = `Contrast ratio of ${ratio.toFixed(2)}:1 meets AA but not AAA standards. AAA requires ${WCAG_STANDARDS.CONTRAST.AAA_NORMAL}:1 for normal text.`;
  } else {
    recommendation = `Excellent contrast ratio of ${ratio.toFixed(2)}:1 meets WCAG AAA standards.`;
  }

  return {
    ratio,
    passesAA: isLargeText ? passesAALarge : passesAA,
    passesAAA: isLargeText ? passesAAALarge : passesAAA,
    passesAALarge,
    passesAAALarge,
    recommendation,
  };
}

/**
 * Validate design system colors against WCAG standards
 */
export function validateDesignSystemColors(): Record<string, ContrastResult[]> {
  const results: Record<string, ContrastResult[]> = {};

  Object.entries(colors).forEach(([colorName, colorScale]) => {
    results[colorName] = [];

    // Test against light and dark backgrounds
    const lightBg = '#ffffff';
    const darkBg = '#000000';

    // Test key shades
    const keyShades = [50, 100, 500, 700, 900] as const;

    keyShades.forEach((shade) => {
      const color = colorScale[shade];
      results[colorName].push({
        shade,
        light: checkContrastCompliance(color.hex, lightBg),
        dark: checkContrastCompliance(color.hex, darkBg),
      } as any);
    });
  });

  return results;
}

/**
 * Focus management utilities
 */

/**
 * Check if element is focusable
 */
export function isFocusable(element: HTMLElement): boolean {
  if (!element || ('disabled' in element && element.disabled)) return false;

  const focusableTags = ['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA', 'DETAILS'];
  const isFocusableTag = focusableTags.includes(element.tagName);
  const hasTabIndex = element.hasAttribute('tabindex') && element.getAttribute('tabindex') !== '-1';
  const isContentEditable = element.getAttribute('contenteditable') === 'true';

  return isFocusableTag || hasTabIndex || isContentEditable;
}

/**
 * Get all focusable elements in a container
 */
export function getFocusableElements(container: HTMLElement): HTMLElement[] {
  const focusableSelectors = [
    'a[href]',
    'button:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
    '[contenteditable="true"]',
    'details summary',
    'iframe',
    'embed',
    'object',
  ].join(', ');

  return Array.from(container.querySelectorAll(focusableSelectors)).filter((element) =>
    isFocusable(element as HTMLElement)
  ) as HTMLElement[];
}

/**
 * Trap focus within a container (for modals, dialogs)
 */
export function createFocusTrap(container: HTMLElement) {
  const focusableElements = getFocusableElements(container);
  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];

  const handleTabKey = (e: KeyboardEvent) => {
    if (e.key !== 'Tab') return;

    if (e.shiftKey) {
      // Shift + Tab
      if (document.activeElement === firstElement) {
        e.preventDefault();
        lastElement?.focus();
      }
    } else {
      // Tab
      if (document.activeElement === lastElement) {
        e.preventDefault();
        firstElement?.focus();
      }
    }
  };

  // Add event listener
  container.addEventListener('keydown', handleTabKey);

  // Return cleanup function
  return () => {
    container.removeEventListener('keydown', handleTabKey);
  };
}

/**
 * Keyboard navigation utilities
 */

/**
 * Check keyboard navigation support
 */
export interface KeyboardNavigationResult {
  hasKeyboardAccess: boolean;
  missingTabIndex: string[];
  missingKeyHandlers: string[];
  recommendations: string[];
}

export function checkKeyboardNavigation(container: HTMLElement): KeyboardNavigationResult {
  const interactiveElements = container.querySelectorAll(
    'button, a, input, select, textarea, [tabindex]'
  );
  const missingTabIndex: string[] = [];
  const missingKeyHandlers: string[] = [];

  interactiveElements.forEach((element) => {
    const el = element as HTMLElement;

    // Check for tabindex
    if (
      !el.hasAttribute('tabindex') &&
      !['button', 'a', 'input', 'select', 'textarea'].includes(el.tagName.toLowerCase())
    ) {
      missingTabIndex.push(
        el.tagName + (el.className ? '.' + el.className.split(' ').join('.') : '')
      );
    }

    // Check for keyboard event handlers on interactive elements
    if (el.tagName === 'button' && !el.hasAttribute('onclick') && !el.hasAttribute('onkeydown')) {
      missingKeyHandlers.push('button');
    }
  });

  const recommendations: string[] = [];

  if (missingTabIndex.length > 0) {
    recommendations.push(`Add tabindex to interactive elements: ${missingTabIndex.join(', ')}`);
  }

  if (missingKeyHandlers.length > 0) {
    recommendations.push(`Add keyboard event handlers to: ${missingKeyHandlers.join(', ')}`);
  }

  return {
    hasKeyboardAccess: missingTabIndex.length === 0 && missingKeyHandlers.length === 0,
    missingTabIndex,
    missingKeyHandlers,
    recommendations,
  };
}

/**
 * ARIA validation utilities
 */

/**
 * Check ARIA attributes
 */
export interface ARIAViolation {
  element: string;
  violation: string;
  severity: 'error' | 'warning';
  recommendation: string;
}

export function validateARIA(container: HTMLElement): ARIAViolation[] {
  const violations: ARIAViolation[] = [];

  // Check for missing alt text on images
  const images = container.querySelectorAll('img:not([alt])');
  images.forEach((img) => {
    violations.push({
      element: 'img',
      violation: 'Missing alt attribute',
      severity: 'error',
      recommendation: 'Add descriptive alt text for screen readers',
    });
  });

  // Check for improper ARIA usage
  const elementsWithARIA = container.querySelectorAll(
    '[aria-label], [aria-labelledby], [aria-describedby]'
  );
  elementsWithARIA.forEach((element) => {
    const el = element as HTMLElement;

    if (el.hasAttribute('aria-label') && !el.getAttribute('aria-label')?.trim()) {
      violations.push({
        element: el.tagName.toLowerCase(),
        violation: 'Empty aria-label',
        severity: 'warning',
        recommendation: 'Provide meaningful aria-label or remove empty attribute',
      });
    }
  });

  // Check for proper heading structure
  const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6');
  const headingLevels = Array.from(headings).map((h) => parseInt(h.tagName.substring(1)));

  for (let i = 1; i < headingLevels.length; i++) {
    if (headingLevels[i] - headingLevels[i - 1] > 1) {
      violations.push({
        element: `h${headingLevels[i]}`,
        violation: 'Skipped heading level',
        severity: 'warning',
        recommendation: 'Do not skip heading levels (e.g., h1 to h3)',
      });
    }
  }

  return violations;
}

/**
 * Brazilian Portuguese accessibility utilities
 */

/**
 * Portuguese language validation
 */
export function validatePortugueseLanguage(container: HTMLElement): {
  hasLangAttribute: boolean;
  hasCorrectDirection: boolean;
  recommendations: string[];
} {
  const html = document.documentElement;
  const hasLangAttribute = html.hasAttribute('lang');
  const lang = html.getAttribute('lang');
  const hasCorrectDirection = html.getAttribute('dir') !== 'rtl';

  const recommendations: string[] = [];

  if (!hasLangAttribute || !lang?.startsWith('pt')) {
    recommendations.push('Add lang="pt-BR" to HTML element for Brazilian Portuguese');
  }

  if (!hasCorrectDirection) {
    recommendations.push('Ensure text direction is LTR for Portuguese');
  }

  // Check for Portuguese-specific accessibility issues
  const portugueseText = container.textContent || '';

  // Check for proper Portuguese abbreviations with periods
  const abbreviations = ['Sr', 'Sra', 'Dr', 'Dra', 'Prof', 'Exmo', 'Exma'];
  abbreviations.forEach((abbr) => {
    if (portugueseText.includes(abbr + ' ')) {
      recommendations.push(`Add period to abbreviation "${abbr}" -> "${abbr}." for screen readers`);
    }
  });

  return {
    hasLangAttribute,
    hasCorrectDirection,
    recommendations,
  };
}

/**
 * Touch target validation
 */

/**
 * Check touch target sizes
 */
export function validateTouchTargets(container: HTMLElement): {
  validTargets: string[];
  invalidTargets: { element: string; size: number; recommendation: string }[];
  recommendations: string[];
} {
  const interactiveElements = container.querySelectorAll('button, a, input, [role="button"]');
  const validTargets: string[] = [];
  const invalidTargets: {
    element: string;
    size: number;
    recommendation: string;
  }[] = [];

  interactiveElements.forEach((element) => {
    const el = element as HTMLElement;
    const rect = el.getBoundingClientRect();
    const size = Math.min(rect.width, rect.height);

    if (size >= WCAG_STANDARDS.TOUCH_TARGET.MINIMUM) {
      validTargets.push(el.tagName.toLowerCase());
    } else {
      invalidTargets.push({
        element: el.tagName.toLowerCase(),
        size,
        recommendation: `Increase touch target to at least ${WCAG_STANDARDS.TOUCH_TARGET.MINIMUM}px`,
      });
    }
  });

  const recommendations: string[] = [];
  if (invalidTargets.length > 0) {
    recommendations.push(`${invalidTargets.length} touch targets are too small for accessibility`);
  }

  return {
    validTargets,
    invalidTargets,
    recommendations,
  };
}

/**
 * Comprehensive accessibility audit
 */

export interface AccessibilityAuditResult {
  contrast: ContrastResult[];
  keyboardNavigation: KeyboardNavigationResult;
  aria: ARIAViolation[];
  portugueseLanguage: ReturnType<typeof validatePortugueseLanguage>;
  touchTargets: ReturnType<typeof validateTouchTargets>;
  overallScore: number;
  criticalIssues: ARIAViolation[];
  recommendations: string[];
}

export function runAccessibilityAudit(
  container: HTMLElement = document.body
): AccessibilityAuditResult {
  // Run all checks
  const ariaViolations = validateARIA(container);
  const keyboardNav = checkKeyboardNavigation(container);
  const portugueseLang = validatePortugueseLanguage(container);
  const touchTargets = validateTouchTargets(container);

  // Calculate overall score
  const maxScore = 100;
  let score = maxScore;

  // Deduct points for violations
  score -= ariaViolations.filter((v) => v.severity === 'error').length * 10;
  score -= ariaViolations.filter((v) => v.severity === 'warning').length * 5;
  score -= keyboardNav.missingTabIndex.length * 3;
  score -= keyboardNav.missingKeyHandlers.length * 3;
  score -= touchTargets.invalidTargets.length * 2;
  score -= portugueseLang.recommendations.length * 1;

  score = Math.max(0, Math.min(maxScore, score));

  const criticalIssues = ariaViolations.filter((v) => v.severity === 'error');

  const allRecommendations = [
    ...ariaViolations.map((v) => v.recommendation),
    ...keyboardNav.recommendations,
    ...portugueseLang.recommendations,
    ...touchTargets.recommendations,
  ];

  return {
    contrast: [], // Would need to implement color scanning
    keyboardNavigation: keyboardNav,
    aria: ariaViolations,
    portugueseLanguage: portugueseLang,
    touchTargets: touchTargets,
    overallScore: score,
    criticalIssues,
    recommendations: [...new Set(allRecommendations)], // Remove duplicates
  };
}

/**
 * Accessibility testing helpers
 */

/**
 * Announce messages to screen readers
 */
export function announceToScreenReader(
  message: string,
  priority: 'polite' | 'assertive' = 'polite'
) {
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;

  document.body.appendChild(announcement);

  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}

/**
 * Skip link implementation
 */
export function createSkipLink(href: string, text: string): HTMLAnchorElement {
  const skipLink = document.createElement('a');
  skipLink.href = href;
  skipLink.textContent = text;
  skipLink.className =
    'sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-primary text-primary-foreground px-4 py-2 rounded-md z-50';
  return skipLink;
}

/**
 * Brazilian market specific accessibility utilities
 */

export const BrazilianAccessibility = {
  // Brazilian Portuguese date format accessibility
  formatDateForScreenReader: (date: Date): string => {
    const options: Intl.DateTimeFormatOptions = {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      timeZone: 'America/Sao_Paulo',
    };
    return date.toLocaleDateString('pt-BR', options);
  },

  // Brazilian currency format accessibility
  formatCurrencyForScreenReader: (amount: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(amount);
  },

  // Brazilian phone number format
  formatPhoneForScreenReader: (phone: string): string => {
    // Remove non-numeric characters
    const clean = phone.replace(/\D/g, '');

    if (clean.length === 11) {
      // Mobile: XX XXXXX-XXXX
      return `${clean.slice(0, 2)} ${clean.slice(2, 7)}-${clean.slice(7)}`;
    } else if (clean.length === 10) {
      // Landline: XX XXXX-XXXX
      return `${clean.slice(0, 2)} ${clean.slice(2, 6)}-${clean.slice(6)}`;
    }

    return phone;
  },

  // Brazilian document format (CPF/CNPJ)
  formatDocumentForScreenReader: (doc: string, type: 'cpf' | 'cnpj'): string => {
    const clean = doc.replace(/\D/g, '');

    if (type === 'cpf' && clean.length === 11) {
      return `${clean.slice(0, 3)}.${clean.slice(3, 6)}.${clean.slice(6, 9)}-${clean.slice(9)}`;
    } else if (type === 'cnpj' && clean.length === 14) {
      return `${clean.slice(0, 2)}.${clean.slice(2, 5)}.${clean.slice(5, 8)}/${clean.slice(8, 12)}-${clean.slice(12)}`;
    }

    return doc;
  },
};

export default {
  WCAG_STANDARDS,
  calculateLuminance,
  calculateContrastRatio,
  checkContrastCompliance,
  validateDesignSystemColors,
  isFocusable,
  getFocusableElements,
  createFocusTrap,
  checkKeyboardNavigation,
  validateARIA,
  validatePortugueseLanguage,
  validateTouchTargets,
  runAccessibilityAudit,
  announceToScreenReader,
  createSkipLink,
  BrazilianAccessibility,
};
