/**
 * Blueprint detail/view page component using Blueprint.js.
 */

import { useParams, useNavigate } from "react-router-dom";
import {
  H1,
  H3,
  Callout,
  Intent,
  Spinner,
  Button,
  Tag,
  Card,
  Divider,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import { useBlueprint, useDeleteBlueprint } from "../hooks/queries/blueprints";
import { pageHeader, sectionSpacing } from "../styles/common";
import { spacing, colors } from "../styles/theme";
import { useAuth } from "../contexts/AuthContext";

export default function BlueprintDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { data: blueprint, isLoading, error } = useBlueprint({ id: id || "" });
  const deleteBlueprint = useDeleteBlueprint();

  const handleDelete = async () => {
    if (
      !id ||
      !window.confirm("Are you sure you want to delete this blueprint?")
    ) {
      return;
    }

    try {
      await deleteBlueprint.mutateAsync(id);
      navigate("/blueprints");
    } catch (err) {
      console.error("Failed to delete blueprint:", err);
    }
  };

  const handleEdit = () => {
    navigate(`/blueprints/${id}/edit`);
  };

  const isOwner = blueprint && user && blueprint.created_by === user.id;

  if (isLoading) {
    return (
      <DashboardLayout>
        <div style={{ textAlign: "center", padding: spacing.xl }}>
          <Spinner size={50} />
        </div>
      </DashboardLayout>
    );
  }

  if (error || !blueprint) {
    return (
      <DashboardLayout>
        <Callout intent={Intent.DANGER} style={sectionSpacing}>
          {error instanceof Error ? error.message : "Blueprint not found"}
        </Callout>
        <Button
          icon="arrow-left"
          text="Back to Blueprints"
          onClick={() => navigate("/blueprints")}
        />
      </DashboardLayout>
    );
  }

  const craftingHours = Math.floor(blueprint.crafting_time_minutes / 60);
  const craftingMinutes = blueprint.crafting_time_minutes % 60;
  const craftingTimeDisplay =
    craftingHours > 0
      ? `${craftingHours}h ${craftingMinutes}m`
      : `${craftingMinutes}m`;

  return (
    <DashboardLayout>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: spacing.lg,
        }}
      >
        <div>
          <H1 style={pageHeader}>{blueprint.name}</H1>
          {blueprint.category && (
            <Tag style={{ marginTop: spacing.sm }}>{blueprint.category}</Tag>
          )}
          <Tag
            intent={blueprint.is_public ? "success" : "none"}
            style={{ marginTop: spacing.sm, marginLeft: spacing.sm }}
          >
            {blueprint.is_public ? "Public" : "Private"}
          </Tag>
        </div>
        {isOwner && (
          <div>
            <Button
              icon="edit"
              text="Edit"
              intent="primary"
              style={{ marginRight: spacing.sm }}
              onClick={handleEdit}
            />
            <Button
              icon="trash"
              text="Delete"
              intent="danger"
              onClick={handleDelete}
              loading={deleteBlueprint.isPending}
            />
          </div>
        )}
      </div>

      {blueprint.description && (
        <Callout style={{ marginBottom: spacing.lg }}>
          {blueprint.description}
        </Callout>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: spacing.lg,
          marginBottom: spacing.lg,
        }}
      >
        <Card>
          <H3>Output</H3>
          <Divider style={{ margin: `${spacing.sm} 0` }} />
          <p>
            <strong>{blueprint.output_quantity}x</strong>{" "}
            {blueprint.output_item?.name || blueprint.output_item_id}
          </p>
          {blueprint.output_item?.category && (
            <Tag style={{ marginTop: spacing.xs }}>
              {blueprint.output_item.category}
            </Tag>
          )}
        </Card>

        <Card>
          <H3>Crafting Time</H3>
          <Divider style={{ margin: `${spacing.sm} 0` }} />
          <p style={{ fontSize: "1.2em", fontWeight: "bold" }}>
            {craftingTimeDisplay}
          </p>
        </Card>
      </div>

      <Card>
        <H3>Ingredients</H3>
        <Divider style={{ margin: `${spacing.sm} 0 ${spacing.md} 0` }} />
        {blueprint.blueprint_data.ingredients.length === 0 ? (
          <p style={{ color: colors.text.secondary }}>
            No ingredients required
          </p>
        ) : (
          <ul style={{ listStyle: "none", padding: 0 }}>
            {blueprint.blueprint_data.ingredients.map((ingredient, idx) => (
              <li
                key={idx}
                style={{
                  padding: spacing.sm,
                  marginBottom: spacing.xs,
                  backgroundColor: "var(--scims-background-tertiary)",
                  borderRadius: "4px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <span>
                  <strong>{ingredient.quantity}x</strong> Item ID:{" "}
                  {ingredient.item_id}
                  {ingredient.optional && (
                    <Tag
                      minimal
                      intent="warning"
                      style={{ marginLeft: spacing.xs }}
                    >
                      Optional
                    </Tag>
                  )}
                </span>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <div
        style={{
          marginTop: spacing.lg,
          display: "flex",
          gap: spacing.md,
          alignItems: "center",
        }}
      >
        <Button
          icon="arrow-left"
          text="Back to Blueprints"
          onClick={() => navigate("/blueprints")}
        />
        <span style={{ color: colors.text.secondary }}>
          Used {blueprint.usage_count} times • Created{" "}
          {new Date(blueprint.created_at).toLocaleDateString()}
        </span>
      </div>
    </DashboardLayout>
  );
}
