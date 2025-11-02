/**
 * Source recommendation card component.
 * Displays a single source option with cost, reliability, and availability information.
 */

import { Card, Tag, Icon, Tooltip, Intent } from "@blueprintjs/core";
import { spacing, colors } from "../../styles/theme";
import type { SourceOption } from "../../types/optimization";

interface SourceCardProps {
  source: SourceOption;
  onSelect?: () => void;
}

function getSourceTypeLabel(sourceType: string): string {
  switch (sourceType) {
    case "stock":
      return "Own Stock";
    case "player_stock":
      return "Player Stock";
    case "universe_location":
      return "Universe Location";
    case "trading_post":
      return "Trading Post";
    default:
      return sourceType;
  }
}

function getSourceTypeIntent(sourceType: string): Intent {
  switch (sourceType) {
    case "stock":
      return Intent.SUCCESS; // Free, own stock
    case "player_stock":
      return Intent.PRIMARY; // Player trading
    case "universe_location":
      return Intent.NONE; // Neutral
    case "trading_post":
      return Intent.WARNING; // May cost money
    default:
      return Intent.NONE;
  }
}

function getReliabilityIntent(score?: number): Intent {
  if (!score) return Intent.NONE;
  if (score >= 0.8) return Intent.SUCCESS;
  if (score >= 0.5) return Intent.WARNING;
  return Intent.DANGER;
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "UEC", // Star Citizen currency
    minimumFractionDigits: 2,
  }).format(amount);
}

export default function SourceCard({ source, onSelect }: SourceCardProps) {
  const sourceTypeLabel = getSourceTypeLabel(source.source_type);
  const sourceTypeIntent = getSourceTypeIntent(source.source_type);
  const reliabilityIntent = getReliabilityIntent(source.reliability_score);

  return (
    <Card
      interactive={!!onSelect}
      onClick={onSelect}
      style={{
        marginBottom: spacing.md,
        cursor: onSelect ? "pointer" : "default",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: spacing.sm,
        }}
      >
        <div>
          <Tag intent={sourceTypeIntent} style={{ marginRight: spacing.xs }}>
            {sourceTypeLabel}
          </Tag>
          {source.reliability_score !== null &&
            source.reliability_score !== undefined && (
              <Tooltip
                content={`Reliability: ${(
                  source.reliability_score * 100
                ).toFixed(0)}%`}
              >
                <Tag intent={reliabilityIntent} minimal>
                  <Icon icon="shield" />
                  {(source.reliability_score * 100).toFixed(0)}%
                </Tag>
              </Tooltip>
            )}
        </div>
        {source.cost_per_unit === 0 && (
          <Tag intent={Intent.SUCCESS} minimal>
            FREE
          </Tag>
        )}
      </div>

      {source.location_name && (
        <div style={{ marginBottom: spacing.xs }}>
          <Icon icon="map-marker" style={{ marginRight: spacing.xs }} />
          <strong>{source.location_name}</strong>
        </div>
      )}

      {source.source_identifier && (
        <div
          style={{
            marginBottom: spacing.xs,
            color: colors.text.secondary,
            fontSize: "0.9em",
          }}
        >
          {source.source_identifier}
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: spacing.sm,
          marginTop: spacing.sm,
          paddingTop: spacing.sm,
          borderTop: `1px solid ${colors.border.medium}`,
        }}
      >
        <div>
          <div style={{ fontSize: "0.85em", color: colors.text.secondary }}>
            Available
          </div>
          <div style={{ fontWeight: "bold" }}>
            {source.available_quantity.toLocaleString()}
          </div>
        </div>
        <div>
          <div style={{ fontSize: "0.85em", color: colors.text.secondary }}>
            Total Cost
          </div>
          <div
            style={{
              fontWeight: "bold",
              color:
                source.cost_per_unit === 0
                  ? colors.success
                  : colors.text.primary,
            }}
          >
            {source.cost_per_unit === 0
              ? "Free"
              : formatCurrency(source.total_cost)}
          </div>
          {source.cost_per_unit > 0 && (
            <div style={{ fontSize: "0.8em", color: colors.text.secondary }}>
              {formatCurrency(source.cost_per_unit)}/unit
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}
