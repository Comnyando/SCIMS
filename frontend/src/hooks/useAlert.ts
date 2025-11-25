/**
 * Hook for showing alerts and confirmations.
 * Provides a convenient API for using the alert store.
 */

import { useCallback } from "react";
import { Intent } from "@blueprintjs/core";
import { useAlertStore } from "../stores/alertStore";

/**
 * Hook for showing alerts and confirmations.
 *
 * @example
 * const { showAlert, showConfirm } = useAlert();
 *
 * // Show an alert
 * await showAlert({
 *   title: "Success",
 *   message: "Operation completed successfully",
 *   intent: Intent.SUCCESS
 * });
 *
 * // Show a confirmation
 * const confirmed = await showConfirm({
 *   title: "Delete Item",
 *   message: "Are you sure you want to delete this item?",
 *   intent: Intent.DANGER
 * });
 * if (confirmed) {
 *   // User confirmed
 * }
 */
export function useAlert() {
  const showAlert = useAlertStore((state) => state.showAlert);
  const showConfirm = useAlertStore((state) => state.showConfirm);

  const showError = useCallback(
    (title: string, message: string) => {
      return showAlert({
        title,
        message,
        intent: Intent.DANGER,
        confirmText: "OK",
      });
    },
    [showAlert]
  );

  const showSuccess = useCallback(
    (title: string, message: string) => {
      return showAlert({
        title,
        message,
        intent: Intent.SUCCESS,
        confirmText: "OK",
      });
    },
    [showAlert]
  );

  const showWarning = useCallback(
    (title: string, message: string) => {
      return showAlert({
        title,
        message,
        intent: Intent.WARNING,
        confirmText: "OK",
      });
    },
    [showAlert]
  );

  const showInfo = useCallback(
    (title: string, message: string) => {
      return showAlert({
        title,
        message,
        intent: Intent.PRIMARY,
        confirmText: "OK",
      });
    },
    [showAlert]
  );

  return {
    showAlert,
    showConfirm,
    showError,
    showSuccess,
    showWarning,
    showInfo,
  };
}
