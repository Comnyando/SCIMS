/**
 * Theme store for managing dark mode state.
 * Supports system preference detection and user preference persistence.
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { Classes } from "@blueprintjs/core";

export type ThemePreference = "light" | "dark" | "system";

interface ThemeStore {
  /** User's theme preference: 'light', 'dark', or 'system' */
  preference: ThemePreference;
  /** Current effective theme: 'light' or 'dark' */
  effectiveTheme: "light" | "dark";
  /** Set the theme preference */
  setPreference: (preference: ThemePreference) => void;
  /** Toggle between light and dark (ignores system preference) */
  toggleTheme: () => void;
  /** Update effective theme based on preference and system setting */
  updateEffectiveTheme: () => void;
}

/**
 * Get system theme preference.
 */
function getSystemTheme(): "light" | "dark" {
  if (typeof window === "undefined") return "light";
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

/**
 * Apply dark mode class to document body.
 */
function applyTheme(theme: "light" | "dark") {
  if (typeof document === "undefined") return;

  if (theme === "dark") {
    document.body.classList.add(Classes.DARK);
  } else {
    document.body.classList.remove(Classes.DARK);
  }
}

/**
 * Get effective theme based on preference.
 */
function getEffectiveTheme(preference: ThemePreference): "light" | "dark" {
  if (preference === "system") {
    return getSystemTheme();
  }
  return preference;
}

// System preference listener (set up once)
let systemThemeListener: ((e: MediaQueryListEvent) => void) | null = null;

function setupSystemThemeListener() {
  if (typeof window === "undefined" || systemThemeListener) return;

  const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
  systemThemeListener = () => {
    const state = useThemeStore.getState();
    if (state.preference === "system") {
      const newTheme = getSystemTheme();
      useThemeStore.setState({ effectiveTheme: newTheme });
      applyTheme(newTheme);
    }
  };
  mediaQuery.addEventListener("change", systemThemeListener);
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set, get) => {
      // Initialize with system preference
      const initialPreference: ThemePreference = "system";
      const initialEffectiveTheme = getEffectiveTheme(initialPreference);

      // Apply theme immediately if in browser
      if (typeof window !== "undefined") {
        applyTheme(initialEffectiveTheme);
        setupSystemThemeListener();
      }

      return {
        preference: initialPreference,
        effectiveTheme: initialEffectiveTheme,
        setPreference: (preference: ThemePreference) => {
          const effectiveTheme = getEffectiveTheme(preference);
          set({ preference, effectiveTheme });
          if (typeof window !== "undefined") {
            applyTheme(effectiveTheme);
            // Ensure listener is set up if switching to system
            if (preference === "system") {
              setupSystemThemeListener();
            }
          }
        },
        toggleTheme: () => {
          const state = get();
          const newTheme = state.effectiveTheme === "light" ? "dark" : "light";
          const newPreference: ThemePreference = newTheme; // Set explicit preference
          set({ preference: newPreference, effectiveTheme: newTheme });
          if (typeof window !== "undefined") {
            applyTheme(newTheme);
          }
        },
        updateEffectiveTheme: () => {
          const state = get();
          const effectiveTheme = getEffectiveTheme(
            state.preference || "system"
          );
          set({ effectiveTheme });
          if (typeof window !== "undefined") {
            applyTheme(effectiveTheme);
            if (state.preference === "system") {
              setupSystemThemeListener();
            }
          }
        },
      };
    },
    {
      name: "scims-theme-preference",
      // Only persist the preference, not the effective theme (it's computed)
      partialize: (state) => ({ preference: state.preference }),
      // On rehydration, update effective theme
      onRehydrateStorage: () => (state) => {
        if (state && typeof window !== "undefined") {
          // Update effective theme based on saved preference
          const preference = state.preference || "system";
          const effectiveTheme = getEffectiveTheme(preference);
          state.effectiveTheme = effectiveTheme;
          applyTheme(effectiveTheme);

          // Set up system preference listener if using system theme
          if (preference === "system") {
            setupSystemThemeListener();
          }
        }
      },
    }
  )
);
