/**
 * Integration creation/edit form page component using Blueprint.js.
 */

import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  H1,
  Callout,
  Intent,
  Spinner,
  Button,
  FormGroup,
  InputGroup,
  HTMLSelect,
  Card,
  TextArea,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import {
  useCreateIntegration,
  useUpdateIntegration,
  useIntegration,
} from "../hooks/queries/integrations";
import { pageHeader } from "../styles/common";
import { spacing } from "../styles/theme";
import type {
  IntegrationCreate,
  IntegrationUpdate,
  IntegrationStatus,
} from "../types/integration";

export default function IntegrationFormPage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEdit = !!id;

  const { data: existingIntegration, isLoading: isLoadingIntegration } =
    useIntegration(id);
  const createIntegration = useCreateIntegration();
  const updateIntegration = useUpdateIntegration();

  const [name, setName] = useState("");
  const [type, setType] = useState<string>("webhook");
  const [status, setStatus] = useState<IntegrationStatus>("active");
  const [webhookUrl, setWebhookUrl] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [apiSecret, setApiSecret] = useState("");
  const [configData, setConfigData] = useState("");
  const [configDataError, setConfigDataError] = useState<string | null>(null);

  // Load existing integration data when editing
  useEffect(() => {
    if (existingIntegration) {
      setName(existingIntegration.name);
      setType(existingIntegration.type);
      setStatus(existingIntegration.status);
      setWebhookUrl(existingIntegration.webhook_url || "");
      setConfigData(
        existingIntegration.config_data
          ? JSON.stringify(existingIntegration.config_data, null, 2)
          : ""
      );
      // Note: API keys/secrets are not returned for security reasons
    }
  }, [existingIntegration]);

  const handleConfigDataChange = (value: string) => {
    setConfigData(value);
    setConfigDataError(null);
    if (value.trim()) {
      try {
        JSON.parse(value);
      } catch (e) {
        setConfigDataError("Invalid JSON format");
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name || !type) {
      return;
    }

    let parsedConfigData: Record<string, unknown> | null = null;
    if (configData.trim()) {
      try {
        parsedConfigData = JSON.parse(configData);
      } catch (e) {
        setConfigDataError("Invalid JSON format");
        return;
      }
    }

    try {
      if (isEdit && id) {
        const updateData: IntegrationUpdate = {
          name,
          status,
          webhook_url: webhookUrl || null,
          config_data: parsedConfigData,
        };
        // Only include API key/secret if provided (for updates, empty string clears them)
        if (apiKey !== "") {
          updateData.api_key = apiKey || null;
        }
        if (apiSecret !== "") {
          updateData.api_secret = apiSecret || null;
        }
        await updateIntegration.mutateAsync({ id, data: updateData });
      } else {
        const createData: IntegrationCreate = {
          name,
          type: type as "webhook" | "api",
          webhook_url: webhookUrl || null,
          api_key: apiKey || null,
          api_secret: apiSecret || null,
          config_data: parsedConfigData,
        };
        await createIntegration.mutateAsync(createData);
      }
      navigate("/integrations");
    } catch (error) {
      console.error("Failed to save integration:", error);
    }
  };

  if (isLoadingIntegration) {
    return (
      <DashboardLayout>
        <div style={{ textAlign: "center", padding: spacing.xl }}>
          <Spinner size={50} />
        </div>
      </DashboardLayout>
    );
  }

  const isSubmitting =
    createIntegration.isPending || updateIntegration.isPending;

  return (
    <DashboardLayout>
      <H1 style={pageHeader}>
        {isEdit ? "Edit Integration" : "Create Integration"}
      </H1>

      <Card style={{ maxWidth: "800px", marginTop: spacing.lg }}>
        <form onSubmit={handleSubmit}>
          <FormGroup label="Name" labelInfo="(required)">
            <InputGroup
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Integration Name"
              required
            />
          </FormGroup>

          <FormGroup label="Type" labelInfo="(required)">
            <HTMLSelect
              value={type}
              onChange={(e) => setType(e.target.value)}
              disabled={isEdit}
            >
              <option value="webhook">Webhook</option>
              <option value="api">API</option>
            </HTMLSelect>
          </FormGroup>

          {isEdit && (
            <FormGroup label="Status">
              <HTMLSelect
                value={status}
                onChange={(e) => setStatus(e.target.value as IntegrationStatus)}
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="error">Error</option>
              </HTMLSelect>
            </FormGroup>
          )}

          {type === "webhook" && (
            <FormGroup label="Webhook URL">
              <InputGroup
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
                placeholder="https://example.com/webhook"
                type="url"
              />
            </FormGroup>
          )}

          {type === "api" && (
            <>
              <FormGroup label="API Key">
                <InputGroup
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder={
                    isEdit
                      ? "Leave empty to keep existing, enter new value to update"
                      : "API Key"
                  }
                  type="password"
                />
              </FormGroup>
              <FormGroup label="API Secret">
                <InputGroup
                  value={apiSecret}
                  onChange={(e) => setApiSecret(e.target.value)}
                  placeholder={
                    isEdit
                      ? "Leave empty to keep existing, enter new value to update"
                      : "API Secret"
                  }
                  type="password"
                />
              </FormGroup>
            </>
          )}

          <FormGroup
            label="Configuration Data"
            helperText="Additional configuration as JSON (optional)"
          >
            <TextArea
              value={configData}
              onChange={(e) => handleConfigDataChange(e.target.value)}
              placeholder='{"key": "value"}'
              rows={6}
              style={{ fontFamily: "monospace" }}
            />
            {configDataError && (
              <Callout intent={Intent.DANGER} style={{ marginTop: spacing.sm }}>
                {configDataError}
              </Callout>
            )}
          </FormGroup>

          <div
            style={{
              display: "flex",
              gap: spacing.md,
              marginTop: spacing.lg,
            }}
          >
            <Button
              type="submit"
              intent={Intent.PRIMARY}
              loading={isSubmitting}
              text={isEdit ? "Update Integration" : "Create Integration"}
            />
            <Button
              text="Cancel"
              onClick={() => navigate("/integrations")}
              disabled={isSubmitting}
            />
          </div>

          {(createIntegration.isError || updateIntegration.isError) && (
            <Callout intent={Intent.DANGER} style={{ marginTop: spacing.md }}>
              Failed to save integration:{" "}
              {createIntegration.error instanceof Error
                ? createIntegration.error.message
                : updateIntegration.error instanceof Error
                ? updateIntegration.error.message
                : "Unknown error"}
            </Callout>
          )}
        </form>
      </Card>
    </DashboardLayout>
  );
}
