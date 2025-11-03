/**
 * Integrations page component using Blueprint.js.
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
import { useIntegrations } from "../hooks/queries/integrations";
import DataTable from "../components/common/DataTable";
import Pagination from "../components/common/Pagination";
import { pageHeader, filterRow, sectionSpacing } from "../styles/common";
import { spacing } from "../styles/theme";
import type { Integration, IntegrationStatus } from "../types/integration";

const STATUS_COLORS: Record<IntegrationStatus, Intent> = {
  active: Intent.SUCCESS,
  inactive: Intent.WARNING,
  error: Intent.DANGER,
};

function formatDate(dateString: string | null): string {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date.toLocaleString();
}

export default function IntegrationsPage() {
  const navigate = useNavigate();
  const [skip, setSkip] = useState(0);
  const [limit] = useState(50);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [typeFilter, setTypeFilter] = useState<string>("");

  const { data, isLoading, error } = useIntegrations({
    skip,
    limit,
    status_filter: statusFilter || undefined,
    type_filter: typeFilter || undefined,
  });

  const handleStatusChange = (value: string) => {
    setStatusFilter(value);
    setSkip(0);
  };

  const handleTypeChange = (value: string) => {
    setTypeFilter(value);
    setSkip(0);
  };

  const handleIntegrationClick = (integration: Integration) => {
    navigate(`/integrations/${integration.id}`);
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
        <Callout intent={Intent.DANGER} style={sectionSpacing}>
          Error loading integrations:{" "}
          {error instanceof Error ? error.message : "Unknown error"}
        </Callout>
      </DashboardLayout>
    );
  }

  const columns = [
    {
      key: "name",
      label: "Name",
      render: (integration: Integration) => (
        <span
          style={{ cursor: "pointer", textDecoration: "underline" }}
          onClick={() => handleIntegrationClick(integration)}
        >
          {integration.name}
        </span>
      ),
    },
    {
      key: "type",
      label: "Type",
      render: (integration: Integration) => <Tag>{integration.type}</Tag>,
    },
    {
      key: "status",
      label: "Status",
      render: (integration: Integration) => (
        <Tag intent={STATUS_COLORS[integration.status as IntegrationStatus]}>
          {integration.status}
        </Tag>
      ),
    },
    {
      key: "webhook_url",
      label: "Webhook URL",
      render: (integration: Integration) =>
        integration.webhook_url ? (
          <span style={{ fontFamily: "monospace", fontSize: "0.9em" }}>
            {integration.webhook_url.length > 50
              ? `${integration.webhook_url.substring(0, 50)}...`
              : integration.webhook_url}
          </span>
        ) : (
          "-"
        ),
    },
    {
      key: "last_tested_at",
      label: "Last Tested",
      render: (integration: Integration) =>
        formatDate(integration.last_tested_at),
    },
    {
      key: "created_at",
      label: "Created",
      render: (integration: Integration) => formatDate(integration.created_at),
    },
  ];

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
        <H1 style={pageHeader}>Integrations</H1>
        <Button
          icon="plus"
          text="Create Integration"
          intent={Intent.PRIMARY}
          onClick={() => navigate("/integrations/new")}
        />
      </div>

      <div style={filterRow}>
        <HTMLSelect
          value={statusFilter}
          onChange={(e) => handleStatusChange(e.target.value)}
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="error">Error</option>
        </HTMLSelect>

        <HTMLSelect
          value={typeFilter}
          onChange={(e) => handleTypeChange(e.target.value)}
        >
          <option value="">All Types</option>
          <option value="webhook">Webhook</option>
          <option value="api">API</option>
        </HTMLSelect>
      </div>

      {data && data.items.length === 0 ? (
        <Callout intent={Intent.PRIMARY} style={sectionSpacing}>
          No integrations found. Create your first integration to get started.
        </Callout>
      ) : (
        <>
          <DataTable
            columns={columns}
            data={data?.items || []}
            keyExtractor={(integration) => integration.id}
          />
          {data && data.total > limit && (
            <Pagination
              currentPage={Math.floor(skip / limit) + 1}
              totalPages={Math.ceil((data.total || 0) / limit)}
              onPrevious={() => setSkip(Math.max(0, skip - limit))}
              onNext={() => setSkip(skip + limit)}
              hasPrevious={skip > 0}
              hasNext={skip + limit < (data.total || 0)}
            />
          )}
        </>
      )}
    </DashboardLayout>
  );
}
