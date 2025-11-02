/**
 * Craft detail page component with progress tracking using Blueprint.js.
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
  ProgressBar,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import {
  useCraft,
  useCraftProgress,
  useDeleteCraft,
  useStartCraft,
  useCompleteCraft,
} from "../hooks/queries/crafts";
import ResourceGapView from "../components/optimization/ResourceGapView";
import { pageHeader, sectionSpacing } from "../styles/common";
import { spacing, colors } from "../styles/theme";
import { useAuth } from "../contexts/AuthContext";
import type { CraftStatus, IngredientStatus } from "../types";

const STATUS_COLORS: Record<CraftStatus, Intent> = {
  planned: Intent.NONE,
  in_progress: Intent.PRIMARY,
  completed: Intent.SUCCESS,
  cancelled: Intent.DANGER,
};

const INGREDIENT_STATUS_COLORS: Record<IngredientStatus, Intent> = {
  pending: Intent.NONE,
  reserved: Intent.WARNING,
  fulfilled: Intent.SUCCESS,
};

function formatTime(minutes: number | null): string {
  if (minutes === null) return "-";
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hours > 0) {
    return `${hours}h ${mins}m`;
  }
  return `${mins}m`;
}

function formatDate(dateString: string | null): string {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date.toLocaleString();
}

export default function CraftDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const {
    data: craft,
    isLoading,
    error,
  } = useCraft({
    id: id || "",
    include_ingredients: true,
  });
  const { data: progress } = useCraftProgress({ id: id || "" });
  const deleteCraft = useDeleteCraft();
  const startCraft = useStartCraft();
  const completeCraft = useCompleteCraft();

  const handleDelete = async () => {
    if (
      !id ||
      !window.confirm(
        "Are you sure you want to delete this craft? This will unreserve any reserved ingredients."
      )
    ) {
      return;
    }

    try {
      await deleteCraft.mutateAsync({
        id,
        unreserve_ingredients: true,
      });
      navigate("/crafts");
    } catch (err) {
      console.error("Failed to delete craft:", err);
    }
  };

  const handleStart = async () => {
    if (!id) return;
    try {
      await startCraft.mutateAsync({
        id,
        reserve_missing_ingredients: true,
      });
    } catch (err) {
      console.error("Failed to start craft:", err);
    }
  };

  const handleComplete = async () => {
    if (!id) return;
    try {
      await completeCraft.mutateAsync(id);
    } catch (err) {
      console.error("Failed to complete craft:", err);
    }
  };

  const isOwner = craft && user && craft.requested_by === user.id;

  if (isLoading) {
    return (
      <DashboardLayout>
        <div style={{ textAlign: "center", padding: spacing.xl }}>
          <Spinner size={50} />
        </div>
      </DashboardLayout>
    );
  }

  if (error || !craft) {
    return (
      <DashboardLayout>
        <Callout intent={Intent.DANGER} style={sectionSpacing}>
          {error instanceof Error ? error.message : "Craft not found"}
        </Callout>
        <Button
          icon="arrow-left"
          text="Back to Crafts"
          onClick={() => navigate("/crafts")}
        />
      </DashboardLayout>
    );
  }

  // Calculate progress percentage for in-progress crafts
  const progressPercent =
    craft.status === "in_progress" && craft.started_at && craft.blueprint
      ? (() => {
          const started = new Date(craft.started_at);
          const now = new Date();
          const elapsed = Math.floor(
            (now.getTime() - started.getTime()) / 60000
          );
          const total = craft.blueprint.crafting_time_minutes;
          return Math.min(100, Math.round((elapsed / total) * 100));
        })()
      : craft.status === "completed"
      ? 100
      : 0;

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
          <H1 style={pageHeader}>
            {craft.blueprint?.name || "Unknown Blueprint"}
          </H1>
          <Tag
            intent={STATUS_COLORS[craft.status]}
            style={{ marginTop: spacing.sm }}
            data-tour="craft-status"
          >
            {craft.status.replace("_", " ").toUpperCase()}
          </Tag>
          {craft.priority > 0 && (
            <Tag style={{ marginTop: spacing.sm, marginLeft: spacing.sm }}>
              Priority: {craft.priority}
            </Tag>
          )}
        </div>
        {isOwner && craft.status === "planned" && (
          <div data-tour="craft-actions">
            <Button
              icon="play"
              text="Start Craft"
              intent="primary"
              style={{ marginRight: spacing.sm }}
              onClick={handleStart}
              loading={startCraft.isPending}
            />
            <Button
              icon="trash"
              text="Delete"
              intent="danger"
              onClick={handleDelete}
              loading={deleteCraft.isPending}
            />
          </div>
        )}
        {isOwner && craft.status === "in_progress" && (
          <div data-tour="craft-actions">
            <Button
              icon="tick-circle"
              text="Complete Craft"
              intent="success"
              onClick={handleComplete}
              loading={completeCraft.isPending}
            />
          </div>
        )}
      </div>

      {/* Progress Section for In-Progress Crafts */}
      {craft.status === "in_progress" && progress && (
        <Card style={{ marginBottom: spacing.lg }} data-tour="craft-progress">
          <H3>Progress</H3>
          <Divider style={{ margin: `${spacing.sm} 0 ${spacing.md} 0` }} />
          <div style={{ marginBottom: spacing.md }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: spacing.xs,
              }}
            >
              <span>
                <strong>{progressPercent}%</strong> Complete
              </span>
              {progress.estimated_completion_minutes !== null && (
                <span style={{ color: colors.text.secondary }}>
                  ~{formatTime(progress.estimated_completion_minutes)} remaining
                </span>
              )}
            </div>
            <ProgressBar
              value={progressPercent / 100}
              intent={Intent.PRIMARY}
              animate
            />
          </div>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr 1fr",
              gap: spacing.md,
              marginTop: spacing.md,
            }}
          >
            <div>
              <strong>Elapsed:</strong>{" "}
              {progress.elapsed_minutes !== null
                ? formatTime(progress.elapsed_minutes)
                : "-"}
            </div>
            <div>
              <strong>Total Time:</strong>{" "}
              {formatTime(progress.crafting_time_minutes)}
            </div>
            <div>
              <strong>Started:</strong> {formatDate(craft.started_at)}
            </div>
          </div>
        </Card>
      )}

      {/* Craft Information */}
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
            <strong>{craft.blueprint?.output_quantity || 1}x</strong>{" "}
            {craft.blueprint?.output_item_id || "Unknown Item ID"}
          </p>
          <p style={{ color: colors.text.secondary, marginTop: spacing.xs }}>
            To: {craft.output_location?.name || "Unknown Location"}
          </p>
        </Card>

        <Card data-tour="craft-timeline">
          <H3>Timeline</H3>
          <Divider style={{ margin: `${spacing.sm} 0` }} />
          <div style={{ fontSize: "0.9em" }}>
            <div style={{ marginBottom: spacing.xs }}>
              <strong>Created:</strong> {formatDate(craft.created_at)}
            </div>
            {craft.scheduled_start && (
              <div style={{ marginBottom: spacing.xs }}>
                <strong>Scheduled:</strong> {formatDate(craft.scheduled_start)}
              </div>
            )}
            {craft.started_at && (
              <div style={{ marginBottom: spacing.xs }}>
                <strong>Started:</strong> {formatDate(craft.started_at)}
              </div>
            )}
            {craft.completed_at && (
              <div style={{ marginBottom: spacing.xs }}>
                <strong>Completed:</strong> {formatDate(craft.completed_at)}
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Resource Gap Analysis */}
      {id && craft.status === "planned" && (
        <div style={{ marginBottom: spacing.lg }}>
          <ResourceGapView craftId={id} />
        </div>
      )}

      {/* Ingredients Section */}
      {craft.ingredients && craft.ingredients.length > 0 && (
        <Card style={{ marginBottom: spacing.lg }} data-tour="ingredients-list">
          <H3>Ingredients</H3>
          <Divider style={{ margin: `${spacing.sm} 0 ${spacing.md} 0` }} />
          {progress && (
            <div
              style={{
                display: "flex",
                gap: spacing.md,
                marginBottom: spacing.md,
                padding: spacing.sm,
                backgroundColor: colors.background.secondary,
                borderRadius: "4px",
              }}
            >
              <span>
                <strong>Total:</strong> {progress.ingredients_status.total}
              </span>
              <span>
                <strong>Pending:</strong>{" "}
                <Tag minimal intent={Intent.NONE}>
                  {progress.ingredients_status.pending}
                </Tag>
              </span>
              <span>
                <strong>Reserved:</strong>{" "}
                <Tag minimal intent={Intent.WARNING}>
                  {progress.ingredients_status.reserved}
                </Tag>
              </span>
              <span>
                <strong>Fulfilled:</strong>{" "}
                <Tag minimal intent={Intent.SUCCESS}>
                  {progress.ingredients_status.fulfilled}
                </Tag>
              </span>
            </div>
          )}
          <ul style={{ listStyle: "none", padding: 0 }}>
            {craft.ingredients.map((ingredient) => (
              <li
                key={ingredient.id}
                style={{
                  padding: spacing.sm,
                  marginBottom: spacing.xs,
                  backgroundColor: colors.background.tertiary,
                  borderRadius: "4px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <strong>{ingredient.required_quantity}x</strong>{" "}
                  {ingredient.item?.name || ingredient.item_id}
                  {ingredient.source_location && (
                    <span
                      style={{
                        color: colors.text.secondary,
                        marginLeft: spacing.xs,
                      }}
                    >
                      (from {ingredient.source_location.name})
                    </span>
                  )}
                </div>
                <Tag
                  intent={INGREDIENT_STATUS_COLORS[ingredient.status]}
                  minimal
                >
                  {ingredient.status.toUpperCase()}
                </Tag>
              </li>
            ))}
          </ul>
        </Card>
      )}

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
          text="Back to Crafts"
          onClick={() => navigate("/crafts")}
        />
        {craft.blueprint && (
          <Button
            icon="document"
            text="View Blueprint"
            onClick={() => navigate(`/blueprints/${craft.blueprint_id}`)}
          />
        )}
      </div>
    </DashboardLayout>
  );
}
