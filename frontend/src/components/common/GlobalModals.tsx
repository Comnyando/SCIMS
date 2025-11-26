/**
 * Global Modals Component
 *
 * Centralized component that renders all global modals used throughout the application.
 * This provides a single place to manage all modal components.
 *
 * Each modal is self-contained and manages its own state via Zustand stores.
 */

import { LocationModal } from "../locations/modal";
import { ItemModal } from "../items/modal";
import { BlueprintModal } from "../blueprints/modal";
import { CraftModal } from "../crafts/modal";
import { InventoryModal } from "../inventory/modal";
import { AlertDialog } from "./AlertDialog";
import { useLocationModalStore } from "../../stores/locationModalStore";
import { useItemModalStore } from "../../stores/itemModalStore";
import { useBlueprintModalStore } from "../../stores/blueprintModalStore";
import { useCraftModalStore } from "../../stores/craftModalStore";
import { useInventoryModalStore } from "../../stores/inventoryModalStore";

/**
 * GlobalModals component that renders all global modals.
 * This should be included once in the App component.
 */
export function GlobalModals() {
  // Get modal visibility from stores
  const isLocationModalOpen = useLocationModalStore((state) => state.isOpen);
  const isItemModalOpen = useItemModalStore((state) => state.isOpen);
  const isBlueprintModalOpen = useBlueprintModalStore((state) => state.isOpen);
  const isCraftModalOpen = useCraftModalStore((state) => state.isOpen);
  const isInventoryModalOpen = useInventoryModalStore((state) => state.isOpen);

  return (
    <>
      {isLocationModalOpen && <LocationModal />}
      {isItemModalOpen && <ItemModal />}
      {isBlueprintModalOpen && <BlueprintModal />}
      {isCraftModalOpen && <CraftModal />}
      {isInventoryModalOpen && <InventoryModal />}
      <AlertDialog />
    </>
  );
}
