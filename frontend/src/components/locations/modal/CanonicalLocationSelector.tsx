/**
 * Canonical Location Selector Component
 *
 * Allows selecting a canonical location to link a regular location to.
 * Only shown for non-canonical locations.
 * Uses EasySelect for a better UX.
 */

import { useMemo } from "react";
import { EasySelect, type EasySelectOption } from "../../common/EasySelect";

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
  searchValue: string; // Kept for backward compatibility but not used directly
  locations: CanonicalLocationEntity[];
  isSubmitting: boolean;
  onValueChange: (value: string) => void;
  onSearchChange: (search: string) => void; // Kept for backward compatibility
}

export function CanonicalLocationSelector({
  label = "Link to Canonical Location",
  helperText = "Search for a canonical location from public commons to link this location to a standard location",
  value,
  locations,
  isSubmitting,
  onValueChange,
}: CanonicalLocationSelectorProps) {
  // Convert locations to EasySelect options
  const options: EasySelectOption<CanonicalLocationEntity>[] = useMemo(
    () =>
      locations.map((loc) => {
        const locName = (loc.data as { name?: string })?.name || loc.id;
        return {
          value: loc.canonical_id || loc.id,
          label: locName,
          data: loc,
        };
      }),
    [locations]
  );

  return (
    <EasySelect
      label={label}
      labelInfo="(optional)"
      helperText={helperText}
      value={value}
      options={options}
      onValueChange={(newValue: string | string[]) =>
        onValueChange(newValue as string)
      }
      disabled={isSubmitting}
      placeholder="Search canonical locations..."
      fill
    />
  );
}
