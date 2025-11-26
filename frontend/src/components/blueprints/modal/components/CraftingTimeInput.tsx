/**
 * Crafting Time Input Component
 *
 * Allows inputting crafting time in hours, minutes, and seconds.
 * Converts to total minutes for storage.
 */

import { FormGroup, NumericInput } from "@blueprintjs/core";
import { ViewEditField } from "../../../common/ViewEditField";
import { spacing } from "../../../../styles/theme";

interface CraftingTimeInputProps {
  isViewMode: boolean;
  totalMinutes: number;
  hours: number;
  minutes: number;
  seconds: number;
  isSubmitting: boolean;
  onHoursChange: (hours: number) => void;
  onMinutesChange: (minutes: number) => void;
  onSecondsChange: (seconds: number) => void;
}

export function CraftingTimeInput({
  isViewMode,
  totalMinutes,
  hours,
  minutes,
  seconds,
  isSubmitting,
  onHoursChange,
  onMinutesChange,
  onSecondsChange,
}: CraftingTimeInputProps) {
  const formatTime = (totalMins: number): string => {
    const totalSeconds = Math.floor(totalMins * 60);
    const h = Math.floor(totalSeconds / 3600);
    const m = Math.floor((totalSeconds % 3600) / 60);
    const s = totalSeconds % 60;

    const parts: string[] = [];
    if (h > 0) parts.push(`${h}h`);
    if (m > 0) parts.push(`${m}m`);
    if (s > 0 || parts.length === 0) parts.push(`${s}s`);

    return parts.join(" ");
  };

  return (
    <FormGroup label="Crafting Time" labelInfo="(required)">
      <ViewEditField
        isViewMode={isViewMode}
        viewContent={formatTime(totalMinutes)}
        editContent={
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr 1fr",
              gap: spacing.sm,
            }}
          >
            <div>
              <label
                style={{
                  display: "block",
                  marginBottom: spacing.xs,
                  fontSize: "12px",
                  color: "var(--scims-text-secondary)",
                }}
              >
                Hours
              </label>
              <NumericInput
                value={hours}
                onValueChange={(value) => onHoursChange(value || 0)}
                min={0}
                max={999}
                disabled={isSubmitting}
                fill
              />
            </div>
            <div>
              <label
                style={{
                  display: "block",
                  marginBottom: spacing.xs,
                  fontSize: "12px",
                  color: "var(--scims-text-secondary)",
                }}
              >
                Minutes
              </label>
              <NumericInput
                value={minutes}
                onValueChange={(value) => onMinutesChange(value || 0)}
                min={0}
                max={59}
                disabled={isSubmitting}
                fill
              />
            </div>
            <div>
              <label
                style={{
                  display: "block",
                  marginBottom: spacing.xs,
                  fontSize: "12px",
                  color: "var(--scims-text-secondary)",
                }}
              >
                Seconds
              </label>
              <NumericInput
                value={seconds}
                onValueChange={(value) => onSecondsChange(value || 0)}
                min={0}
                max={59}
                disabled={isSubmitting}
                fill
              />
            </div>
          </div>
        }
      />
    </FormGroup>
  );
}
