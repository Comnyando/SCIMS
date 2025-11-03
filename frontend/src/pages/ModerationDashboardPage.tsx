/**
 * Moderation Dashboard page component using Blueprint.js.
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
import { useSubmissions } from "../hooks/queries/commons";
import DataTable from "../components/common/DataTable";
import Pagination from "../components/common/Pagination";
import { pageHeader, filterRow } from "../styles/common";
import { spacing } from "../styles/theme";
import type {
  CommonsSubmissionResponse,
  SubmissionStatus,
} from "../types/commons";

const STATUS_COLORS: Record<SubmissionStatus, Intent> = {
  pending: Intent.WARNING,
  approved: Intent.SUCCESS,
  rejected: Intent.DANGER,
  needs_changes: Intent.PRIMARY,
  merged: Intent.NONE,
};

const ENTITY_TYPE_OPTIONS = [
  { value: "", label: "All Types" },
  { value: "item", label: "Items" },
  { value: "blueprint", label: "Blueprints" },
  { value: "location", label: "Locations" },
  { value: "ingredient", label: "Ingredients" },
  { value: "taxonomy", label: "Taxonomy" },
];

const STATUS_OPTIONS = [
  { value: "", label: "All Statuses" },
  { value: "pending", label: "Pending" },
  { value: "needs_changes", label: "Needs Changes" },
  { value: "approved", label: "Approved" },
  { value: "rejected", label: "Rejected" },
  { value: "merged", label: "Merged" },
];

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString();
}

function formatEntityPayload(payload: Record<string, unknown>): string {
  const name = payload.name || payload.title || "Unknown";
  return String(name);
}

export default function ModerationDashboardPage() {
  const navigate = useNavigate();
  const [skip, setSkip] = useState(0);
  const [limit] = useState(50);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [entityTypeFilter, setEntityTypeFilter] = useState<string>("");

  const { data, isLoading, error } = useSubmissions({
    skip,
    limit,
    status: statusFilter || undefined,
    entity_type: entityTypeFilter || undefined,
  });

  const handleStatusChange = (value: string) => {
    setStatusFilter(value);
    setSkip(0);
  };

  const handleEntityTypeChange = (value: string) => {
    setEntityTypeFilter(value);
    setSkip(0);
  };

  const handleSubmissionClick = (submission: CommonsSubmissionResponse) => {
    navigate(`/admin/commons/submissions/${submission.id}`);
  };

  const handlePageChange = (newSkip: number) => {
    setSkip(newSkip);
    window.scrollTo({ top: 0, behavior: "smooth" });
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

  if (error) {
    return (
      <DashboardLayout>
        <Callout intent={Intent.DANGER}>
          Error loading submissions:{" "}
          {error instanceof Error ? error.message : "Unknown error"}
        </Callout>
      </DashboardLayout>
    );
  }

  const columns = [
    {
      key: "entity_type",
      label: "Type",
      render: (submission: CommonsSubmissionResponse) => (
        <Tag intent={Intent.NONE}>{submission.entity_type}</Tag>
      ),
    },
    {
      key: "name",
      label: "Name",
      render: (submission: CommonsSubmissionResponse) =>
        formatEntityPayload(submission.entity_payload),
    },
    {
      key: "status",
      label: "Status",
      render: (submission: CommonsSubmissionResponse) => (
        <Tag intent={STATUS_COLORS[submission.status]}>
          {submission.status.replace("_", " ").toUpperCase()}
        </Tag>
      ),
    },
    {
      key: "created_at",
      label: "Submitted",
      render: (submission: CommonsSubmissionResponse) =>
        formatDate(submission.created_at),
    },
    {
      key: "actions",
      label: "Actions",
      render: (submission: CommonsSubmissionResponse) => (
        <Button
          small
          text="View"
          onClick={() => handleSubmissionClick(submission)}
          intent={Intent.PRIMARY}
        />
      ),
    },
  ];

  const totalPages = data?.pages || 0;
  const currentPage = Math.floor(skip / limit) + 1;
  const hasPrevious = skip > 0;
  const hasNext = skip + limit < (data?.total || 0);

  return (
    <DashboardLayout>
      <H1 style={pageHeader}>Moderation Dashboard</H1>

      <div style={filterRow}>
        <div style={{ display: "flex", gap: spacing.md, alignItems: "center" }}>
          <label style={{ minWidth: "100px" }}>Status:</label>
          <HTMLSelect
            value={statusFilter}
            onChange={(e) => handleStatusChange(e.target.value)}
            options={STATUS_OPTIONS.map((opt) => ({
              value: opt.value,
              label: opt.label,
            }))}
          />
        </div>

        <div style={{ display: "flex", gap: spacing.md, alignItems: "center" }}>
          <label style={{ minWidth: "100px" }}>Entity Type:</label>
          <HTMLSelect
            value={entityTypeFilter}
            onChange={(e) => handleEntityTypeChange(e.target.value)}
            options={ENTITY_TYPE_OPTIONS.map((opt) => ({
              value: opt.value,
              label: opt.label,
            }))}
          />
        </div>

        <div style={{ marginLeft: "auto" }}>
          <Tag>Total: {data?.total || 0}</Tag>
        </div>
      </div>

      {data && data.submissions.length > 0 ? (
        <>
          <DataTable
            data={data.submissions}
            columns={columns}
            keyExtractor={(submission) => submission.id}
          />
          {totalPages > 1 && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPrevious={() => handlePageChange(Math.max(0, skip - limit))}
              onNext={() => handlePageChange(skip + limit)}
              hasPrevious={hasPrevious}
              hasNext={hasNext}
            />
          )}
        </>
      ) : (
        <Callout intent={Intent.NONE} style={{ marginTop: spacing.lg }}>
          No submissions found.
        </Callout>
      )}
    </DashboardLayout>
  );
}
