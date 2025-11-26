/**
 * Item Description Field Component
 */

import { FormGroup, TextArea } from "@blueprintjs/core";
import { ViewEditField } from "../../../common/ViewEditField";
import { colors } from "../../../../styles/theme";

interface ItemDescriptionFieldProps {
  /** Whether in view mode */
  isViewMode: boolean;
  /** Current description value */
  value: string;
  /** Callback when description changes */
  onChange: (value: string) => void;
  /** Whether the field is disabled */
  disabled?: boolean;
}

export function ItemDescriptionField({
  isViewMode,
  value,
  onChange,
  disabled = false,
}: ItemDescriptionFieldProps) {
  return (
    <FormGroup label="Description" labelInfo="(optional)">
      <ViewEditField
        isViewMode={isViewMode}
        viewContent={
          value || <span style={{ color: colors.text.muted }}>—</span>
        }
        editContent={
          <TextArea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Enter item description"
            disabled={disabled}
            rows={3}
            fill
          />
        }
      />
    </FormGroup>
  );
}

