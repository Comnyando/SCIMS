/**
 * EasySelect Component
 *
 * A reusable, searchable select component that wraps Blueprint.js Suggest/MultiSelect.
 * Handles both single and multi-select scenarios with async data fetching support.
 */

import React, { useMemo, useState, useCallback } from "react";
import { FormGroup, MenuItem } from "@blueprintjs/core";
import { Suggest, ItemRenderer, ItemPredicate } from "@blueprintjs/select";
import type { ItemListRendererProps } from "@blueprintjs/select";
import { spacing } from "../../styles/theme";

export interface EasySelectOption<T = unknown> {
  /** Unique identifier for the option */
  value: string;
  /** Display label for the option */
  label: string;
  /** Optional additional data */
  data?: T;
  /** Optional secondary text or description */
  secondaryText?: string;
}

export interface EasySelectProps<T = unknown> {
  /** Form label */
  label?: string;
  /** Label info (e.g., "(required)") */
  labelInfo?: string;
  /** Helper text */
  helperText?: string;
  /** Current selected value(s) - string for single, string[] for multi */
  value: string | string[];
  /** Available options */
  options: EasySelectOption<T>[];
  /** Callback when selection changes */
  onValueChange: (value: string | string[]) => void;
  /** Whether the field is disabled */
  disabled?: boolean;
  /** Placeholder text */
  placeholder?: string;
  /** Whether to allow multiple selections */
  multiple?: boolean;
  /** Whether to show create option (for creating new items) */
  createNewItemFromQuery?: (query: string) => EasySelectOption<T>;
  /** Custom filter function (defaults to case-insensitive label matching) */
  itemPredicate?: ItemPredicate<EasySelectOption<T>>;
  /** Custom item renderer */
  itemRenderer?: ItemRenderer<EasySelectOption<T>>;
  /** Custom list renderer */
  itemListRenderer?: (
    props: ItemListRendererProps<EasySelectOption<T>>
  ) => React.ReactElement;
  /** Whether to fill available width */
  fill?: boolean;
  /** Minimum characters before showing results */
  minQueryLength?: number;
}

const defaultItemPredicate: ItemPredicate<EasySelectOption> = (
  query: string,
  item: EasySelectOption
) => {
  const normalizedQuery = query.toLowerCase();
  const normalizedLabel = item.label.toLowerCase();
  const normalizedSecondary = item.secondaryText?.toLowerCase() || "";
  return (
    normalizedLabel.includes(normalizedQuery) ||
    normalizedSecondary.includes(normalizedQuery)
  );
};

const defaultItemRenderer: ItemRenderer<EasySelectOption> = (
  item: EasySelectOption,
  itemProps
) => {
  if (!itemProps.modifiers.matchesPredicate) {
    return null;
  }

  return (
    <MenuItem
      key={item.value}
      text={item.label}
      label={item.secondaryText}
      onClick={itemProps.handleClick}
      active={itemProps.modifiers.active}
      disabled={itemProps.modifiers.disabled}
    />
  );
};

const defaultItemListRenderer = <T,>(
  props: ItemListRendererProps<EasySelectOption<T>>
) => {
  const { items, itemsParentRef, renderItem } = props;
  const renderedItems = items
    .map(renderItem)
    .filter((item: React.ReactNode) => item != null);

  return (
    <ul
      ref={itemsParentRef as React.Ref<HTMLUListElement>}
      style={{
        maxHeight: "300px",
        overflowY: "auto",
        listStyle: "none",
        margin: 0,
        padding: 0,
      }}
    >
      {renderedItems.length > 0 ? (
        renderedItems
      ) : (
        <MenuItem disabled text="No results found" />
      )}
    </ul>
  );
};

/**
 * EasySelect - A searchable, reusable select component
 */
export function EasySelect<T = unknown>({
  label,
  labelInfo,
  helperText,
  value,
  options,
  onValueChange,
  disabled = false,
  placeholder = "Search and select...",
  multiple = false,
  createNewItemFromQuery,
  itemPredicate = defaultItemPredicate,
  itemRenderer = defaultItemRenderer,
  itemListRenderer = defaultItemListRenderer,
  fill = true,
  minQueryLength = 0,
}: EasySelectProps<T>) {
  const [query, setQuery] = useState("");

  // Find selected option(s) for display
  const selectedOption = useMemo(() => {
    if (multiple) {
      const values = value as string[];
      return options.filter((opt) => values.includes(opt.value));
    } else {
      return options.find((opt) => opt.value === (value as string));
    }
  }, [value, options, multiple]);

  // Get display text for selected value(s) - used for inputValueRenderer
  const getInputValue = useCallback((item: EasySelectOption<T> | null) => {
    if (!item) return "";
    return item.label;
  }, []);

  // Filter options based on query
  const filteredOptions = useMemo(() => {
    const trimmedQuery = query?.trim() || "";
    if (!trimmedQuery || trimmedQuery.length < minQueryLength) {
      return options;
    }
    return options.filter((item) => itemPredicate(trimmedQuery, item));
  }, [query, options, itemPredicate, minQueryLength]);

  // Handle selection
  const handleItemSelect = useCallback(
    (item: EasySelectOption<T>) => {
      if (multiple) {
        const currentValues = (value as string[]) || [];
        const newValues = currentValues.includes(item.value)
          ? currentValues.filter((v) => v !== item.value)
          : [...currentValues, item.value];
        onValueChange(newValues);
      } else {
        onValueChange(item.value);
        setQuery(""); // Clear query after selection
      }
    },
    [value, multiple, onValueChange]
  );

  // Handle input change
  const handleQueryChange = useCallback((newQuery: string) => {
    setQuery(newQuery);
  }, []);

  const suggestComponent = (
    <Suggest<EasySelectOption<T>>
      items={filteredOptions}
      selectedItem={
        multiple
          ? undefined
          : (selectedOption as EasySelectOption<T> | undefined)
      }
      onItemSelect={handleItemSelect}
      onQueryChange={handleQueryChange}
      query={query}
      inputValueRenderer={getInputValue}
      itemPredicate={itemPredicate}
      itemRenderer={itemRenderer}
      itemListRenderer={itemListRenderer}
      inputProps={{
        placeholder,
        onFocus: () => {
          // Don't clear query on focus - let user see their search
          // Only clear if there's no query and we want to show all options
          if (!query || query.trim().length === 0) {
            setQuery("");
          }
        },
      }}
      popoverProps={{
        minimal: true,
        placement: "bottom-start",
        onOpening: () => {
          // When opening, show all options if no query
          // This allows users to see all available options when they first open
          if (!query || query.trim().length === 0) {
            setQuery("");
          }
        },
      }}
      disabled={disabled}
      fill={fill}
      createNewItemFromQuery={createNewItemFromQuery}
      createNewItemRenderer={
        createNewItemFromQuery
          ? (
              query: string,
              active: boolean,
              handleClick: React.MouseEventHandler<HTMLElement>
            ) => (
              <MenuItem
                icon="add"
                text={`Create "${query}"`}
                active={active}
                onClick={handleClick}
              />
            )
          : undefined
      }
      noResults={<MenuItem disabled text="No results found" />}
    />
  );

  if (label || labelInfo || helperText) {
    return (
      <FormGroup
        label={label}
        labelInfo={labelInfo}
        helperText={helperText}
        style={{ marginBottom: spacing.md }}
      >
        {suggestComponent}
      </FormGroup>
    );
  }

  return suggestComponent;
}
