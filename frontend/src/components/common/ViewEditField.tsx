/**
 * Helper component for rendering fields in view or edit mode.
 */

import { ReactNode } from "react";
import { colors } from "../../styles/theme";
import { themeStyles } from "../../utils/theme";

interface ViewEditFieldProps {
  /** Whether in view mode */
  isViewMode: boolean;
  /** Content to show in view mode */
  viewContent: ReactNode;
  /** Content to show in edit mode */
  editContent: ReactNode;
}

export function ViewEditField({
  isViewMode,
  viewContent,
  editContent,
}: ViewEditFieldProps) {
  if (isViewMode) {
    return (
      <div style={themeStyles.viewField}>
        {viewContent || <span style={{ color: colors.text.muted }}>—</span>}
      </div>
    );
  }

  return <>{editContent}</>;
}
