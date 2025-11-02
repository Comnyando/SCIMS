/**
 * Analytics consent management page component using Blueprint.js.
 */

import { useState } from "react";
import {
  H1,
  Card,
  Callout,
  Intent,
  Switch,
  Spinner,
  Divider,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import { useConsent, useUpdateConsent } from "../hooks/queries/analytics";
import { pageHeader, sectionSpacing } from "../styles/common";
import { spacing } from "../styles/theme";

export default function AnalyticsConsentPage() {
  const { data: consent, isLoading, error } = useConsent();
  const updateConsent = useUpdateConsent();

  const [isUpdating, setIsUpdating] = useState(false);

  const handleConsentChange = async (checked: boolean) => {
    setIsUpdating(true);
    try {
      await updateConsent.mutateAsync({ analytics_consent: checked });
    } catch (error) {
      console.error("Failed to update consent:", error);
    } finally {
      setIsUpdating(false);
    }
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div style={{ textAlign: "center", padding: spacing.xl }}>
          <Spinner size={50} />
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <Callout intent={Intent.DANGER} style={sectionSpacing}>
          Error loading consent settings:{" "}
          {error instanceof Error ? error.message : "Unknown error"}
        </Callout>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <H1 style={pageHeader}>Analytics & Privacy</H1>

      <Card style={{ marginBottom: spacing.lg }}>
        <div style={{ marginBottom: spacing.md }}>
          <h2 style={{ marginBottom: spacing.sm }}>
            Usage Analytics & Data Collection
          </h2>
          <p style={{ color: "#666", marginBottom: spacing.md }}>
            Help us improve SCIMS by sharing anonymous usage data. This data
            helps us understand how features are used and prioritize
            improvements.
          </p>
        </div>

        <Divider />

        <div style={{ marginTop: spacing.md, marginBottom: spacing.md }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: spacing.sm,
            }}
          >
            <div>
              <strong>Enable Analytics</strong>
              <p
                style={{
                  fontSize: "0.9em",
                  color: "#666",
                  marginTop: spacing.xs,
                }}
              >
                Allow collection of anonymous usage statistics
              </p>
            </div>
            <Switch
              checked={consent?.analytics_consent || false}
              onChange={(e) =>
                handleConsentChange((e.target as HTMLInputElement).checked)
              }
              disabled={isUpdating || updateConsent.isPending}
              large
            />
          </div>
        </div>

        {updateConsent.error && (
          <Callout intent={Intent.DANGER} style={{ marginTop: spacing.md }}>
            Error updating consent:{" "}
            {updateConsent.error instanceof Error
              ? updateConsent.error.message
              : "Unknown error"}
          </Callout>
        )}

        {updateConsent.isSuccess && (
          <Callout intent={Intent.SUCCESS} style={{ marginTop: spacing.md }}>
            Consent preferences updated successfully.
          </Callout>
        )}

        <Divider style={{ marginTop: spacing.lg }} />

        <div style={{ marginTop: spacing.md }}>
          <h3 style={{ marginBottom: spacing.sm }}>What We Collect</h3>
          <ul style={{ paddingLeft: spacing.lg, color: "#666" }}>
            <li>Actions you take (crafts created, goals set, etc.)</li>
            <li>Features you use most frequently</li>
            <li>
              Aggregated statistics (no personally identifiable information)
            </li>
          </ul>

          <h3 style={{ marginTop: spacing.md, marginBottom: spacing.sm }}>
            Privacy & Security
          </h3>
          <ul style={{ paddingLeft: spacing.lg, color: "#666" }}>
            <li>IP addresses are anonymized before storage</li>
            <li>User agent strings are truncated</li>
            <li>No personal information is collected</li>
            <li>You can revoke consent at any time</li>
            <li>When consent is revoked, no new events are logged</li>
          </ul>

          <h3 style={{ marginTop: spacing.md, marginBottom: spacing.sm }}>
            How We Use This Data
          </h3>
          <ul style={{ paddingLeft: spacing.lg, color: "#666" }}>
            <li>Improve feature prioritization</li>
            <li>Understand usage patterns</li>
            <li>Identify popular blueprints and goals</li>
            <li>Guide future development decisions</li>
          </ul>
        </div>
      </Card>
    </DashboardLayout>
  );
}
