/**
 * Global Modals Component
 *
 * Centralized component that renders all global modals used throughout the application.
 * This provides a single place to manage all modal components.
 *
 * Each modal is self-contained and manages its own state via Zustand stores.
 */

import { LocationModal } from "../locations/modal";
import { AlertDialog } from "./AlertDialog";
import { useLocationModalStore } from "../../stores/locationModalStore";
import { useAlertStore } from "../../stores/alertStore";

/**
 * GlobalModals component that renders all global modals.
 * This should be included once in the App component.
 */
export function GlobalModals() {
  // Get modal visibility from stores
  const isLocationModalOpen = useLocationModalStore((state) => state.isOpen);
  const isAlertOpen = useAlertStore((state) => state.alert.isOpen);

  return (
    <>
      {isLocationModalOpen && <LocationModal />}
      {isAlertOpen && <AlertDialog />}
      {/* Add other global modals here as they are created */}
    </>
  );
}
