/**
 * Centralized theme utility functions.
 * Provides easy access to theme-aware colors and styles.
 */

import { useMemo } from "react";
import { useThemeStore } from "../stores/themeStore";
import { colors } from "../styles/theme";

/**
 * Hook to get theme-aware styles.
 * Returns an object with commonly used theme-aware style properties.
 */
export function useThemeStyles() {
  const { effectiveTheme } = useThemeStore();

  return useMemo(
    () => ({
      // Background styles
      background: {
        primary: { backgroundColor: colors.background.primary },
        secondary: { backgroundColor: colors.background.secondary },
        tertiary: { backgroundColor: colors.background.tertiary },
      },
      // Text styles
      text: {
        primary: { color: colors.text.primary },
        secondary: { color: colors.text.secondary },
        muted: { color: colors.text.muted },
        inverse: { color: colors.text.inverse },
      },
      // Border styles
      border: {
        light: { borderColor: colors.border.light },
        medium: { borderColor: colors.border.medium },
        dark: { borderColor: colors.border.dark },
      },
      // Combined common styles
      card: {
        backgroundColor: colors.background.primary,
        borderRadius: "8px",
        padding: "16px",
      },
      viewField: {
        backgroundColor: colors.background.tertiary,
        borderRadius: "4px",
        padding: "8px",
      },
      codeBlock: {
        backgroundColor: colors.code.background,
        color: colors.code.text,
        borderRadius: "4px",
        padding: "16px",
      },
      // Theme info
      isDark: effectiveTheme === "dark",
      isLight: effectiveTheme === "light",
    }),
    [effectiveTheme]
  );
}

/**
 * Get theme-aware color values directly (for use outside React components).
 */
export function getThemeColors() {
  return colors;
}

/**
 * Common theme-aware style objects (for use in style props).
 */
export const themeStyles = {
  background: {
    primary: { backgroundColor: colors.background.primary },
    secondary: { backgroundColor: colors.background.secondary },
    tertiary: { backgroundColor: colors.background.tertiary },
  },
  text: {
    primary: { color: colors.text.primary },
    secondary: { color: colors.text.secondary },
    muted: { color: colors.text.muted },
  },
  viewField: {
    backgroundColor: colors.background.tertiary,
    borderRadius: "4px",
    padding: "8px",
    minHeight: "32px",
    display: "flex",
    alignItems: "center",
  },
  codeBlock: {
    backgroundColor: colors.code.background,
    color: colors.code.text,
    borderRadius: "4px",
    padding: "16px",
    overflow: "auto",
  },
} as const;
