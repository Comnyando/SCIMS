/**
 * Item Creation/Edit/View Modal Component
 *
 * A self-contained modal for creating, editing, and viewing items.
 * Uses Zustand store for state management and handles all submission logic internally.
 */

import { EntityModal } from "../../common/EntityModal";
import { MetadataField } from "../../common/MetadataField";
import { useCreateItem, useUpdateItem } from "../../../hooks/mutations/items";
import { useItemModalStore } from "../../../stores/itemModalStore";
import {
  ItemNameField,
  ItemDescriptionField,
  ItemTextField,
} from "./components";

/**
 * Self-contained ItemModal component.
 * Gets all state from Zustand store and handles submission internally.
 */
export function ItemModal() {
  // Get all state and actions from store
  const {
    isOpen,
    mode,
    item,
    isSubmitting,
    error,
    name,
    description,
    category,
    subcategory,
    rarity,
    metadataJson,
    closeModal,
    switchToEditMode,
    setName,
    setDescription,
    setCategory,
    setSubcategory,
    setRarity,
    setMetadataJson,
    handleSubmit: storeHandleSubmit,
  } = useItemModalStore();

  const isViewMode = mode === "view";
  const isEditMode = mode === "edit";

  // Mutations for submission
  const createMutation = useCreateItem();
  const updateMutation = useUpdateItem();

  // Handle form submission
  const handleSubmit = async () => {
    await storeHandleSubmit(createMutation, updateMutation);
  };

  const validateForm = (): boolean => {
    if (!name.trim()) return false;
    if (metadataJson.trim()) {
      try {
        JSON.parse(metadataJson);
      } catch {
        return false;
      }
    }
    return true;
  };

  const modalTitle = isViewMode
    ? `View Item: ${item?.name || ""}`
    : isEditMode
    ? "Edit Item"
    : "Create New Item";

  // For items, all authenticated users can edit
  const canEdit = true;

  return (
    <EntityModal
      isOpen={isOpen}
      onClose={closeModal}
      title={modalTitle}
      mode={mode}
      onSwitchToEdit={switchToEditMode}
      canEdit={canEdit}
      submitText={isEditMode ? "Update" : "Create"}
      onSubmit={isViewMode ? undefined : handleSubmit}
      isSubmitting={isSubmitting}
      error={error}
      isSubmitDisabled={!validateForm()}
    >
      <div>
        <ItemNameField
          isViewMode={isViewMode}
          value={name}
          onChange={setName}
          disabled={isSubmitting}
        />

        <ItemDescriptionField
          isViewMode={isViewMode}
          value={description}
          onChange={setDescription}
          disabled={isSubmitting}
        />

        <ItemTextField
          label="Category"
          isViewMode={isViewMode}
          value={category}
          onChange={setCategory}
          placeholder="Enter category"
          disabled={isSubmitting}
        />

        <ItemTextField
          label="Subcategory"
          isViewMode={isViewMode}
          value={subcategory}
          onChange={setSubcategory}
          placeholder="Enter subcategory"
          disabled={isSubmitting}
        />

        <ItemTextField
          label="Rarity"
          isViewMode={isViewMode}
          value={rarity}
          onChange={setRarity}
          placeholder="Enter rarity"
          disabled={isSubmitting}
        />

        <MetadataField
          isViewMode={isViewMode}
          value={metadataJson}
          onChange={setMetadataJson}
          disabled={isSubmitting}
        />
      </div>
    </EntityModal>
  );
}
