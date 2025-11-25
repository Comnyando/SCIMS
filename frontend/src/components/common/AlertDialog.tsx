/**
 * Alert and Confirmation Dialog Component
 *
 * A reusable dialog component for showing alerts and confirmations.
 * Uses Blueprint.js Alert component.
 */

import { Alert } from "@blueprintjs/core";
import { useAlertStore } from "../../stores/alertStore";

/**
 * AlertDialog component that renders alerts and confirmations.
 * Should be included in GlobalModals.
 */
export function AlertDialog() {
  const alert = useAlertStore((state) => state.alert);
  const handleConfirm = useAlertStore((state) => state.handleConfirm);
  const handleCancel = useAlertStore((state) => state.handleCancel);
  const closeAlert = useAlertStore((state) => state.closeAlert);

  // Determine if this is a confirmation (has cancel button) or just an alert
  const isConfirm = !!alert.onCancel;

  return (
    <Alert
      isOpen={alert.isOpen}
      onClose={closeAlert}
      onConfirm={handleConfirm}
      onCancel={isConfirm ? handleCancel : undefined}
      intent={alert.intent}
      icon={isConfirm ? "warning-sign" : undefined}
      confirmButtonText={alert.confirmText}
      cancelButtonText={isConfirm ? alert.cancelText : undefined}
    >
      <div>
        <strong>{alert.title}</strong>
        {alert.message && (
          <div style={{ marginTop: "8px" }}>{alert.message}</div>
        )}
      </div>
    </Alert>
  );
}
