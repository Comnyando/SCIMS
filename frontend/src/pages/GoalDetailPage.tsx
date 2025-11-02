/**
 * Goal detail page component using Blueprint.js.
 */

import { useNavigate, useParams } from "react-router-dom";
import {
  H1,
  H3,
  Callout,
  Intent,
  Spinner,
  Button,
  Tag,
  Card,
  ProgressBar,
  Divider,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import {
  useGoal,
  useGoalProgress,
  useDeleteGoal,
} from "../hooks/queries/goals";
import { pageHeader, sectionSpacing } from "../styles/common";
import { spacing, colors } from "../styles/theme";

function formatDate(dateString: string | null): string {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date.toLocaleString();
}

export default function GoalDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: goal, isLoading, error } = useGoal({ id: id || "" });
  const { data: progress } = useGoalProgress({
    id: id || "",
    recalculate: false,
  });
  const deleteGoal = useDeleteGoal();

  const handleDelete = async () => {
    if (!id || !window.confirm("Are you sure you want to delete this goal?")) {
      return;
    }

    try {
      await deleteGoal.mutateAsync(id);
      navigate("/goals");
    } catch (error) {
      console.error("Failed to delete goal:", error);
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

  if (error || !goal) {
    return (
      <DashboardLayout>
        <Callout intent={Intent.DANGER} style={sectionSpacing}>
          {error instanceof Error ? error.message : "Goal not found"}
        </Callout>
        <Button
          icon="arrow-left"
          text="Back to Goals"
          onClick={() => navigate("/goals")}
        />
      </DashboardLayout>
    );
  }

  const progressData = progress?.progress || {
    current_quantity: 0,
    target_quantity: goal.goal_items.reduce(
      (sum, item) => sum + item.target_quantity,
      0
    ),
    progress_percentage: 0,
    is_completed: false,
    days_remaining: null,
    item_progress: [],
  };

  const STATUS_COLORS: Record<string, Intent> = {
    active: Intent.PRIMARY,
    completed: Intent.SUCCESS,
    cancelled: Intent.DANGER,
  };

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
        <H1 style={pageHeader}>{goal.name}</H1>
        <div style={{ display: "flex", gap: spacing.sm }}>
          {goal.status === "active" && (
            <Button
              icon="edit"
              text="Edit"
              onClick={() => navigate(`/goals/${goal.id}/edit`)}
            />
          )}
          {goal.status !== "completed" && (
            <Button
              icon="delete"
              text="Delete"
              intent="danger"
              onClick={handleDelete}
              loading={deleteGoal.isPending}
            />
          )}
          <Button
            icon="arrow-left"
            text="Back to Goals"
            onClick={() => navigate("/goals")}
          />
        </div>
      </div>

      <Card style={{ marginBottom: spacing.lg }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: spacing.md,
          }}
        >
          <Tag intent={STATUS_COLORS[goal.status]}>
            {goal.status.toUpperCase()}
          </Tag>
          {goal.organization && <Tag>{goal.organization.name}</Tag>}
        </div>

        {goal.description && (
          <p style={{ marginBottom: spacing.md, color: colors.text.secondary }}>
            {goal.description}
          </p>
        )}

        <Divider />

        <div style={{ marginTop: spacing.md }}>
          <H3>Overall Progress</H3>
          <div style={{ marginTop: spacing.md, marginBottom: spacing.md }}>
            <ProgressBar
              value={progressData.progress_percentage / 100}
              intent={
                progressData.is_completed
                  ? Intent.SUCCESS
                  : progressData.progress_percentage >= 50
                  ? Intent.PRIMARY
                  : Intent.WARNING
              }
              animate={goal.status === "active"}
            />
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginTop: spacing.sm,
                color: colors.text.secondary,
              }}
            >
              <span>
                {progressData.current_quantity.toFixed(2)} /{" "}
                {progressData.target_quantity.toFixed(2)} total
              </span>
              <span>{progressData.progress_percentage.toFixed(1)}%</span>
            </div>
          </div>

          {progressData.days_remaining !== null && (
            <p
              style={{ color: colors.text.secondary, marginBottom: spacing.md }}
            >
              {progressData.days_remaining > 0
                ? `${progressData.days_remaining} days remaining`
                : "Target date has passed"}
            </p>
          )}

          {/* Individual Item Progress */}
          {progressData.item_progress &&
            progressData.item_progress.length > 0 && (
              <div style={{ marginTop: spacing.lg }}>
                <H3 style={{ marginBottom: spacing.md }}>Item Progress</H3>
                {progressData.item_progress.map((itemProgress) => {
                  const goalItem = goal.goal_items.find(
                    (gi) => gi.item_id === itemProgress.item_id
                  );
                  const itemName =
                    goalItem?.item?.name ||
                    `Item ${itemProgress.item_id.slice(0, 8)}`;

                  return (
                    <Card
                      key={itemProgress.item_id}
                      style={{ marginBottom: spacing.md }}
                    >
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          marginBottom: spacing.sm,
                        }}
                      >
                        <div>
                          <strong>{itemName}</strong>
                          {itemProgress.is_completed && (
                            <Tag
                              intent={Intent.SUCCESS}
                              style={{ marginLeft: spacing.sm }}
                            >
                              Complete
                            </Tag>
                          )}
                        </div>
                        <span style={{ color: colors.text.secondary }}>
                          {itemProgress.progress_percentage.toFixed(1)}%
                        </span>
                      </div>
                      <ProgressBar
                        value={itemProgress.progress_percentage / 100}
                        intent={
                          itemProgress.is_completed
                            ? Intent.SUCCESS
                            : itemProgress.progress_percentage >= 50
                            ? Intent.PRIMARY
                            : Intent.WARNING
                        }
                        animate={goal.status === "active"}
                      />
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          marginTop: spacing.xs,
                          fontSize: "0.9em",
                          color: colors.text.secondary,
                        }}
                      >
                        <span>
                          {itemProgress.current_quantity.toFixed(2)} /{" "}
                          {itemProgress.target_quantity.toFixed(2)}
                        </span>
                      </div>
                    </Card>
                  );
                })}
              </div>
            )}
        </div>

        <Divider />

        <div style={{ marginTop: spacing.md }}>
          <H3>Details</H3>
          <dl style={{ marginTop: spacing.md }}>
            <dt style={{ fontWeight: "bold", marginBottom: spacing.xs }}>
              Goal Items:
            </dt>
            <dd style={{ marginBottom: spacing.md, marginLeft: 0 }}>
              {goal.goal_items.length === 0 ? (
                "No items"
              ) : (
                <ul style={{ margin: 0, paddingLeft: spacing.lg }}>
                  {goal.goal_items.map((item) => (
                    <li key={item.id}>
                      {item.item?.name || `Item ${item.item_id.slice(0, 8)}`}:{" "}
                      {item.target_quantity.toFixed(2)}
                    </li>
                  ))}
                </ul>
              )}
            </dd>

            <dt style={{ fontWeight: "bold", marginBottom: spacing.xs }}>
              Target Date:
            </dt>
            <dd style={{ marginBottom: spacing.md, marginLeft: 0 }}>
              {formatDate(goal.target_date)}
            </dd>

            <dt style={{ fontWeight: "bold", marginBottom: spacing.xs }}>
              Created:
            </dt>
            <dd style={{ marginBottom: spacing.md, marginLeft: 0 }}>
              {formatDate(goal.created_at)}
            </dd>

            <dt style={{ fontWeight: "bold", marginBottom: spacing.xs }}>
              Last Updated:
            </dt>
            <dd style={{ marginBottom: spacing.md, marginLeft: 0 }}>
              {formatDate(goal.updated_at)}
            </dd>
          </dl>
        </div>
      </Card>
    </DashboardLayout>
  );
}
