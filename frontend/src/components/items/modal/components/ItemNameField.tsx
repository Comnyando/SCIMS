/**
 * Item Name Field Component
 */

import { FormGroup, InputGroup } from "@blueprintjs/core";
import { ViewEditField } from "../../../common/ViewEditField";

interface ItemNameFieldProps {
  /** Whether in view mode */
  isViewMode: boolean;
  /** Current name value */
  value: string;
  /** Callback when name changes */
  onChange: (value: string) => void;
  /** Whether the field is disabled */
  disabled?: boolean;
}

export function ItemNameField({
  isViewMode,
  value,
  onChange,
  disabled = false,
}: ItemNameFieldProps) {
  return (
    <FormGroup label="Name" labelInfo="(required)">
      <ViewEditField
        isViewMode={isViewMode}
        viewContent={value}
        editContent={
          <InputGroup
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Enter item name"
            disabled={disabled}
            fill
          />
        }
      />
    </FormGroup>
  );
}

