/**
 * Analytics dashboard page component using Blueprint.js.
 */

import { useState } from "react";
import {
  H1,
  Card,
  Callout,
  Intent,
  Spinner,
  HTMLSelect,
  Tag,
  ProgressBar,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import { useConsent, useUsageStats } from "../hooks/queries/analytics";
import { pageHeader, sectionSpacing } from "../styles/common";
import { spacing, colors } from "../styles/theme";

export default function AnalyticsDashboardPage() {
  const { data: consent } = useConsent();
  const [periodDays, setPeriodDays] = useState(30);

  const {
    data: stats,
    isLoading,
    error,
  } = useUsageStats(periodDays, consent?.analytics_consent || false);

  if (!consent?.analytics_consent) {
    return (
      <DashboardLayout>
        <H1 style={pageHeader}>Analytics Dashboard</H1>
        <Callout intent={Intent.WARNING} style={sectionSpacing}>
          Analytics is disabled. Enable analytics in{" "}
          <a href="/analytics/consent">Privacy Settings</a> to view usage
          statistics.
        </Callout>
      </DashboardLayout>
    );
  }

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
          Error loading analytics:{" "}
          {error instanceof Error ? error.message : "Unknown error"}
        </Callout>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: spacing.lg,
        }}
      >
        <H1 style={pageHeader}>Analytics Dashboard</H1>
        <HTMLSelect
          value={periodDays}
          onChange={(e) => setPeriodDays(Number(e.target.value))}
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
          <option value={365}>Last year</option>
        </HTMLSelect>
      </div>

      {stats && (
        <>
          {/* Overview Card */}
          <Card style={{ marginBottom: spacing.lg }}>
            <h2 style={{ marginBottom: spacing.md }}>Overview</h2>
            <div style={{ display: "flex", gap: spacing.lg, flexWrap: "wrap" }}>
              <div>
                <div style={{ fontSize: "2em", fontWeight: "bold" }}>
                  {stats.total_events.toLocaleString()}
                </div>
                <div style={{ color: colors.text.secondary }}>Total Events</div>
              </div>
              <div>
                <div style={{ fontSize: "2em", fontWeight: "bold" }}>
                  {Object.keys(stats.events_by_type).length}
                </div>
                <div style={{ color: colors.text.secondary }}>Event Types</div>
              </div>
            </div>
            {stats.period_start && stats.period_end && (
              <div
                style={{ marginTop: spacing.md, color: colors.text.secondary }}
              >
                Period: {new Date(stats.period_start).toLocaleDateString()} -{" "}
                {new Date(stats.period_end).toLocaleDateString()}
              </div>
            )}
          </Card>

          {/* Events by Type */}
          {Object.keys(stats.events_by_type).length > 0 && (
            <Card style={{ marginBottom: spacing.lg }}>
              <h2 style={{ marginBottom: spacing.md }}>Events by Type</h2>
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: spacing.md,
                }}
              >
                {Object.entries(stats.events_by_type)
                  .sort(([, a], [, b]) => b - a)
                  .map(([eventType, count]) => {
                    const percentage =
                      stats.total_events > 0
                        ? (count / stats.total_events) * 100
                        : 0;
                    return (
                      <div key={eventType}>
                        <div
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            marginBottom: spacing.xs,
                          }}
                        >
                          <span>
                            <strong>{eventType.replace(/_/g, " ")}</strong>
                          </span>
                          <span style={{ color: colors.text.secondary }}>
                            {count} ({percentage.toFixed(1)}%)
                          </span>
                        </div>
                        <ProgressBar value={percentage / 100} />
                      </div>
                    );
                  })}
              </div>
            </Card>
          )}

          {/* Top Blueprints */}
          {stats.top_blueprints && stats.top_blueprints.length > 0 && (
            <Card style={{ marginBottom: spacing.lg }}>
              <h2 style={{ marginBottom: spacing.md }}>Most Used Blueprints</h2>
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: spacing.sm,
                }}
              >
                {stats.top_blueprints.map((bp) => (
                  <div
                    key={bp.blueprint_id}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      padding: spacing.sm,
                      backgroundColor: "var(--scims-background-secondary)",
                      borderRadius: "4px",
                    }}
                  >
                    <span>
                      <strong>{bp.name}</strong>
                    </span>
                    <Tag intent={Intent.PRIMARY}>{bp.uses} uses</Tag>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Top Goals */}
          {stats.top_goals && stats.top_goals.length > 0 && (
            <Card>
              <h2 style={{ marginBottom: spacing.md }}>Most Created Goals</h2>
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: spacing.sm,
                }}
              >
                {stats.top_goals.map((goal) => (
                  <div
                    key={goal.goal_id}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      padding: spacing.sm,
                      backgroundColor: "var(--scims-background-secondary)",
                      borderRadius: "4px",
                    }}
                  >
                    <span>Goal {goal.goal_id.slice(0, 8)}...</span>
                    <Tag intent={Intent.SUCCESS}>
                      {goal.created_count} created
                    </Tag>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </>
      )}
    </DashboardLayout>
  );
}
