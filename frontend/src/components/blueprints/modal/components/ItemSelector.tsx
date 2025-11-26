/**
 * Item Selector Component for Blueprint Modal
 *
 * Allows searching and selecting an item from the item catalog.
 * Uses EasySelect for a better UX.
 */

import { useMemo, useCallback } from "react";
import { EasySelect, type EasySelectOption } from "../../../common/EasySelect";
import type { Item } from "../../../../types/item";

interface ItemSelectorProps {
  label?: string;
  labelInfo?: string;
  helperText?: string;
  value: string;
  searchValue: string; // Kept for backward compatibility but not used directly
  items: Item[];
  isSubmitting: boolean;
  onValueChange: (value: string) => void;
  onSearchChange: (search: string) => void; // Kept for backward compatibility
  onCreateNewItem?: (name: string) => Promise<string>; // Returns the new item ID
}

export function ItemSelector({
  label = "Item",
  labelInfo,
  helperText,
  value,
  items,
  isSubmitting,
  onValueChange,
  onCreateNewItem,
}: ItemSelectorProps) {
  // Convert items to EasySelect options
  const options: EasySelectOption<Item>[] = useMemo(
    () =>
      items.map((item) => ({
        value: item.id,
        label: item.name,
        secondaryText: item.category || undefined,
        data: item,
      })),
    [items]
  );

  // Handle creating a new item from query
  // Note: EasySelect's createNewItemFromQuery is synchronous, so we create a placeholder
  // and handle the actual creation via onValueChange
  const handleCreateNewItem = useCallback(
    (query: string): EasySelectOption<Item> => {
      // Return a placeholder option - the actual creation will happen when selected
      // We'll use a special prefix to identify placeholder items
      const placeholderId = `__new__${query}`;
      return {
        value: placeholderId,
        label: query,
        data: { id: placeholderId, name: query } as Item,
      };
    },
    []
  );

  // Handle when a placeholder item is selected
  const handleValueChange = useCallback(
    async (newValue: string | string[]) => {
      const valueToUse = typeof newValue === "string" ? newValue : newValue[0];

      // Check if this is a placeholder item that needs to be created
      if (valueToUse && valueToUse.startsWith("__new__") && onCreateNewItem) {
        const itemName = valueToUse.replace("__new__", "");
        try {
          // Create the actual item and wait for it to complete
          const newItemId = await onCreateNewItem(itemName);
          // Only update with the real item ID if creation succeeded
          if (newItemId && !newItemId.startsWith("__new__")) {
            onValueChange(newItemId);
          } else {
            console.error("Invalid item ID returned from creation:", newItemId);
          }
        } catch (error) {
          console.error("Failed to create item:", error);
          // Don't update if creation failed - this prevents placeholder IDs from being stored
        }
      } else if (valueToUse && !valueToUse.startsWith("__new__")) {
        // Normal selection - only allow non-placeholder IDs
        onValueChange(valueToUse);
      }
    },
    [onCreateNewItem, onValueChange]
  );

  const defaultHelperText = onCreateNewItem
    ? "Search for an item or type a new name to create one"
    : "Search for an item from your catalog";

  return (
    <EasySelect
      label={label}
      labelInfo={labelInfo}
      helperText={helperText || defaultHelperText}
      value={value}
      options={options}
      onValueChange={handleValueChange}
      disabled={isSubmitting}
      placeholder={
        options.length === 0
          ? "Loading items..."
          : onCreateNewItem
          ? "Search items or type to create new..."
          : "Search and select an item..."
      }
      fill
      createNewItemFromQuery={onCreateNewItem ? handleCreateNewItem : undefined}
    />
  );
}
