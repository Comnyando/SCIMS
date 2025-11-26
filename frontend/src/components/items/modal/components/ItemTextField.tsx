/**
 * Reusable Text Field Component for Item Modal
 *
 * Used for category, subcategory, rarity, and other simple text fields.
 */

import { FormGroup, InputGroup } from "@blueprintjs/core";
import { ViewEditField } from "../../../common/ViewEditField";
import { colors } from "../../../../styles/theme";

interface ItemTextFieldProps {
  /** Field label */
  label: string;
  /** Whether in view mode */
  isViewMode: boolean;
  /** Current value */
  value: string;
  /** Callback when value changes */
  onChange: (value: string) => void;
  /** Placeholder text */
  placeholder?: string;
  /** Whether the field is disabled */
  disabled?: boolean;
  /** Optional label info */
  labelInfo?: string;
}

export function ItemTextField({
  label,
  isViewMode,
  value,
  onChange,
  placeholder,
  disabled = false,
  labelInfo = "(optional)",
}: ItemTextFieldProps) {
  return (
    <FormGroup label={label} labelInfo={labelInfo}>
      <ViewEditField
        isViewMode={isViewMode}
        viewContent={
          value || <span style={{ color: colors.text.muted }}>—</span>
        }
        editContent={
          <InputGroup
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            disabled={disabled}
            fill
          />
        }
      />
    </FormGroup>
  );
}
