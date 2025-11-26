/**
 * Public Entity Detail page component using Blueprint.js.
 */

import { useParams, useNavigate } from "react-router-dom";
import {
  H1,
  Callout,
  Intent,
  Spinner,
  Button,
  Card,
  Tag,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import { usePublicEntity } from "../hooks/queries/commons";
import { pageHeader, sectionSpacing } from "../styles/common";
import { spacing } from "../styles/theme";

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString();
}

export default function PublicEntityDetailPage() {
  const { entityType, entityId } = useParams<{
    entityType: "item" | "recipe" | "location";
    entityId: string;
  }>();
  const navigate = useNavigate();

  const {
    data: entity,
    isLoading,
    error,
  } = usePublicEntity(entityType || "item", entityId);

  if (isLoading) {
    return (
      <DashboardLayout>
        <div style={{ textAlign: "center", padding: spacing.xl }}>
          <Spinner size={50} />
        </div>
      </DashboardLayout>
    );
  }

  if (error || !entity) {
    return (
      <DashboardLayout>
        <Callout intent={Intent.DANGER}>
          {error instanceof Error
            ? `Error loading entity: ${error.message}`
            : "Entity not found"}
        </Callout>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div
        style={{ display: "flex", gap: spacing.md, marginBottom: spacing.lg }}
      >
        <Button
          icon="arrow-left"
          text="Back to Public Commons"
          onClick={() => navigate("/commons/public")}
        />
      </div>

      <H1 style={pageHeader}>
        {entity.data.name
          ? String(entity.data.name)
          : entity.data.title
          ? String(entity.data.title)
          : "Public Entity"}
      </H1>

      <Card style={sectionSpacing}>
        <div style={{ marginBottom: spacing.md }}>
          <strong>Type: </strong>
          <Tag>{entity.entity_type}</Tag>
        </div>

        <div style={{ marginBottom: spacing.md }}>
          <strong>Version: </strong>
          <Tag>v{entity.version}</Tag>
        </div>

        {entity.tags && entity.tags.length > 0 && (
          <div style={{ marginBottom: spacing.md }}>
            <strong>Tags: </strong>
            <div
              style={{
                display: "flex",
                gap: spacing.xs,
                marginTop: spacing.xs,
              }}
            >
              {entity.tags.map((tag) => (
                <Tag key={tag} minimal>
                  {tag}
                </Tag>
              ))}
            </div>
          </div>
        )}

        <div style={{ marginBottom: spacing.md }}>
          <strong>Published: </strong>
          {formatDate(entity.created_at)}
        </div>

        <div style={{ marginTop: spacing.lg }}>
          <strong>Entity Data:</strong>
          <pre
            style={{
              marginTop: spacing.sm,
              padding: spacing.md,
              backgroundColor: "var(--scims-code-background)",
              color: "var(--scims-text-primary)",
              borderRadius: "4px",
              overflow: "auto",
              maxHeight: "600px",
            }}
          >
            {JSON.stringify(entity.data, null, 2)}
          </pre>
        </div>
      </Card>
    </DashboardLayout>
  );
}
