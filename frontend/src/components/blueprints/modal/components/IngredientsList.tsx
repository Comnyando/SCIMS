/**
 * Ingredients List Component for Blueprint Modal
 *
 * Handles viewing and editing blueprint ingredients.
 */

import { useMemo, useCallback } from "react";
import { Button, FormGroup, NumericInput, Switch } from "@blueprintjs/core";
import { EasySelect, type EasySelectOption } from "../../../common/EasySelect";
import { spacing, colors } from "../../../../styles/theme";
import type { BlueprintIngredient } from "../../../../types/blueprint";
import type { Item } from "../../../../types/item";

interface IngredientsListProps {
  /** Whether in view mode */
  isViewMode: boolean;
  /** Current ingredients */
  ingredients: BlueprintIngredient[];
  /** Available items for selection */
  items: Item[];
  /** Callback to add a new ingredient */
  onAddIngredient: () => void;
  /** Callback to remove an ingredient */
  onRemoveIngredient: (index: number) => void;
  /** Callback to update an ingredient */
  onUpdateIngredient: (
    index: number,
    field: keyof BlueprintIngredient,
    value: string | number | boolean
  ) => void;
  /** Whether the field is disabled */
  disabled?: boolean;
  /** Callback to create a new item (returns item ID) */
  onCreateNewItem?: (name: string) => Promise<string>;
}

export function IngredientsList({
  isViewMode,
  ingredients,
  items,
  onAddIngredient,
  onRemoveIngredient,
  onUpdateIngredient,
  disabled = false,
  onCreateNewItem,
}: IngredientsListProps) {
  // Convert items to EasySelect options
  const itemOptions: EasySelectOption<Item>[] = useMemo(
    () =>
      items.map((item) => ({
        value: item.id,
        label: item.name,
        secondaryText: item.category || undefined,
        data: item,
      })),
    [items]
  );

  const getItemName = (itemId: string): string => {
    const item = items.find((i) => i.id === itemId);
    return item?.name || itemId || "—";
  };

  // Handle creating a new item from query
  // Note: EasySelect's createNewItemFromQuery is synchronous, so we create a placeholder
  const handleCreateNewItem = useCallback(
    (query: string): EasySelectOption<Item> => {
      // Return a placeholder option - the actual creation will happen when selected
      const placeholderId = `__new__${query}`;
      return {
        value: placeholderId,
        label: query,
        data: { id: placeholderId, name: query } as Item,
      };
    },
    []
  );

  // Handle when a placeholder item is selected in an ingredient
  const handleIngredientItemChange = useCallback(
    async (index: number, newValue: string | string[]) => {
      const valueToUse = typeof newValue === "string" ? newValue : newValue[0];

      // Check if this is a placeholder item that needs to be created
      if (valueToUse && valueToUse.startsWith("__new__") && onCreateNewItem) {
        const itemName = valueToUse.replace("__new__", "");
        try {
          // Create the actual item and wait for it to complete
          const newItemId = await onCreateNewItem(itemName);
          // Only update with the real item ID if creation succeeded
          if (newItemId && !newItemId.startsWith("__new__")) {
            onUpdateIngredient(index, "item_id", newItemId);
          } else {
            console.error("Invalid item ID returned from creation:", newItemId);
          }
        } catch (error) {
          console.error("Failed to create item:", error);
          // Don't update if creation failed - this prevents placeholder IDs from being stored
        }
      } else if (valueToUse && !valueToUse.startsWith("__new__")) {
        // Normal selection - only allow non-placeholder IDs
        onUpdateIngredient(index, "item_id", valueToUse);
      }
    },
    [onCreateNewItem, onUpdateIngredient]
  );

  // Get placeholder text based on items availability
  const getItemPlaceholder = useCallback(() => {
    if (items.length === 0) {
      return "Loading items...";
    }
    if (onCreateNewItem) {
      return "Search items or type to create new...";
    }
    return "Search and select an item...";
  }, [items.length, onCreateNewItem]);

  return (
    <FormGroup
      label="Ingredients"
      helperText={
        isViewMode ? undefined : "Add items required to craft this blueprint"
      }
    >
      {isViewMode ? (
        <div>
          {ingredients.length === 0 ? (
            <span style={{ color: colors.text.muted }}>No ingredients</span>
          ) : (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: spacing.xs,
              }}
            >
              {ingredients.map((ing, index) => (
                <div
                  key={index}
                  style={{
                    padding: spacing.sm,
                    backgroundColor: "var(--scims-background-tertiary)",
                    borderRadius: 4,
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <div>
                    <strong>{getItemName(ing.item_id)}</strong>
                    <span
                      style={{
                        marginLeft: spacing.sm,
                        color: colors.text.muted,
                      }}
                    >
                      × {ing.quantity}
                      {ing.optional && " (optional)"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div>
          {ingredients.length === 0 ? (
            <div style={{ color: colors.text.muted, marginBottom: spacing.sm }}>
              No ingredients added yet
            </div>
          ) : (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: spacing.sm,
              }}
            >
              {ingredients.map((ing, index) => (
                <div
                  key={index}
                  style={{
                    display: "grid",
                    gridTemplateColumns: "2fr 1fr auto auto",
                    gap: spacing.sm,
                    alignItems: "center",
                    padding: spacing.sm,
                    backgroundColor: "var(--scims-background-tertiary)",
                    borderRadius: 4,
                  }}
                >
                  <EasySelect
                    value={ing.item_id}
                    options={itemOptions}
                    onValueChange={(newValue) =>
                      handleIngredientItemChange(index, newValue)
                    }
                    disabled={disabled}
                    placeholder={getItemPlaceholder()}
                    fill
                    createNewItemFromQuery={
                      onCreateNewItem ? handleCreateNewItem : undefined
                    }
                  />
                  <NumericInput
                    value={ing.quantity}
                    onValueChange={(value) =>
                      onUpdateIngredient(index, "quantity", value || 1)
                    }
                    min={1}
                    disabled={disabled}
                    fill
                  />
                  <Switch
                    checked={ing.optional || false}
                    onChange={(e) =>
                      onUpdateIngredient(
                        index,
                        "optional",
                        e.currentTarget.checked
                      )
                    }
                    label="Optional"
                    disabled={disabled}
                  />
                  <Button
                    icon="trash"
                    minimal
                    intent="danger"
                    onClick={() => onRemoveIngredient(index)}
                    disabled={disabled}
                    title="Remove ingredient"
                  />
                </div>
              ))}
            </div>
          )}
          <Button
            icon="add"
            text="Add Ingredient"
            onClick={onAddIngredient}
            disabled={disabled}
            style={{ marginTop: spacing.sm }}
          />
        </div>
      )}
    </FormGroup>
  );
}
