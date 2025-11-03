/**
 * Integration detail page component using Blueprint.js.
 */

import { useNavigate, useParams } from "react-router-dom";
import { useState } from "react";
import {
  H1,
  H3,
  Callout,
  Intent,
  Spinner,
  Button,
  Tag,
  Card,
  Pre,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import {
  useIntegration,
  useIntegrationLogs,
  useDeleteIntegration,
  useTestIntegration,
} from "../hooks/queries/integrations";
import DataTable from "../components/common/DataTable";
import Pagination from "../components/common/Pagination";
import { pageHeader, sectionSpacing } from "../styles/common";
import { spacing } from "../styles/theme";
import type {
  IntegrationStatus,
  IntegrationLogStatus,
  IntegrationLog,
} from "../types/integration";

const STATUS_COLORS: Record<IntegrationStatus, Intent> = {
  active: Intent.SUCCESS,
  inactive: Intent.WARNING,
  error: Intent.DANGER,
};

const LOG_STATUS_COLORS: Record<IntegrationLogStatus, Intent> = {
  success: Intent.SUCCESS,
  error: Intent.DANGER,
  pending: Intent.WARNING,
};

function formatDate(dateString: string | null): string {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date.toLocaleString();
}

export default function IntegrationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [logSkip, setLogSkip] = useState(0);
  const [logLimit] = useState(20);

  const { data: integration, isLoading, error } = useIntegration(id);
  const { data: logsData, isLoading: isLoadingLogs } = useIntegrationLogs(id, {
    skip: logSkip,
    limit: logLimit,
  });
  const deleteIntegration = useDeleteIntegration();
  const testIntegration = useTestIntegration();

  const handleDelete = async () => {
    if (
      !id ||
      !window.confirm("Are you sure you want to delete this integration?")
    ) {
      return;
    }

    try {
      await deleteIntegration.mutateAsync(id);
      navigate("/integrations");
    } catch (error) {
      console.error("Failed to delete integration:", error);
    }
  };

  const handleTest = async () => {
    if (!id) return;
    try {
      await testIntegration.mutateAsync(id);
      // Test result will be shown via the mutation state
    } catch (error) {
      console.error("Failed to test integration:", error);
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

  if (error || !integration) {
    return (
      <DashboardLayout>
        <Callout intent={Intent.DANGER} style={sectionSpacing}>
          {error instanceof Error ? error.message : "Integration not found"}
        </Callout>
        <Button
          icon="arrow-left"
          text="Back to Integrations"
          onClick={() => navigate("/integrations")}
        />
      </DashboardLayout>
    );
  }

  const logColumns = [
    {
      key: "timestamp",
      label: "Timestamp",
      render: (log: IntegrationLog) => formatDate(log.timestamp),
    },
    {
      key: "event_type",
      label: "Event Type",
      render: (log: IntegrationLog) => <Tag>{log.event_type}</Tag>,
    },
    {
      key: "status",
      label: "Status",
      render: (log: IntegrationLog) => (
        <Tag intent={LOG_STATUS_COLORS[log.status]}>{log.status}</Tag>
      ),
    },
    {
      key: "execution_time_ms",
      label: "Execution Time",
      render: (log: IntegrationLog) =>
        log.execution_time_ms ? `${log.execution_time_ms}ms` : "-",
    },
    {
      key: "error_message",
      label: "Error",
      render: (log: IntegrationLog) => log.error_message || "-",
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
        <H1 style={pageHeader}>{integration.name}</H1>
        <div style={{ display: "flex", gap: spacing.sm }}>
          <Button
            icon="play"
            text="Test Integration"
            intent={Intent.PRIMARY}
            onClick={handleTest}
            loading={testIntegration.isPending}
          />
          <Button
            icon="edit"
            text="Edit"
            onClick={() => navigate(`/integrations/${integration.id}/edit`)}
          />
          <Button
            icon="trash"
            text="Delete"
            intent={Intent.DANGER}
            onClick={handleDelete}
            loading={deleteIntegration.isPending}
          />
        </div>
      </div>

      {testIntegration.isSuccess && (
        <Callout intent={Intent.SUCCESS} style={{ marginBottom: spacing.md }}>
          Test Result: {testIntegration.data.message}
        </Callout>
      )}

      {testIntegration.isError && (
        <Callout intent={Intent.DANGER} style={{ marginBottom: spacing.md }}>
          Test Failed:{" "}
          {testIntegration.error instanceof Error
            ? testIntegration.error.message
            : "Unknown error"}
        </Callout>
      )}

      {/* Integration Details */}
      <Card style={{ marginBottom: spacing.lg }}>
        <H3 style={{ marginTop: 0 }}>Details</H3>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "200px 1fr",
            gap: spacing.md,
          }}
        >
          <strong>Status:</strong>
          <Tag intent={STATUS_COLORS[integration.status as IntegrationStatus]}>
            {integration.status}
          </Tag>

          <strong>Type:</strong>
          <Tag>{integration.type}</Tag>

          <strong>Webhook URL:</strong>
          <span style={{ fontFamily: "monospace", wordBreak: "break-all" }}>
            {integration.webhook_url || "-"}
          </span>

          <strong>Last Tested:</strong>
          <span>{formatDate(integration.last_tested_at)}</span>

          <strong>Last Error:</strong>
          <span>{integration.last_error || "-"}</span>

          <strong>Created:</strong>
          <span>{formatDate(integration.created_at)}</span>

          <strong>Updated:</strong>
          <span>{formatDate(integration.updated_at)}</span>

          {integration.config_data && (
            <>
              <strong>Configuration:</strong>
              <Pre
                style={{
                  fontSize: "0.9em",
                  margin: 0,
                  maxHeight: "200px",
                  overflow: "auto",
                }}
              >
                {JSON.stringify(integration.config_data, null, 2)}
              </Pre>
            </>
          )}
        </div>
      </Card>

      {/* Integration Logs */}
      <Card>
        <H3 style={{ marginTop: 0 }}>Logs</H3>
        {isLoadingLogs ? (
          <Spinner size={20} />
        ) : logsData && logsData.logs.length === 0 ? (
          <Callout intent={Intent.PRIMARY}>
            No logs found for this integration.
          </Callout>
        ) : (
          <>
            <DataTable
              columns={logColumns}
              data={logsData?.logs || []}
              keyExtractor={(log) => log.id}
            />
            {logsData && logsData.total > logLimit && (
              <Pagination
                currentPage={Math.floor(logSkip / logLimit) + 1}
                totalPages={Math.ceil(logsData.total / logLimit)}
                onPrevious={() => setLogSkip(Math.max(0, logSkip - logLimit))}
                onNext={() => setLogSkip(logSkip + logLimit)}
                hasPrevious={logSkip > 0}
                hasNext={logSkip + logLimit < logsData.total}
              />
            )}
          </>
        )}
      </Card>
    </DashboardLayout>
  );
}
