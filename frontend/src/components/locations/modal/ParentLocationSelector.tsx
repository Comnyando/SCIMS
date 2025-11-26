/**
 * Parent Location Selector Component
 *
 * Allows selecting a parent location for a location.
 * For canonical locations, only shows canonical parent locations.
 * For regular locations, shows user's accessible locations.
 * Uses EasySelect for a better UX.
 */

import { useMemo } from "react";
import { EasySelect, type EasySelectOption } from "../../common/EasySelect";

interface ParentLocation {
  id: string;
  name: string;
  type: string;
}

interface ParentLocationSelectorProps {
  label?: string;
  helperText?: string;
  value: string;
  searchValue: string; // Kept for backward compatibility but not used directly
  locations: ParentLocation[];
  isSubmitting: boolean;
  isCanonical?: boolean;
  onValueChange: (value: string) => void;
  onSearchChange: (search: string) => void; // Kept for backward compatibility
}

export function ParentLocationSelector({
  label = "Parent Location",
  helperText,
  value,
  locations,
  isSubmitting,
  isCanonical = false,
  onValueChange,
}: ParentLocationSelectorProps) {
  // Convert locations to EasySelect options
  const options: EasySelectOption<ParentLocation>[] = useMemo(
    () =>
      locations.map((loc) => ({
        value: loc.id,
        label: loc.name,
        secondaryText: loc.type,
        data: loc,
      })),
    [locations]
  );

  const defaultHelperText = isCanonical
    ? "Search for a canonical parent location (canonical locations can only have canonical parents)"
    : "Search for a parent location from your accessible locations";

  const placeholder = isCanonical
    ? "Search canonical parent locations..."
    : "Search parent locations...";

  return (
    <EasySelect
      label={label}
      labelInfo="(optional)"
      helperText={helperText || defaultHelperText}
      value={value}
      options={options}
      onValueChange={(newValue) => onValueChange(newValue as string)}
      disabled={isSubmitting}
      placeholder={placeholder}
      fill
    />
  );
}
