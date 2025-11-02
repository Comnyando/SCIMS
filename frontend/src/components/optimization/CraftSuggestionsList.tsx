/**
 * Craft suggestions list component for displaying suggest-crafts results.
 */

import {
  Card,
  H3,
  Divider,
  Callout,
  Intent,
  Tag,
  Button,
  Spinner,
  Icon,
} from "@blueprintjs/core";
import { spacing, colors } from "../../styles/theme";
import { useSuggestCrafts } from "../../hooks/queries/optimization";
import type { SuggestCraftsRequest } from "../../types/optimization";

interface CraftSuggestionsListProps {
  request: SuggestCraftsRequest;
  onBlueprintSelect?: (blueprintId: string) => void;
}

function formatTime(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hours > 0) {
    return `${hours}h ${mins}m`;
  }
  return `${mins}m`;
}

export default function CraftSuggestionsList({
  request,
  onBlueprintSelect,
}: CraftSuggestionsListProps) {
  const { data, isLoading, error, refetch } = useSuggestCrafts({ request });

  if (isLoading) {
    return (
      <Card>
        <div style={{ textAlign: "center", padding: spacing.xl }}>
          <Spinner />
          <div style={{ marginTop: spacing.md }}>
            Finding craft suggestions...
          </div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Callout intent={Intent.DANGER} icon="error">
        Failed to find craft suggestions:{" "}
        {error instanceof Error ? error.message : "Unknown error"}
        <div style={{ marginTop: spacing.sm }}>
          <Button text="Retry" onClick={() => refetch()} small />
        </div>
      </Callout>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <Card>
      <H3>
        Craft Suggestions for {data.target_item_name || data.target_item_id}
        <Tag style={{ marginLeft: spacing.sm }}>
          Target: {data.target_quantity.toLocaleString()}
        </Tag>
      </H3>
      <Divider style={{ margin: `${spacing.sm} 0 ${spacing.md} 0` }} />

      {data.suggestions.length === 0 ? (
        <Callout intent={Intent.NONE}>
          No blueprints found that produce this item. You may need to:
          <ul style={{ marginTop: spacing.sm, paddingLeft: spacing.lg }}>
            <li>Create a blueprint for this item</li>
            <li>Check if the item can be crafted</li>
            <li>Browse public blueprints</li>
          </ul>
        </Callout>
      ) : (
        <div>
          {data.suggestions.map((suggestion) => (
            <Card
              key={suggestion.blueprint_id}
              interactive={!!onBlueprintSelect}
              onClick={() => onBlueprintSelect?.(suggestion.blueprint_id)}
              style={{
                marginBottom: spacing.md,
                cursor: onBlueprintSelect ? "pointer" : "default",
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
                  <strong>{suggestion.blueprint_name}</strong>
                  {suggestion.all_ingredients_available && (
                    <Tag
                      intent={Intent.SUCCESS}
                      style={{ marginLeft: spacing.xs }}
                    >
                      <Icon icon="tick" />
                      All Ingredients Available
                    </Tag>
                  )}
                  {!suggestion.all_ingredients_available && (
                    <Tag
                      intent={Intent.WARNING}
                      style={{ marginLeft: spacing.xs }}
                    >
                      <Icon icon="warning-sign" />
                      Missing Ingredients
                    </Tag>
                  )}
                </div>
                <Tag>{suggestion.suggested_count}x crafts</Tag>
              </div>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr 1fr",
                  gap: spacing.md,
                  marginTop: spacing.sm,
                  paddingTop: spacing.sm,
                  borderTop: `1px solid ${colors.border.medium}`,
                }}
              >
                <div>
                  <div
                    style={{ fontSize: "0.85em", color: colors.text.secondary }}
                  >
                    Output per Craft
                  </div>
                  <div style={{ fontWeight: "bold" }}>
                    {suggestion.output_quantity.toLocaleString()}
                  </div>
                </div>
                <div>
                  <div
                    style={{ fontSize: "0.85em", color: colors.text.secondary }}
                  >
                    Total Output
                  </div>
                  <div style={{ fontWeight: "bold" }}>
                    {suggestion.total_output.toLocaleString()}
                  </div>
                </div>
                <div>
                  <div
                    style={{ fontSize: "0.85em", color: colors.text.secondary }}
                  >
                    Total Time
                  </div>
                  <div style={{ fontWeight: "bold" }}>
                    {formatTime(
                      suggestion.crafting_time_minutes *
                        suggestion.suggested_count
                    )}
                  </div>
                  <div
                    style={{ fontSize: "0.8em", color: colors.text.secondary }}
                  >
                    {formatTime(suggestion.crafting_time_minutes)} per craft
                  </div>
                </div>
              </div>

              {suggestion.ingredients.length > 0 && (
                <div style={{ marginTop: spacing.sm }}>
                  <div
                    style={{
                      fontSize: "0.85em",
                      color: colors.text.secondary,
                      marginBottom: spacing.xs,
                    }}
                  >
                    Ingredients (per craft):
                  </div>
                  <div
                    style={{
                      display: "flex",
                      flexWrap: "wrap",
                      gap: spacing.xs,
                    }}
                  >
                    {suggestion.ingredients.map((ing, idx) => (
                      <Tag
                        key={idx}
                        intent={
                          ing.available >= ing.quantity
                            ? Intent.SUCCESS
                            : ing.available > 0
                            ? Intent.WARNING
                            : Intent.DANGER
                        }
                        minimal
                      >
                        {ing.quantity} needed ({ing.available} available)
                      </Tag>
                    ))}
                  </div>
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </Card>
  );
}
