/**
 * Sources list component for displaying find-sources results.
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
} from "@blueprintjs/core";
import { spacing } from "../../styles/theme";
import { useFindSources } from "../../hooks/queries/optimization";
import SourceCard from "./SourceCard";
import type { FindSourcesRequest } from "../../types/optimization";

interface SourcesListProps {
  request: FindSourcesRequest;
  onSourceSelect?: (sourceId?: string) => void;
}

export default function SourcesList({
  request,
  onSourceSelect,
}: SourcesListProps) {
  const { data, isLoading, error, refetch } = useFindSources({ request });

  if (isLoading) {
    return (
      <Card>
        <div style={{ textAlign: "center", padding: spacing.xl }}>
          <Spinner />
          <div style={{ marginTop: spacing.md }}>Finding sources...</div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Callout intent={Intent.DANGER} icon="error">
        Failed to find sources:{" "}
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
        Sources for {data.item_name || data.item_id}
        {data.required_quantity && (
          <Tag style={{ marginLeft: spacing.sm }}>
            Need: {data.required_quantity.toLocaleString()}
          </Tag>
        )}
      </H3>
      <Divider style={{ margin: `${spacing.sm} 0 ${spacing.md} 0` }} />

      <div style={{ marginBottom: spacing.md }}>
        <Callout
          intent={data.has_sufficient ? Intent.SUCCESS : Intent.WARNING}
          icon={data.has_sufficient ? "tick-circle" : "warning-sign"}
        >
          {data.has_sufficient ? (
            <>
              <strong>Sufficient sources available!</strong> Total available:{" "}
              {data.total_available.toLocaleString()} units
            </>
          ) : (
            <>
              <strong>Insufficient sources.</strong> Only{" "}
              {data.total_available.toLocaleString()} units available (need{" "}
              {data.required_quantity.toLocaleString()})
            </>
          )}
        </Callout>
      </div>

      {data.sources.length === 0 ? (
        <Callout intent={Intent.NONE}>
          No sources found for this item. You may need to:
          <ul style={{ marginTop: spacing.sm, paddingLeft: spacing.lg }}>
            <li>Check your inventory stock</li>
            <li>Add resource sources manually</li>
            <li>Verify source tracking is enabled</li>
          </ul>
        </Callout>
      ) : (
        <div>
          {data.sources.map((source, idx) => (
            <SourceCard
              key={idx}
              source={source}
              onSelect={() => onSourceSelect?.(source.source_id)}
            />
          ))}
        </div>
      )}
    </Card>
  );
}
