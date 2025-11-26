/**
 * Inventory Adjustment/Transfer/View Modal Component
 *
 * A self-contained modal for viewing inventory, adjusting quantities, and transferring items.
 * Uses Zustand store for state management and handles all submission logic internally.
 */

import { useMemo } from "react";
import { FormGroup, InputGroup, TextArea } from "@blueprintjs/core";
import { EntityModal } from "../../common/EntityModal";
import { ViewEditField } from "../../common/ViewEditField";
import { EasySelect, type EasySelectOption } from "../../common/EasySelect";
import {
  useAdjustInventory,
  useTransferInventory,
} from "../../../hooks/mutations/inventory";
import { useInventoryModalStore } from "../../../stores/inventoryModalStore";
import { useItems } from "../../../hooks/queries/items";
import { useLocations } from "../../../hooks/queries/locations";
import type { Location } from "../../../types/location";

/**
 * Self-contained InventoryModal component.
 * Gets all state from Zustand store and handles submission internally.
 */
export function InventoryModal() {
  // Get all state and actions from store
  const {
    isOpen,
    action,
    stock,
    isSubmitting,
    error,
    itemId,
    locationId,
    quantityChange,
    notes,
    fromLocationId,
    toLocationId,
    transferQuantity,
    transferNotes,
    closeModal,
    setQuantityChange,
    setNotes,
    setToLocationId,
    setTransferQuantity,
    setTransferNotes,
    handleAdjust,
    handleTransfer,
  } = useInventoryModalStore();

  const isViewMode = action === "view";
  const isAdjustMode = action === "adjust";
  const isTransferMode = action === "transfer";

  // Fetch items and locations for dropdowns
  const { data: itemsData } = useItems({ skip: 0, limit: 1000 });
  const { data: locationsData } = useLocations({ skip: 0, limit: 1000 });
  const items = useMemo(() => itemsData?.items || [], [itemsData?.items]);
  const locations = useMemo(
    () => locationsData?.locations || [],
    [locationsData?.locations]
  );

  // Convert locations to EasySelect options (excluding fromLocationId for transfer mode)
  const locationOptions: EasySelectOption<Location>[] = useMemo(
    () =>
      locations
        .filter((loc) => !isTransferMode || loc.id !== fromLocationId)
        .map((loc) => ({
          value: loc.id,
          label: loc.name,
          secondaryText: loc.type,
          data: loc,
        })),
    [locations, isTransferMode, fromLocationId]
  );

  // Mutations for submission
  const adjustMutation = useAdjustInventory();
  const transferMutation = useTransferInventory();

  // Handle form submission
  const handleSubmit = async () => {
    if (isAdjustMode) {
      await handleAdjust((data) => adjustMutation.mutateAsync(data));
    } else if (isTransferMode) {
      await handleTransfer((data) => transferMutation.mutateAsync(data));
    }
  };

  const validateForm = (): boolean => {
    if (isAdjustMode) {
      if (!itemId || !locationId) return false;
      if (!quantityChange || parseFloat(quantityChange) === 0) return false;
      return true;
    } else if (isTransferMode) {
      if (!itemId || !fromLocationId || !toLocationId) return false;
      if (!transferQuantity || parseFloat(transferQuantity) <= 0) return false;
      if (fromLocationId === toLocationId) return false;
      return true;
    }
    return true;
  };

  const modalTitle = isViewMode
    ? `View Inventory: ${stock?.item_name || ""}`
    : isAdjustMode
    ? "Adjust Inventory"
    : "Transfer Inventory";

  const getItemName = (id: string): string => {
    const item = items.find((i) => i.id === id);
    return item?.name || id || "—";
  };

  const getLocationName = (id: string): string => {
    const loc = locations.find((l) => l.id === id);
    return loc?.name || id || "—";
  };

  return (
    <EntityModal
      isOpen={isOpen}
      onClose={closeModal}
      title={modalTitle}
      mode={isViewMode ? "view" : "edit"}
      canEdit={!isViewMode}
      submitText={
        isAdjustMode ? "Adjust" : isTransferMode ? "Transfer" : undefined
      }
      onSubmit={isViewMode ? undefined : handleSubmit}
      isSubmitting={isSubmitting}
      error={error}
      isSubmitDisabled={!validateForm()}
    >
      <div>
        {isViewMode && stock && (
          <>
            <FormGroup label="Item">
              <ViewEditField
                isViewMode={true}
                viewContent={stock.item_name}
                editContent={null}
              />
            </FormGroup>
            <FormGroup label="Location">
              <ViewEditField
                isViewMode={true}
                viewContent={`${stock.location_name} (${stock.location_type})`}
                editContent={null}
              />
            </FormGroup>
            <FormGroup label="Quantity">
              <ViewEditField
                isViewMode={true}
                viewContent={stock.quantity}
                editContent={null}
              />
            </FormGroup>
            <FormGroup label="Reserved">
              <ViewEditField
                isViewMode={true}
                viewContent={stock.reserved_quantity}
                editContent={null}
              />
            </FormGroup>
            <FormGroup label="Available">
              <ViewEditField
                isViewMode={true}
                viewContent={stock.available_quantity}
                editContent={null}
              />
            </FormGroup>
            <FormGroup label="Last Updated">
              <ViewEditField
                isViewMode={true}
                viewContent={new Date(stock.last_updated).toLocaleString()}
                editContent={null}
              />
            </FormGroup>
          </>
        )}

        {isAdjustMode && (
          <>
            <FormGroup label="Item" labelInfo="(required)">
              <ViewEditField
                isViewMode={true}
                viewContent={getItemName(itemId)}
                editContent={null}
              />
            </FormGroup>
            <FormGroup label="Location" labelInfo="(required)">
              <ViewEditField
                isViewMode={true}
                viewContent={getLocationName(locationId)}
                editContent={null}
              />
            </FormGroup>
            <FormGroup
              label="Quantity Change"
              labelInfo="(required)"
              helperText="Positive number to add, negative to remove (e.g., 10 or -5)"
            >
              <InputGroup
                type="number"
                value={quantityChange}
                onChange={(e) => setQuantityChange(e.target.value)}
                placeholder="Enter quantity change"
                disabled={isSubmitting}
                fill
              />
            </FormGroup>
            <FormGroup label="Notes" labelInfo="(optional)">
              <TextArea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Optional notes about this adjustment"
                disabled={isSubmitting}
                rows={3}
                fill
              />
            </FormGroup>
          </>
        )}

        {isTransferMode && (
          <>
            <FormGroup label="Item" labelInfo="(required)">
              <ViewEditField
                isViewMode={true}
                viewContent={getItemName(itemId)}
                editContent={null}
              />
            </FormGroup>
            <FormGroup label="From Location" labelInfo="(required)">
              <ViewEditField
                isViewMode={true}
                viewContent={getLocationName(fromLocationId)}
                editContent={null}
              />
            </FormGroup>
            <EasySelect
              label="To Location"
              labelInfo="(required)"
              value={toLocationId}
              options={locationOptions}
              onValueChange={(newValue) => setToLocationId(newValue as string)}
              disabled={isSubmitting}
              placeholder="Search and select destination location..."
              fill
            />
            <FormGroup
              label="Quantity"
              labelInfo="(required)"
              helperText="Amount to transfer"
            >
              <InputGroup
                type="number"
                value={transferQuantity}
                onChange={(e) => setTransferQuantity(e.target.value)}
                placeholder="Enter quantity"
                disabled={isSubmitting}
                min="0"
                step="0.01"
                fill
              />
            </FormGroup>
            <FormGroup label="Notes" labelInfo="(optional)">
              <TextArea
                value={transferNotes}
                onChange={(e) => setTransferNotes(e.target.value)}
                placeholder="Optional notes about this transfer"
                disabled={isSubmitting}
                rows={3}
                fill
              />
            </FormGroup>
          </>
        )}
      </div>
    </EntityModal>
  );
}
