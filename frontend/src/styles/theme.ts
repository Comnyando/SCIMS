/**
 * Standardized theme constants for consistent styling across the application.
 */

export const spacing = {
  xs: "0.25rem", // 4px
  sm: "0.5rem", // 8px
  md: "1rem", // 16px
  lg: "1.5rem", // 24px
  xl: "2rem", // 32px
  xxl: "3rem", // 48px
} as const;

export const typography = {
  fontSize: {
    xs: "0.75rem", // 12px
    sm: "0.875rem", // 14px
    base: "1rem", // 16px
    lg: "1.125rem", // 18px
    xl: "1.25rem", // 20px
    "2xl": "1.5rem", // 24px
    "3xl": "2rem", // 32px
    "4xl": "2.5rem", // 40px
  },
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },
} as const;

/**
 * Theme-aware color utilities that adapt to dark mode.
 * Uses custom CSS variables defined in theme-variables.css.
 */
export const colors = {
  // Text colors - use CSS variables that adapt to dark mode
  text: {
    primary: "var(--scims-text-primary)",
    secondary: "var(--scims-text-secondary)",
    muted: "var(--scims-text-muted)",
    inverse: "var(--scims-text-inverse)",
  },
  // Background colors - use CSS variables
  background: {
    primary: "var(--scims-background-primary)",
    secondary: "var(--scims-background-secondary)",
    tertiary: "var(--scims-background-tertiary)",
  },
  // Border colors
  border: {
    light: "var(--scims-border-light)",
    medium: "var(--scims-border-medium)",
    dark: "var(--scims-border-dark)",
  },
  // Intent colors (these are consistent across themes)
  success: "#0F9960",
  warning: "#D9822B",
  danger: "#DB3737",
  // Additional theme-aware colors
  code: {
    background: "var(--scims-code-background)",
    text: "var(--scims-text-primary)",
  },
} as const;

export const borderRadius = {
  sm: "2px",
  md: "4px",
  lg: "8px",
  xl: "12px",
} as const;

export const shadows = {
  sm: "0 1px 2px rgba(0, 0, 0, 0.05)",
  md: "0 2px 4px rgba(0, 0, 0, 0.1)",
  lg: "0 4px 8px rgba(0, 0, 0, 0.15)",
} as const;
