/**
 * Duplicate Finder page component using Blueprint.js.
 */

import { useState } from "react";
import { H1, Callout, Intent, Spinner } from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import { pageHeader } from "../styles/common";
import { spacing } from "../styles/theme";

export default function DuplicateFinderPage() {
  const [isLoading] = useState(false);

  return (
    <DashboardLayout>
      <H1 style={pageHeader}>Duplicate Finder</H1>

      <Callout intent={Intent.WARNING} style={{ marginTop: spacing.lg }}>
        <h4>Coming Soon</h4>
        <p>
          The Duplicate Finder UI will allow moderators to review and merge
          duplicate entities in the commons. This feature will be available in a
          future update.
        </p>
        <p style={{ marginTop: spacing.sm }}>
          For now, duplicates can be handled manually through the moderation
          dashboard by using the merge action on submissions.
        </p>
      </Callout>

      {isLoading && (
        <div style={{ textAlign: "center", padding: spacing.xl }}>
          <Spinner size={50} />
        </div>
      )}
    </DashboardLayout>
  );
}
