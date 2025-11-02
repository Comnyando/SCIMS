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

export const colors = {
  text: {
    primary: "#293742",
    secondary: "#5C7080",
    muted: "#8A9BA8",
    inverse: "#F5F8FA",
  },
  background: {
    primary: "#FFFFFF",
    secondary: "#F5F8FA",
    tertiary: "#EBF1F5",
  },
  border: {
    light: "#E1E8ED",
    medium: "#CED9E0",
    dark: "#8A9BA8",
  },
  success: "#0F9960",
  warning: "#D9822B",
  danger: "#DB3737",
    dark: "#A7B6C2",
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

