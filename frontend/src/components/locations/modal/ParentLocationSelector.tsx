/**
 * Parent Location Selector Component
 *
 * Allows selecting a parent location for a location.
 * For canonical locations, only shows canonical parent locations.
 * For regular locations, shows user's accessible locations.
 */

import {
  FormGroup,
  InputGroup,
  HTMLSelect,
  Callout,
  Intent,
} from "@blueprintjs/core";
import { spacing } from "../../../styles/theme";

interface ParentLocation {
  id: string;
  name: string;
  type: string;
}

interface ParentLocationSelectorProps {
  label?: string;
  helperText?: string;
  value: string;
  searchValue: string;
  locations: ParentLocation[];
  isSubmitting: boolean;
  isCanonical?: boolean;
  onValueChange: (value: string) => void;
  onSearchChange: (search: string) => void;
}

export function ParentLocationSelector({
  label = "Parent Location",
  helperText,
  value,
  searchValue,
  locations,
  isSubmitting,
  isCanonical = false,
  onValueChange,
  onSearchChange,
}: ParentLocationSelectorProps) {
  const handleFocus = () => {
    // Show results when focused, even if search is empty
    if (!searchValue && locations.length === 0) {
      onSearchChange(" ");
    }
  };

  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newValue = e.target.value;
    onValueChange(newValue);
    if (newValue) {
      // Update search to show selected value name
      const selected = locations.find((loc) => loc.id === newValue);
      if (selected) {
        onSearchChange(selected.name);
      }
    }
  };

  const defaultHelperText = isCanonical
    ? "Search for a canonical parent location (canonical locations can only have canonical parents)"
    : "Search for a parent location from your accessible locations";

  const placeholder = isCanonical
    ? "Click to search canonical parent locations..."
    : "Click to search parent locations...";

  const emptyMessage = isCanonical
    ? "No canonical locations found"
    : "No locations found";

  const selectPlaceholder = isCanonical
    ? "Select a canonical parent location..."
    : "Select a parent location...";

  return (
    <FormGroup
      label={label}
      labelInfo="(optional)"
      helperText={helperText || defaultHelperText}
    >
      <InputGroup
        value={searchValue}
        onChange={(e) => onSearchChange(e.target.value)}
        onFocus={handleFocus}
        placeholder={placeholder}
        leftIcon="search"
        disabled={isSubmitting}
        large
        fill
        style={{ marginBottom: spacing.xs }}
      />
      {(searchValue || locations.length > 0 || value) && (
        <HTMLSelect
          value={value}
          onChange={handleSelectChange}
          disabled={isSubmitting}
          large
          fill
        >
          <option value="">
            {locations.length > 0 ? selectPlaceholder : emptyMessage}
          </option>
          {locations.map((loc) => (
            <option key={loc.id} value={loc.id}>
              {loc.name} ({loc.type})
            </option>
          ))}
        </HTMLSelect>
      )}
      {value && (
        <Callout intent={Intent.SUCCESS} style={{ marginTop: spacing.xs }}>
          {(() => {
            const selected = locations.find((loc) => loc.id === value);
            return selected
              ? `Parent location selected: ${selected.name}`
              : "Parent location selected";
          })()}
        </Callout>
      )}
    </FormGroup>
  );
}
