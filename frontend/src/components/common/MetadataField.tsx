/**
 * Reusable Metadata Field Component
 *
 * Handles viewing and editing JSON metadata with validation.
 * Can be used in any modal that needs metadata editing.
 */

import { FormGroup, TextArea, Intent, Callout } from "@blueprintjs/core";
import { ViewEditField } from "./ViewEditField";
import { spacing, colors } from "../../styles/theme";

interface MetadataFieldProps {
  /** Whether in view mode */
  isViewMode: boolean;
  /** Current metadata JSON string */
  value: string;
  /** Callback when metadata changes */
  onChange: (value: string) => void;
  /** Whether the field is disabled */
  disabled?: boolean;
  /** Optional label override */
  label?: string;
  /** Optional label info */
  labelInfo?: string;
}

export function MetadataField({
  isViewMode,
  value,
  onChange,
  disabled = false,
  label = "Metadata",
  labelInfo = "(optional)",
}: MetadataFieldProps) {
  const isValidJson = (): boolean => {
    if (!value.trim()) return true; // Empty is valid
    try {
      JSON.parse(value);
      return true;
    } catch {
      return false;
    }
  };

  const isValid = isValidJson();

  return (
    <FormGroup
      label={label}
      labelInfo={labelInfo}
      helperText={
        isViewMode
          ? undefined
          : "Additional metadata as JSON. Must be valid JSON format."
      }
    >
      <ViewEditField
        isViewMode={isViewMode}
        viewContent={
          value.trim() ? (
            <pre
              style={{
                fontFamily: "monospace",
                fontSize: "12px",
                margin: 0,
                whiteSpace: "pre-wrap",
              }}
            >
              {value}
            </pre>
          ) : (
            <span style={{ color: colors.text.muted }}>No metadata</span>
          )
        }
        editContent={
          <>
            <TextArea
              value={value}
              onChange={(e) => onChange(e.target.value)}
              placeholder='{"key": "value"}'
              disabled={disabled}
              rows={6}
              fill
              style={{ fontFamily: "monospace", fontSize: "12px" }}
            />
            {value.trim() && (
              <Callout
                intent={isValid ? Intent.SUCCESS : Intent.DANGER}
                style={{ marginTop: spacing.xs }}
              >
                {isValid ? "Valid JSON" : "Invalid JSON format"}
              </Callout>
            )}
          </>
        }
      />
    </FormGroup>
  );
}
