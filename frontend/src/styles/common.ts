/**
 * Common CSS-in-JS styles and utilities.
 */

import { spacing, typography, borderRadius, shadows } from "./theme";

/**
 * Common page container styles for auth pages (login, register)
 */
export const authPageContainer = {
  minHeight: "100vh",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: spacing.xl,
  backgroundColor: "var(--scims-background-secondary)",
} as const;

/**
 * Common card styles for auth forms
 */
export const authCard = {
  width: "100%",
  maxWidth: "400px",
} as const;

/**
 * Common page header styles
 */
export const pageHeader = {
  marginBottom: spacing.lg,
} as const;

/**
 * Common section spacing
 */
export const sectionSpacing = {
  marginBottom: spacing.lg,
} as const;

/**
 * Common input group spacing
 */
export const inputGroupSpacing = {
  marginBottom: spacing.md,
} as const;

/**
 * Common flex container for filters/search
 */
export const filterRow = {
  display: "flex",
  gap: spacing.md,
  marginBottom: spacing.lg,
  flexWrap: "wrap" as const,
} as const;

/**
 * Common table container styles
 */
export const tableContainer = {
  backgroundColor: "var(--scims-background-primary)",
  borderRadius: borderRadius.lg,
  overflow: "hidden" as const,
  boxShadow: shadows.md,
} as const;

/**
 * Common pagination container
 */
export const paginationContainer = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginTop: spacing.md,
} as const;

/**
 * Common text styles
 */
export const textMuted = {
  color: "var(--scims-text-secondary)",
} as const;

export const textSecondary = {
  color: "var(--scims-text-muted)",
  fontSize: typography.fontSize.sm,
} as const;
