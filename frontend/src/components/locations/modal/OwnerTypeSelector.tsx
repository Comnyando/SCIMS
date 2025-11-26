/**
 * Owner Type Selector Component for Location Modal
 *
 * Handles selection of owner type with conditional callouts based on selection.
 * Uses EasySelect for consistency.
 */

import { useMemo } from "react";
import { Callout, Intent } from "@blueprintjs/core";
import { EasySelect, type EasySelectOption } from "../../common/EasySelect";
import { OwnerType } from "../../../types/enums";
import { OWNER_TYPES } from "./constants";
import { spacing } from "../../../styles/theme";

interface OwnerTypeSelectorProps {
  /** Current owner type value */
  value: OwnerType;
  /** Callback when owner type changes */
  onChange: (value: OwnerType) => void;
  /** Whether the field is disabled */
  disabled?: boolean;
  /** Organization ID (if available) */
  organizationId?: string | null;
}

export function OwnerTypeSelector({
  value,
  onChange,
  disabled = false,
  organizationId,
}: OwnerTypeSelectorProps) {
  // Convert owner types to EasySelect format
  const ownerTypeOptions: EasySelectOption[] = useMemo(
    () =>
      OWNER_TYPES.map((opt) => ({
        value: opt.value,
        label: opt.label,
      })),
    []
  );

  return (
    <>
      <EasySelect
        label="Owner Type"
        value={value}
        options={ownerTypeOptions}
        onValueChange={(newValue) => onChange(newValue as OwnerType)}
        disabled={disabled}
        placeholder="Select owner type..."
        fill
      />
      {value === OwnerType.ORGANIZATION && !organizationId && (
        <Callout intent={Intent.WARNING} style={{ marginTop: spacing.xs }}>
          No organization selected. This location will be user-owned.
        </Callout>
      )}
      {value === OwnerType.WORLD && (
        <Callout intent={Intent.PRIMARY} style={{ marginTop: spacing.xs }}>
          World-owned locations represent universe structures (moons, planets,
          star systems) and are publicly accessible.
        </Callout>
      )}
    </>
  );
}
