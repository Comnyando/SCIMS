/**
 * Crafts queue page component using Blueprint.js.
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
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import { useCrafts } from "../hooks/queries/crafts";
import DataTable from "../components/common/DataTable";
import Pagination from "../components/common/Pagination";
import { pageHeader, filterRow, sectionSpacing } from "../styles/common";
import { spacing, colors } from "../styles/theme";
import type { Craft, CraftStatus } from "../types";

const STATUS_COLORS: Record<CraftStatus, Intent> = {
  planned: Intent.NONE,
  in_progress: Intent.PRIMARY,
  completed: Intent.SUCCESS,
  cancelled: Intent.DANGER,
};

function formatDate(dateString: string | null): string {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date.toLocaleString();
}

export default function CraftsPage() {
  const navigate = useNavigate();
  const [skip, setSkip] = useState(0);
  const [limit] = useState(50);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [sortBy, setSortBy] = useState<string>("created_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const { data, isLoading, error } = useCrafts({
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

  const handleCraftClick = (craft: Craft) => {
    navigate(`/crafts/${craft.id}`);
  };

  const columns = [
    {
      key: "blueprint",
      label: "Blueprint",
      render: (craft: Craft) => (
        <strong
          style={{ cursor: "pointer" }}
          onClick={() => handleCraftClick(craft)}
        >
          {craft.blueprint?.name || "Unknown"}
        </strong>
      ),
    },
    {
      key: "status",
      label: "Status",
      render: (craft: Craft) => (
        <Tag intent={STATUS_COLORS[craft.status]}>
          {craft.status.replace("_", " ").toUpperCase()}
        </Tag>
      ),
    },
    {
      key: "priority",
      label: "Priority",
      render: (craft: Craft) => craft.priority,
      align: "center" as const,
    },
    {
      key: "started_at",
      label: "Started",
      render: (craft: Craft) => formatDate(craft.started_at),
    },
    {
      key: "progress",
      label: "Progress",
      render: (craft: Craft) => {
        if (
          craft.status === "in_progress" &&
          craft.started_at &&
          craft.blueprint
        ) {
          const started = new Date(craft.started_at);
          const now = new Date();
          const elapsed = Math.floor(
            (now.getTime() - started.getTime()) / 60000
          );
          const total = craft.blueprint.crafting_time_minutes;
          const percent = Math.min(100, Math.round((elapsed / total) * 100));
          return `${percent}%`;
        }
        return craft.status === "completed" ? "100%" : "-";
      },
      align: "center" as const,
    },
    {
      key: "scheduled_start",
      label: "Scheduled",
      render: (craft: Craft) => formatDate(craft.scheduled_start),
    },
    {
      key: "completed_at",
      label: "Completed",
      render: (craft: Craft) => formatDate(craft.completed_at),
    },
    {
      key: "output_location",
      label: "Output Location",
      render: (craft: Craft) => craft.output_location?.name || "-",
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
        <H1 style={pageHeader} data-tour="crafts-page-header">
          Craft Queue
        </H1>
        <Button
          icon="plus"
          text="Create Craft"
          intent="primary"
          data-tour="create-craft-button"
          onClick={() => navigate("/crafts/new")}
        />
      </div>

      {error && (
        <Callout intent={Intent.DANGER} style={sectionSpacing}>
          Error loading crafts:{" "}
          {error instanceof Error ? error.message : "Unknown error"}
        </Callout>
      )}

      <div style={filterRow}>
        <HTMLSelect
          value={statusFilter}
          onChange={(e) => handleStatusChange(e.target.value)}
          data-tour="craft-status-filter"
        >
          <option value="">All Statuses</option>
          <option value="planned">Planned</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </HTMLSelect>
        <HTMLSelect
          value={sortBy}
          onChange={(e) => handleSortChange(e.target.value)}
          style={{ marginLeft: spacing.md }}
          data-tour="craft-sort"
        >
          <option value="created_at">Sort by Created</option>
          <option value="priority">Sort by Priority</option>
          <option value="started_at">Sort by Started</option>
          <option value="scheduled_start">Sort by Scheduled</option>
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
            Showing {data.items.length} of {data.total} crafts
          </p>
          <div data-tour="craft-list">
            <DataTable
              columns={columns}
              data={data.items}
              emptyMessage="No crafts found"
              keyExtractor={(craft) => craft.id}
            />
          </div>
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
          No crafts found.{" "}
          {statusFilter
            ? "Try adjusting your filters."
            : "Create your first craft!"}
        </Callout>
      )}
    </DashboardLayout>
  );
}
