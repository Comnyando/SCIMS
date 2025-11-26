/**
 * Blueprint Creation/Edit/View Modal Component
 *
 * A self-contained modal for creating, editing, and viewing blueprints.
 * Uses Zustand store for state management and handles all submission logic internally.
 */

import React, { useMemo } from "react";
import {
  FormGroup,
  InputGroup,
  TextArea,
  NumericInput,
  Switch,
} from "@blueprintjs/core";
import { EntityModal } from "../../common/EntityModal";
import { ViewEditField } from "../../common/ViewEditField";
import { EasySelect, type EasySelectOption } from "../../common/EasySelect";
import {
  useCreateBlueprint,
  useUpdateBlueprint,
} from "../../../hooks/mutations/blueprints";
import { useCreateItem } from "../../../hooks/mutations/items";
import { useBlueprintModalStore } from "../../../stores/blueprintModalStore";
import { useItems } from "../../../hooks/queries/items";
import { useAlert } from "../../../hooks/useAlert";
import { spacing, colors } from "../../../styles/theme";
import { IngredientsList, ItemSelector, CraftingTimeInput } from "./components";

const CATEGORY_OPTIONS = [
  { value: "", label: "Select category..." },
  { value: "Weapons", label: "Weapons" },
  { value: "Components", label: "Components" },
  { value: "Food", label: "Food" },
  { value: "Materials", label: "Materials" },
  { value: "Other", label: "Other" },
];

/**
 * Self-contained BlueprintModal component.
 * Gets all state from Zustand store and handles submission internally.
 */
export function BlueprintModal() {
  // Get all state and actions from store
  const {
    isOpen,
    mode,
    blueprint,
    isSubmitting,
    error,
    name,
    description,
    category,
    craftingTimeMinutes,
    craftingTimeHours,
    craftingTimeMinutesInput,
    craftingTimeSeconds,
    outputItemId,
    outputItemSearch,
    outputQuantity,
    ingredients,
    isPublic,
    closeModal,
    switchToEditMode,
    setName,
    setDescription,
    setCategory,
    setCraftingTimeHours,
    setCraftingTimeMinutesInput,
    setCraftingTimeSeconds,
    setOutputItemId,
    setOutputItemSearch,
    setOutputQuantity,
    setIsPublic,
    addIngredient,
    removeIngredient,
    updateIngredient,
    handleSubmit: storeHandleSubmit,
  } = useBlueprintModalStore();

  const isViewMode = mode === "view";
  const isEditMode = mode === "edit";

  // Mutation for creating items inline
  const createItemMutation = useCreateItem();

  // Fetch items for dropdowns - always fetch when modal is open (in create/edit mode)
  // Use a larger limit to get more items for selection
  // IMPORTANT: Never use search filter - we want all items available for selection
  // The EasySelect component handles filtering on the client side
  // Fetch items - backend has a max limit of 100, so we fetch the first 100
  // For dropdowns, this should be sufficient for most use cases
  // If users have more than 100 items, they can use the search functionality
  const { data: itemsData, refetch: refetchItems } = useItems({
    skip: 0,
    limit: 100, // Backend maximum limit is 100
    search: undefined, // Never use search - we want all items for the dropdown
    enabled: isOpen && !isViewMode, // Always fetch when modal is open in create/edit mode
  });
  const items = useMemo(() => itemsData?.items || [], [itemsData?.items]);

  // Alert hook for user feedback
  const { showSuccess, showError, showInfo } = useAlert();

  // Handler for creating new items from the selector
  const handleCreateItem = async (name: string): Promise<string> => {
    const trimmedName = name.trim();
    if (!trimmedName) {
      throw new Error("Item name cannot be empty");
    }

    try {
      // Show info alert that item creation is in progress
      showInfo("Creating Item", `Creating new item "${trimmedName}"...`);

      const newItem = await createItemMutation.mutateAsync({
        name: trimmedName,
        description: `Placeholder item created from blueprint modal`,
      });

      // Refetch items after creation to include the new item
      await refetchItems();

      // Show success alert
      showSuccess(
        "Item Created",
        `Item "${trimmedName}" has been created and selected.`
      );

      return newItem.id;
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to create item";
      showError("Item Creation Failed", errorMessage);
      throw error;
    }
  };

  // Refetch items when a new item is created to ensure it appears in the list
  React.useEffect(() => {
    if (createItemMutation.isSuccess) {
      refetchItems();
    }
  }, [createItemMutation.isSuccess, refetchItems]);

  // Convert category options to EasySelect format
  const categoryOptions: EasySelectOption[] = useMemo(
    () =>
      CATEGORY_OPTIONS.filter((opt) => opt.value !== "").map((opt) => ({
        value: opt.value,
        label: opt.label,
      })),
    []
  );

  // Update search value when we have an item selected but no search value
  React.useEffect(() => {
    if (outputItemId && !outputItemSearch && items.length > 0) {
      const selectedItem = items.find((item) => item.id === outputItemId);
      if (selectedItem) {
        setOutputItemSearch(selectedItem.name);
      }
    }
  }, [outputItemId, outputItemSearch, items, setOutputItemSearch]);

  // Mutations for submission
  const createMutation = useCreateBlueprint();
  const updateMutation = useUpdateBlueprint();

  // Handle form submission
  const handleSubmit = async () => {
    await storeHandleSubmit(createMutation, updateMutation);
  };

  const validateForm = (): boolean => {
    if (!name.trim()) return false;
    if (!outputItemId) return false;
    if (outputQuantity < 1) return false;
    if (craftingTimeMinutes < 0) return false;
    // Check that all ingredients have item_id
    const hasInvalidIngredient = ingredients.some((ing) => !ing.item_id);
    if (hasInvalidIngredient) return false;
    return true;
  };

  const modalTitle = isViewMode
    ? `View Blueprint: ${blueprint?.name || ""}`
    : isEditMode
    ? "Edit Blueprint"
    : "Create New Blueprint";

  // For blueprints, all authenticated users can edit their own, or if public
  const canEdit = true; // TODO: Check ownership/permissions

  const getItemName = (itemId: string): string => {
    const item = items.find((i) => i.id === itemId);
    return item?.name || itemId || "—";
  };

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
        <FormGroup label="Name" labelInfo="(required)">
          <ViewEditField
            isViewMode={isViewMode}
            viewContent={name}
            editContent={
              <InputGroup
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter blueprint name"
                disabled={isSubmitting}
                fill
              />
            }
          />
        </FormGroup>

        <FormGroup label="Description" labelInfo="(optional)">
          <ViewEditField
            isViewMode={isViewMode}
            viewContent={
              description || <span style={{ color: colors.text.muted }}>—</span>
            }
            editContent={
              <TextArea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Enter blueprint description"
                disabled={isSubmitting}
                rows={3}
                fill
              />
            }
          />
        </FormGroup>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: spacing.md,
          }}
        >
          {isViewMode ? (
            <FormGroup label="Category" labelInfo="(optional)">
              <ViewEditField
                isViewMode={true}
                viewContent={
                  category || (
                    <span style={{ color: colors.text.muted }}>—</span>
                  )
                }
                editContent={null}
              />
            </FormGroup>
          ) : (
            <EasySelect
              label="Category"
              labelInfo="(optional)"
              value={category}
              options={categoryOptions}
              onValueChange={(newValue) => setCategory(newValue as string)}
              disabled={isSubmitting}
              placeholder="Select category..."
              fill
            />
          )}

          <CraftingTimeInput
            isViewMode={isViewMode}
            totalMinutes={craftingTimeMinutes}
            hours={craftingTimeHours}
            minutes={craftingTimeMinutesInput}
            seconds={craftingTimeSeconds}
            isSubmitting={isSubmitting}
            onHoursChange={setCraftingTimeHours}
            onMinutesChange={setCraftingTimeMinutesInput}
            onSecondsChange={setCraftingTimeSeconds}
          />
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "2fr 1fr",
            gap: spacing.md,
          }}
        >
          {isViewMode ? (
            <FormGroup label="Output Item" labelInfo="(required)">
              <ViewEditField
                isViewMode={true}
                viewContent={getItemName(outputItemId)}
                editContent={null}
              />
            </FormGroup>
          ) : (
            <ItemSelector
              label="Output Item"
              labelInfo="(required)"
              value={outputItemId}
              searchValue={outputItemSearch}
              items={items}
              isSubmitting={isSubmitting || createItemMutation.isPending}
              onValueChange={setOutputItemId}
              onSearchChange={setOutputItemSearch}
              onCreateNewItem={handleCreateItem}
            />
          )}

          <FormGroup label="Output Quantity" labelInfo="(required)">
            <ViewEditField
              isViewMode={isViewMode}
              viewContent={outputQuantity.toString()}
              editContent={
                <NumericInput
                  value={outputQuantity}
                  onValueChange={(value) => setOutputQuantity(value || 1)}
                  min={1}
                  disabled={isSubmitting}
                  fill
                />
              }
            />
          </FormGroup>
        </div>

        <IngredientsList
          isViewMode={isViewMode}
          ingredients={ingredients}
          items={items}
          onAddIngredient={addIngredient}
          onRemoveIngredient={removeIngredient}
          onUpdateIngredient={updateIngredient}
          disabled={isSubmitting || createItemMutation.isPending}
          onCreateNewItem={handleCreateItem}
        />

        {!isViewMode && (
          <FormGroup
            label="Public Blueprint"
            helperText="Make this blueprint visible to all users"
          >
            <Switch
              checked={isPublic}
              onChange={(e) => setIsPublic(e.currentTarget.checked)}
              disabled={isSubmitting}
              label="Share with community"
            />
          </FormGroup>
        )}
        {isViewMode && (
          <FormGroup label="Public">
            <ViewEditField
              isViewMode={true}
              viewContent={isPublic ? "Yes" : "No"}
              editContent={null}
            />
          </FormGroup>
        )}
      </div>
    </EntityModal>
  );
}
