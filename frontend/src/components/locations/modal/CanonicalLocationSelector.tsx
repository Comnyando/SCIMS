/**
 * Canonical Location Selector Component
 *
 * Allows selecting a canonical location to link a regular location to.
 * Only shown for non-canonical locations.
 */

import {
  FormGroup,
  InputGroup,
  HTMLSelect,
  Callout,
  Intent,
} from "@blueprintjs/core";
import { spacing } from "../../../styles/theme";

interface CanonicalLocationEntity {
  id: string;
  canonical_id?: string | null;
  data: {
    name?: string;
    [key: string]: unknown;
  };
}

interface CanonicalLocationSelectorProps {
  label?: string;
  helperText?: string;
  value: string;
  searchValue: string;
  locations: CanonicalLocationEntity[];
  isSubmitting: boolean;
  onValueChange: (value: string) => void;
  onSearchChange: (search: string) => void;
}

export function CanonicalLocationSelector({
  label = "Link to Canonical Location",
  helperText = "Search for a canonical location from public commons to link this location to a standard location",
  value,
  searchValue,
  locations,
  isSubmitting,
  onValueChange,
  onSearchChange,
}: CanonicalLocationSelectorProps) {
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
      const selected = locations.find(
        (loc) => (loc.canonical_id || loc.id) === newValue
      );
      if (selected) {
        const locName =
          (selected.data as { name?: string })?.name || selected.id;
        onSearchChange(locName);
      }
    }
  };

  return (
    <FormGroup label={label} labelInfo="(optional)" helperText={helperText}>
      <InputGroup
        value={searchValue}
        onChange={(e) => onSearchChange(e.target.value)}
        onFocus={handleFocus}
        placeholder="Click to search canonical locations..."
        leftIcon="search"
        disabled={isSubmitting}
        large
        fill
        style={{ marginBottom: spacing.xs }}
      />
      {(searchValue || locations.length > 0) && (
        <HTMLSelect
          value={value}
          onChange={handleSelectChange}
          disabled={isSubmitting}
          large
          fill
        >
          <option value="">
            {locations.length > 0
              ? "Select a canonical location..."
              : "No canonical locations found"}
          </option>
          {locations.map((loc) => {
            const locName = (loc.data as { name?: string })?.name || loc.id;
            return (
              <option key={loc.id} value={loc.canonical_id || loc.id}>
                {locName}
              </option>
            );
          })}
        </HTMLSelect>
      )}
      {value && (
        <Callout intent={Intent.SUCCESS} style={{ marginTop: spacing.xs }}>
          Canonical location selected
        </Callout>
      )}
    </FormGroup>
  );
}
