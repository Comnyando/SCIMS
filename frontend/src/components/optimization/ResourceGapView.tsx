/**
 * Resource gap visualization component.
 * Displays gaps for craft ingredients with available sources.
 */

import {
  Card,
  H3,
  Divider,
  Tag,
  Callout,
  Intent,
  ProgressBar,
  Icon,
  Button,
} from "@blueprintjs/core";
import { spacing, colors } from "../../styles/theme";
import { useResourceGap } from "../../hooks/queries/optimization";
import SourceCard from "./SourceCard";
import type { ResourceGapItem } from "../../types/optimization";

interface ResourceGapViewProps {
  craftId: string;
  onRefresh?: () => void;
}

function getGapIntent(gapQuantity: number): Intent {
  if (gapQuantity <= 0) return Intent.SUCCESS;
  if (gapQuantity <= 10) return Intent.WARNING;
  return Intent.DANGER;
}

function GapItemCard({ gap }: { gap: ResourceGapItem }) {
  const gapIntent = getGapIntent(gap.gap_quantity);
  const hasSurplus = gap.gap_quantity < 0;
  const hasGap = gap.gap_quantity > 0;

  return (
    <Card style={{ marginBottom: spacing.md }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: spacing.sm,
        }}
      >
        <div>
          <strong>{gap.item_name || gap.item_id}</strong>
        </div>
        <Tag intent={gapIntent}>
          {hasSurplus ? (
            <>
              <Icon icon="tick-circle" style={{ marginRight: spacing.xs }} />
              Surplus: {Math.abs(gap.gap_quantity).toFixed(1)}
            </>
          ) : hasGap ? (
            <>
              <Icon icon="warning-sign" style={{ marginRight: spacing.xs }} />
              Missing: {gap.gap_quantity.toFixed(1)}
            </>
          ) : (
            <>
              <Icon icon="tick" style={{ marginRight: spacing.xs }} />
              Available
            </>
          )}
        </Tag>
      </div>

      <div style={{ marginBottom: spacing.sm }}>
        <ProgressBar
          value={Math.min(1, gap.available_quantity / gap.required_quantity)}
          intent={gapIntent}
          stripes={false}
        />
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            fontSize: "0.85em",
            color: colors.text.secondary,
            marginTop: spacing.xs,
          }}
        >
          <span>Available: {gap.available_quantity.toFixed(1)}</span>
          <span>Required: {gap.required_quantity.toFixed(1)}</span>
        </div>
      </div>

      {hasGap && gap.sources.length > 0 && (
        <>
          <Divider style={{ margin: `${spacing.sm} 0` }} />
          <div style={{ marginTop: spacing.sm }}>
            <div
              style={{
                marginBottom: spacing.xs,
                fontSize: "0.9em",
                fontWeight: "bold",
              }}
            >
              Available Sources:
            </div>
            {gap.sources.slice(0, 3).map((source, idx) => (
              <SourceCard key={idx} source={source} />
            ))}
            {gap.sources.length > 3 && (
              <div
                style={{
                  fontSize: "0.85em",
                  color: colors.text.secondary,
                  marginTop: spacing.xs,
                }}
              >
                +{gap.sources.length - 3} more sources available
              </div>
            )}
          </div>
        </>
      )}

      {hasGap && gap.sources.length === 0 && (
        <Callout
          intent={Intent.WARNING}
          icon="warning-sign"
          style={{ marginTop: spacing.sm }}
        >
          No sources found for this item. You may need to acquire it manually or
          check source tracking.
        </Callout>
      )}
    </Card>
  );
}

export default function ResourceGapView({
  craftId,
  onRefresh,
}: ResourceGapViewProps) {
  const {
    data: gapData,
    isLoading,
    error,
    refetch,
  } = useResourceGap({ craftId });

  const handleRefresh = () => {
    refetch();
    onRefresh?.();
  };

  if (isLoading) {
    return (
      <Card>
        <div style={{ textAlign: "center", padding: spacing.xl }}>
          Loading resource gap analysis...
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Callout intent={Intent.DANGER} icon="error">
        Failed to load resource gap analysis:{" "}
        {error instanceof Error ? error.message : "Unknown error"}
      </Callout>
    );
  }

  if (!gapData) {
    return null;
  }

  const hasGaps = gapData.total_gaps > 0;
  const canProceed = gapData.can_proceed;

  return (
    <Card>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: spacing.md,
        }}
      >
        <H3>Resource Gap Analysis</H3>
        <Button
          icon="refresh"
          text="Refresh"
          minimal
          onClick={handleRefresh}
          small
        />
      </div>

      <Divider style={{ marginBottom: spacing.md }} />

      {gapData.blueprint_name && (
        <div style={{ marginBottom: spacing.md }}>
          <strong>Blueprint:</strong> {gapData.blueprint_name}
        </div>
      )}

      <div style={{ marginBottom: spacing.md }}>
        <Callout
          intent={canProceed ? Intent.SUCCESS : Intent.WARNING}
          icon={canProceed ? "tick-circle" : "warning-sign"}
        >
          {canProceed ? (
            <>
              <strong>Ready to proceed!</strong> All ingredients are available
              or have sources to acquire them.
            </>
          ) : (
            <>
              <strong>Missing resources detected.</strong> Review the gaps below
              and acquire missing ingredients before starting the craft.
            </>
          )}
        </Callout>
      </div>

      <div style={{ marginBottom: spacing.md }}>
        <div
          style={{ display: "flex", gap: spacing.md, marginBottom: spacing.sm }}
        >
          <Tag>Total Ingredients: {gapData.gaps.length}</Tag>
          <Tag intent={hasGaps ? Intent.WARNING : Intent.SUCCESS}>
            Gaps: {gapData.total_gaps}
          </Tag>
          <Tag intent={canProceed ? Intent.SUCCESS : Intent.DANGER}>
            Status: {canProceed ? "Ready" : "Not Ready"}
          </Tag>
        </div>
      </div>

      <div>
        {gapData.gaps.length === 0 ? (
          <Callout intent={Intent.NONE}>
            No ingredients found for this craft.
          </Callout>
        ) : (
          gapData.gaps.map((gap) => <GapItemCard key={gap.item_id} gap={gap} />)
        )}
      </div>
    </Card>
  );
}
