/**
 * Goals page component using Blueprint.js.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  H1,
  Callout,
  Intent,
  Spinner,
  HTMLSelect,
  Button,
  Tag,
  ProgressBar,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import { useGoals } from "../hooks/queries/goals";
import DataTable from "../components/common/DataTable";
import Pagination from "../components/common/Pagination";
import { pageHeader, filterRow, sectionSpacing } from "../styles/common";
import { spacing, colors } from "../styles/theme";
import type { Goal, GoalStatus } from "../types/goal";

const STATUS_COLORS: Record<GoalStatus, Intent> = {
  active: Intent.PRIMARY,
  completed: Intent.SUCCESS,
  cancelled: Intent.DANGER,
};

function formatDate(dateString: string | null): string {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date.toLocaleString();
}

function getProgressFromData(goal: Goal): number {
  if (
    goal.progress_data &&
    typeof goal.progress_data.progress_percentage === "number"
  ) {
    return goal.progress_data.progress_percentage;
  }
  return 0;
}

export default function GoalsPage() {
  const navigate = useNavigate();
  const [skip, setSkip] = useState(0);
  const [limit] = useState(50);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [sortBy, setSortBy] = useState<string>("created_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const { data, isLoading, error } = useGoals({
    skip,
    limit,
    status_filter: statusFilter || undefined,
    sort_by: sortBy,
    sort_order: sortOrder,
  });

  const handleStatusChange = (value: string) => {
    setStatusFilter(value);
    setSkip(0);
  };

  const handleSortChange = (value: string) => {
    setSortBy(value);
    setSkip(0);
  };

  const handleSortOrderChange = (value: string) => {
    setSortOrder(value as "asc" | "desc");
    setSkip(0);
  };

  const handleGoalClick = (goal: Goal) => {
    navigate(`/goals/${goal.id}`);
  };

  const columns = [
    {
      key: "name",
      label: "Goal",
      render: (goal: Goal) => (
        <strong
          style={{ cursor: "pointer" }}
          onClick={() => handleGoalClick(goal)}
        >
          {goal.name}
        </strong>
      ),
    },
    {
      key: "status",
      label: "Status",
      render: (goal: Goal) => (
        <Tag intent={STATUS_COLORS[goal.status]}>
          {goal.status.toUpperCase()}
        </Tag>
      ),
    },
    {
      key: "target",
      label: "Target",
      render: (goal: Goal) => {
        if (goal.goal_items.length === 0) {
          return "No items";
        }
        if (goal.goal_items.length === 1) {
          const item = goal.goal_items[0];
          return `${item.item?.name || "Item"}: ${item.target_quantity.toFixed(
            2
          )}`;
        }
        return `${goal.goal_items.length} items (${goal.goal_items
          .reduce((sum, item) => sum + item.target_quantity, 0)
          .toFixed(2)} total)`;
      },
    },
    {
      key: "progress",
      label: "Progress",
      render: (goal: Goal) => {
        const progress = getProgressFromData(goal);
        return (
          <div style={{ minWidth: 150 }}>
            <ProgressBar
              value={progress / 100}
              intent={
                progress >= 100
                  ? Intent.SUCCESS
                  : progress >= 50
                  ? Intent.PRIMARY
                  : Intent.WARNING
              }
              animate={goal.status === "active"}
            />
            <span style={{ fontSize: "0.85em", color: colors.text.secondary }}>
              {progress.toFixed(1)}%
            </span>
          </div>
        );
      },
    },
    {
      key: "target_date",
      label: "Target Date",
      render: (goal: Goal) => formatDate(goal.target_date),
    },
    {
      key: "created_at",
      label: "Created",
      render: (goal: Goal) => formatDate(goal.created_at),
    },
  ];

  const currentPage = Math.floor(skip / limit) + 1;
  const totalPages = data ? Math.ceil(data.total / limit) : 1;

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
        <H1 style={pageHeader}>Goals</H1>
        <Button
          icon="plus"
          text="Create Goal"
          intent="primary"
          onClick={() => navigate("/goals/new")}
        />
      </div>

      {error && (
        <Callout intent={Intent.DANGER} style={sectionSpacing}>
          Error loading goals:{" "}
          {error instanceof Error ? error.message : "Unknown error"}
        </Callout>
      )}

      <div style={filterRow}>
        <HTMLSelect
          value={statusFilter}
          onChange={(e) => handleStatusChange(e.target.value)}
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </HTMLSelect>
        <HTMLSelect
          value={sortBy}
          onChange={(e) => handleSortChange(e.target.value)}
          style={{ marginLeft: spacing.md }}
        >
          <option value="created_at">Sort by Created</option>
          <option value="target_date">Sort by Target Date</option>
          <option value="name">Sort by Name</option>
        </HTMLSelect>
        <HTMLSelect
          value={sortOrder}
          onChange={(e) => handleSortOrderChange(e.target.value)}
          style={{ marginLeft: spacing.sm }}
        >
          <option value="desc">Descending</option>
          <option value="asc">Ascending</option>
        </HTMLSelect>
      </div>

      {isLoading ? (
        <div style={{ textAlign: "center", padding: spacing.xl }}>
          <Spinner size={50} />
        </div>
      ) : data && data.items.length > 0 ? (
        <>
          <p style={{ color: colors.text.secondary, marginBottom: spacing.md }}>
            Showing {data.items.length} of {data.total} goals
          </p>
          <DataTable
            columns={columns}
            data={data.items}
            emptyMessage="No goals found"
            keyExtractor={(goal) => goal.id}
          />
          {totalPages > 1 && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPrevious={() => setSkip(Math.max(0, skip - limit))}
              onNext={() => setSkip(skip + limit)}
              hasPrevious={skip > 0}
              hasNext={skip + limit < (data?.total || 0)}
            />
          )}
        </>
      ) : (
        <Callout intent={Intent.WARNING} style={sectionSpacing}>
          No goals found.{" "}
          {statusFilter
            ? "Try adjusting your filters."
            : "Create your first goal!"}
        </Callout>
      )}
    </DashboardLayout>
  );
}
